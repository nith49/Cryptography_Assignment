"""
User Client Implementation for UPI Payment Gateway System
"""

import json
import socket
import threading
import time
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_utils import ( # type: ignore
    HOST, PORT_BANK, PORT_UPI_MACHINE, PORT_USER,
    send_message
)

class UserClient:
    """User Client Implementation"""
    def __init__(self):
        # User credentials
        self.mmid = None
        self.pin = None
        
        # Initialize server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', PORT_USER))
        self.server_socket.listen(5)
        
        print(f"User Client started on {HOST}:{PORT_USER}")
        
        # Start server thread
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def login(self, mmid, pin):
        """Login user with MMID and PIN"""
        # Verify credentials with bank
        response = send_message(HOST, PORT_BANK, {
            "type": "get_user_balance",
            "mmid": mmid,
            "pin": pin
        })
        
        if response["status"] == "success":
            self.mmid = mmid
            self.pin = pin
            return {
                "status": "success",
                "message": "Login successful",
                "balance": response["balance"]
            }
        else:
            return {
                "status": "error",
                "message": response["message"]
            }
    
    def logout(self):
        """Logout user"""
        self.mmid = None
        self.pin = None
        return {
            "status": "success",
            "message": "Logout successful"
        }
    
    def scan_qr_code(self, qr_data, amount, simulate_quantum_attack=False):
        """Process payment by scanning QR code"""
        if not self.mmid or not self.pin:
            return {"status": "error", "message": "User not logged in"}
        
        # QR data contains VMID
        payment_data = {
            "vmid": qr_data,
            "mmid": self.mmid,
            "pin": self.pin,
            "amount": amount
        }
        
        if simulate_quantum_attack:
            payment_data["simulate_quantum_attack"] = True
        
        # Send payment request to UPI machine
        response = send_message(HOST, PORT_UPI_MACHINE, {
            "type": "process_payment",
            "payment_data": payment_data
        })
        
        return response
    
    def check_balance(self):
        """Check user balance"""
        if not self.mmid or not self.pin:
            return {"status": "error", "message": "User not logged in"}
        
        # Send balance request to bank
        response = send_message(HOST, PORT_BANK, {
            "type": "get_user_balance",
            "mmid": self.mmid,
            "pin": self.pin
        })
        
        return response
    
    def view_transactions(self):
        """View user transactions"""
        if not self.mmid or not self.pin:
            return {"status": "error", "message": "User not logged in"}
        
        # Send transactions request to bank
        response = send_message(HOST, PORT_BANK, {
            "type": "get_user_transactions",
            "mmid": self.mmid,
            "pin": self.pin
        })
        
        return response
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            # Receive data from client
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            
            # Process request
            response = {"status": "error", "message": "Unknown request type"}
            
            if "type" in request:
                if request["type"] == "login":
                    response = self.login(request["mmid"], request["pin"])
                elif request["type"] == "logout":
                    response = self.logout()
                elif request["type"] == "scan_qr":
                    response = self.scan_qr_code(request["qr_data"], request["amount"], 
                                               request.get("simulate_quantum_attack", False))
                elif request["type"] == "check_balance":
                    response = self.check_balance()
                elif request["type"] == "view_transactions":
                    response = self.view_transactions()
            
            # Send response
            client_socket.sendall(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error handling client: {e}")
            try:
                error_response = {"status": "error", "message": f"User Client error: {str(e)}"}
                client_socket.sendall(json.dumps(error_response).encode())
            except:
                pass
        finally:
            client_socket.close()
    
    def start_server(self):
        """Start the user client server"""
        print("User Client Server is running. Waiting for connections...")
        
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("User Client Server shutting down...")
        finally:
            self.server_socket.close()
    
    def start(self):
        """Start the user client UI"""
        while True:
            if self.mmid and self.pin:
                print(f"\n===== UPI User Client (Logged in as MMID: {self.mmid}) =====")
                print("1. Scan QR Code & Pay")
                print("2. Check Balance")
                print("3. View Transaction History")
                print("4. Logout")
                print("5. Exit")
                
                choice = input("Enter your choice (1-5): ")
                
                if choice == "1":
                    self.scan_qr_ui()
                elif choice == "2":
                    self.check_balance_ui()
                elif choice == "3":
                    self.view_transactions_ui()
                elif choice == "4":
                    self.logout()
                    print("Logged out successfully.")
                elif choice == "5":
                    print("Exiting User Client...")
                    break
                else:
                    print("Invalid choice. Please try again.")
            else:
                print("\n===== UPI User Client (Not logged in) =====")
                print("1. Login")
                print("2. Register New User")
                print("3. Exit")
                
                choice = input("Enter your choice (1-3): ")
                
                if choice == "1":
                    self.login_ui()
                elif choice == "2":
                    self.register_ui()
                elif choice == "3":
                    print("Exiting User Client...")
                    break
                else:
                    print("Invalid choice. Please try again.")
    
    def login_ui(self):
        """UI for user login"""
        print("\n----- Login -----")
        
        mmid = input("Enter MMID: ")
        pin = input("Enter PIN: ")
        
        result = self.login(mmid, pin)
        
        if result["status"] == "success":
            print(f"\nLogin successful!")
            print(f"Current Balance: ₹{result['balance']:.2f}")
        else:
            print(f"\nError: {result['message']}")
    
    def register_ui(self):
        """UI for user registration"""
        print("\n----- Register New User -----")
        print("Please use the Bank Terminal to register a new user.")
        input("Press Enter to continue...")
    
    def scan_qr_ui(self):
        """UI for scanning QR code and making payment"""
        print("\n----- Scan QR Code & Pay -----")
        
        qr_data = input("Enter QR code data (VMID): ")
        if not qr_data:
            print("QR code data cannot be empty.")
            return
        
        try:
            amount = float(input("Enter payment amount: "))
        except ValueError:
            print("Invalid amount. Please enter a number.")
            return
        
        # Ask if user wants to simulate quantum attack
        simulate_attack = input("Simulate quantum attack for educational purposes? (y/n): ").lower() == 'y'
        
        result = self.scan_qr_code(qr_data, amount, simulate_attack)
        
        if result["status"] == "success":
            print(f"\nPayment successful!")
            print(f"Transaction ID: {result['transaction_id']}")
            print(f"Amount: ₹{float(result['amount']):.2f}")
            print(f"New Balance: ₹{float(result['user_balance']):.2f}")
            print(f"Timestamp: {datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"\nError: {result['message']}")
    
    def check_balance_ui(self):
        """UI for checking balance"""
        print("\n----- Check Balance -----")
        
        result = self.check_balance()
        
        if result["status"] == "success":
            print(f"Current Balance: ₹{result['balance']:.2f}")
        else:
            print(f"Error: {result['message']}")
    
    def view_transactions_ui(self):
        """UI for viewing transaction history"""
        print("\n----- Transaction History -----")
        
        result = self.view_transactions()
        
        if result["status"] == "success":
            transactions = result["transactions"]
            
            if not transactions:
                print("No transactions found.")
                return
            
            for i, transaction in enumerate(transactions, 1):
                print(f"\nTransaction #{i}:")
                print(f"Transaction ID: {transaction['transaction_id']}")
                print(f"Amount: ₹{float(transaction['amount']):.2f}")
                print(f"Merchant: {transaction['to_merchant']}")
                print(f"Date: {datetime.fromtimestamp(transaction['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Error: {result['message']}")


if __name__ == "__main__":
    user_client = UserClient()
    user_client.start()