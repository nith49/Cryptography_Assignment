"""
Shared data handling for UPI Payment Gateway System
This module provides functions for sharing data between distributed components
"""

import os
import json
import shutil
import socket
import time
import threading

# Define shared data directory
SHARED_DATA_DIR = 'shared_data'

def setup_shared_data():
    """Ensure shared data directory exists"""
    if not os.path.exists(SHARED_DATA_DIR):
        os.makedirs(SHARED_DATA_DIR)

def save_shared_data(file_name, data):
    """Save data to shared directory"""
    setup_shared_data()
    file_path = os.path.join(SHARED_DATA_DIR, file_name)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving shared data: {e}")
        return False

def load_shared_data(file_name):
    """Load data from shared directory"""
    setup_shared_data()
    file_path = os.path.join(SHARED_DATA_DIR, file_name)
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading shared data: {e}")
        return None

class DataSyncServer:
    """Server for syncing data between components"""
    def __init__(self, port=5005):
        self.port = port
        self.running = False
        
        # Initialize server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        
        print(f"Data Sync Server started on port {self.port}")
    
    def start(self):
        """Start the data sync server"""
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def stop(self):
        """Stop the data sync server"""
        self.running = False
        self.server_socket.close()
    
    def _run_server(self):
        """Run the server loop"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Data sync connection from {addr}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except:
                if self.running:
                    print("Data sync server error, restarting...")
                    time.sleep(1)
    
    def _handle_client(self, client_socket):
        """Handle data sync client connection"""
        try:
            # Receive request
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            
            response = {"status": "error", "message": "Unknown request"}
            
            if request["action"] == "get_data":
                # Client is requesting data
                if "file_name" in request:
                    file_name = request["file_name"]
                    data = load_shared_data(file_name)
                    if data is not None:
                        response = {"status": "success", "data": data}
                    else:
                        response = {"status": "error", "message": f"File not found: {file_name}"}
            
            elif request["action"] == "save_data":
                # Client is sending data to save
                if "file_name" in request and "data" in request:
                    file_name = request["file_name"]
                    data = request["data"]
                    if save_shared_data(file_name, data):
                        response = {"status": "success", "message": f"Data saved: {file_name}"}
                    else:
                        response = {"status": "error", "message": f"Error saving data: {file_name}"}
            
            # Send response
            client_socket.sendall(json.dumps(response).encode())
        
        except Exception as e:
            print(f"Error handling data sync client: {e}")
            try:
                error_response = {"status": "error", "message": str(e)}
                client_socket.sendall(json.dumps(error_response).encode())
            except:
                pass
        finally:
            client_socket.close()

def sync_data_with_server(host, port, action, file_name, data=None):
    """Sync data with a remote server"""
    try:
        # Create request
        request = {
            "action": action,
            "file_name": file_name
        }
        
        if data is not None:
            request["data"] = data
        
        # Send request
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)  # 5 second timeout
            sock.connect((host, port))
            sock.sendall(json.dumps(request).encode())
            
            # Get response
            response = sock.recv(4096).decode()
            return json.loads(response)
    
    except Exception as e:
        print(f"Error syncing data with server: {e}")
        return {"status": "error", "message": str(e)}

def get_remote_data(host, port, file_name):
    """Get data from remote server"""
    response = sync_data_with_server(host, port, "get_data", file_name)
    if response["status"] == "success":
        return response["data"]
    return None

def save_remote_data(host, port, file_name, data):
    """Save data to remote server"""
    response = sync_data_with_server(host, port, "save_data", file_name, data)
    return response["status"] == "success"