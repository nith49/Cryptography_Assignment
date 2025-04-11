"""
UPI Machine Implementation for UPI Payment Gateway System
"""

import json
import socket
import threading
import time
import os
import sys
from datetime import datetime
import base64

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_utils import ( # type: ignore
    generate_qr_code, display_qr_code, SPECK,
    HOST, PORT_BANK, PORT_UPI_MACHINE, PORT_USER,
    send_message
)

class UPIMachine:
    """UPI Machine Implementation"""
    def __init__(self):
        # Initialize server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', PORT_UPI_MACHINE))
        self.server_socket.listen(5)
        
        print(f"UPI Machine started on {HOST}:{PORT_UPI_MACHINE}")
        
        # Create QR code directory if it doesn't exist
        self.qr_code_dir = "qr_codes"
        os.makedirs(self.qr_code_dir, exist_ok=True)
        print(f"QR codes will be stored in: {self.qr_code_dir}")
        
        # Start server thread
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Current transaction data
        self.current_transaction = None
    
    def generate_qr_code_for_merchant(self, mid):
        """Generate QR code for merchant ID"""
        # Send request to bank to generate VMID
        response = send_message(HOST, PORT_BANK, {
            "type": "generate_vmid",
            "mid": mid
        })
        
        if response["status"] != "success":
            return {"status": "error", "message": response["message"]}
        
        # Get VMID from response
        vmid = response["vmid"]
        
        # Generate QR code filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        qr_filename = f"{mid}_{timestamp}.png"
        qr_filepath = os.path.join(self.qr_code_dir, qr_filename)
        
        # Generate and display QR code
        qr_data = vmid
        print(f"Generating QR code for Merchant ID: {mid}")
        print(f"VMID: {vmid}")
        
        # First, generate and display the QR code using the existing function
        display_qr_code(qr_data)
        
        # Since display_qr_code doesn't accept a filepath parameter,
        # we need to handle saving to a custom path differently
        # Let's move the default 'qr_code.png' to our custom path
        if os.path.exists('qr_code.png'):
            os.makedirs(self.qr_code_dir, exist_ok=True)
            os.rename('qr_code.png', qr_filepath)
        
        return {
            "status": "success",
            "message": "QR code generated successfully",
            "vmid": vmid,
            "qr_data": qr_data,
            "qr_filepath": qr_filepath
        }
    
    def process_payment(self, payment_data):
        """Process payment from user"""
        required_fields = ["vmid", "mmid", "amount", "pin"]
        for field in required_fields:
            if field not in payment_data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Store current transaction
        self.current_transaction = payment_data
        
        # Decode VMID to get merchant ID
        vmid = payment_data["vmid"]
        
        # First, we need to determine which merchant this VMID belongs to
        # In a real system, this would involve querying the bank or using a different mechanism
        # For simplicity, we'll ask the bank to decode the VMID
        # This would normally require more secure handling
        
        # For demo purposes, we'll try to decode with merchant IDs from the bank
        merchant_list_response = send_message(HOST, PORT_BANK, {"type": "list_merchants"})
        
        if merchant_list_response["status"] != "success":
            return {"status": "error", "message": "Could not retrieve merchant list"}
        
        merchants = merchant_list_response["merchants"]
        decoded_mid = None
        
        # Try to decode VMID with each merchant ID
        for mid in merchants:
            decode_response = send_message(HOST, PORT_BANK, {
                "type": "decode_vmid",
                "vmid": vmid,
                "mid": mid
            })
            
            if decode_response["status"] == "success":
                decoded_mid = mid
                break
        
        if not decoded_mid:
            return {"status": "error", "message": "Could not decode VMID"}
        
        # Process transaction with bank
        transaction_data = {
            "mid": decoded_mid,
            "mmid": payment_data["mmid"],
            "amount": payment_data["amount"],
            "pin": payment_data["pin"]
        }
        
        # If quantum attack simulation is requested
        if "simulate_quantum_attack" in payment_data and payment_data["simulate_quantum_attack"]:
            transaction_data["simulate_quantum_attack"] = True
        
        transaction_response = send_message(HOST, PORT_BANK, {
            "type": "process_transaction",
            "data": transaction_data
        })
        
        # Clear current transaction
        self.current_transaction = None
        
        # Return transaction response
        return transaction_response
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            # Receive data from client
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            
            # Process request
            response = {"status": "error", "message": "Unknown request type"}
            
            if "type" in request:
                if request["type"] == "generate_qr":
                    response = self.generate_qr_code_for_merchant(request["mid"])
                elif request["type"] == "process_payment":
                    response = self.process_payment(request["payment_data"])
                elif request["type"] == "get_merchant_balance":
                    # Forward request to bank
                    response = send_message(HOST, PORT_BANK, {
                        "type": "get_merchant_balance",
                        "mid": request["mid"]
                    })
            
            # Send response
            client_socket.sendall(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error handling client: {e}")
            try:
                error_response = {"status": "error", "message": f"UPI Machine error: {str(e)}"}
                client_socket.sendall(json.dumps(error_response).encode())
            except:
                pass
        finally:
            client_socket.close()
    
    def start_server(self):
        """Start the UPI machine server"""
        print("UPI Machine Server is running. Waiting for connections...")
        try:
            while True:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"Connection from {addr}")
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.daemon = True
                    client_thread.start()
                except OSError as e:
                    if hasattr(e, 'winerror') and e.winerror == 10038:  # Socket operation on non-socket
                        print("Socket error detected. Recreating socket...")
                        # Recreate the socket
                        try:
                            self.server_socket.close()
                        except:
                            pass
                        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.server_socket.bind(('0.0.0.0', PORT_UPI_MACHINE))
                        self.server_socket.listen(5)
                        continue
                    else:
                        print(f"Socket error in accept(): {e}")
                        break
        except KeyboardInterrupt:
            print("UPI Machine Server shutting down...")
        finally:
            if hasattr(self, 'server_socket') and self.server_socket:
                try:
                    self.server_socket.close()
                except Exception as e:
                    print(f"Error closing UPI Machine socket: {e}")
    
    def start(self):
        """Start the UPI machine UI"""
        while True:
            print("\n===== UPI Machine =====")
            print("1. Generate QR Code for Merchant")
            print("2. View Current Transaction")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                self.generate_qr_ui()
            elif choice == "2":
                self.view_transaction()
            elif choice == "3":
                print("Exiting UPI Machine...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def generate_qr_ui(self):
        """UI for generating QR code"""
        print("\n----- Generate QR Code -----")
        
        mid = input("Enter Merchant ID: ")
        
        if not mid:
            print("Merchant ID cannot be empty.")
            return
        
        result = self.generate_qr_code_for_merchant(mid)
        
        if result["status"] == "success":
            print(f"\nQR code generated successfully!")
            print(f"VMID: {result['vmid']}")
            print(f"QR code has been displayed and saved as '{result['qr_filepath']}'.")
        else:
            print(f"\nError: {result['message']}")
    
    def view_transaction(self):
        """View current transaction"""
        print("\n----- Current Transaction -----")
        
        if not self.current_transaction:
            print("No transaction in progress.")
            return
        
        print(f"VMID: {self.current_transaction['vmid']}")
        print(f"MMID: {self.current_transaction['mmid']}")
        print(f"Amount: ₹{float(self.current_transaction['amount']):.2f}")
        print(f"Status: Processing")


if __name__ == "__main__":
    upi_machine = UPIMachine()
    upi_machine.start()