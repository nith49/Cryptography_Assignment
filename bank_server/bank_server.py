"""
Bank Server Implementation for UPI Payment Gateway System
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
    generate_merchant_id, generate_user_id, generate_mmid, 
    HOST, PORT_BANK, PORT_UPI_MACHINE, PORT_USER,
    send_message, get_bank_from_ifsc, BANKS, SPECK,
    simulate_quantum_attack
)
from blockchain import Blockchain # type: ignore

class BankServer:
    """Bank Server Implementation"""
    def __init__(self):
        # Initialize bank data
        self.merchants = {}  # merchant_id -> merchant_data
        self.users = {}  # user_id -> user_data
        self.mmid_to_uid = {}  # mmid -> user_id mapping
        
        # Initialize blockchains for each bank
        self.blockchains = {
            "HDFC": Blockchain("HDFC"),
            "ICICI": Blockchain("ICICI"),
            "SBI": Blockchain("SBI")
        }
        
        # Initialize server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', PORT_BANK))
        self.server_socket.listen(5)
        
        print(f"Bank Server started on {HOST}:{PORT_BANK}")
        
        # Load data if exists
        self.load_data()
        
        # Start server thread
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def load_data(self):
        """Load bank data from files if they exist"""
        try:
            if os.path.exists("merchants.json"):
                with open("merchants.json", "r") as f:
                    self.merchants = json.load(f)
                print(f"Loaded {len(self.merchants)} merchants")
            
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    self.users = json.load(f)
                print(f"Loaded {len(self.users)} users")
                
                # Rebuild mmid_to_uid mapping
                for uid, user_data in self.users.items():
                    if "mmid" in user_data:
                        self.mmid_to_uid[user_data["mmid"]] = uid
            
            # Also load blockchain data
            self.load_blockchain_data()
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save bank data to files"""
        try:
            with open("merchants.json", "w") as f:
                json.dump(self.merchants, f, indent=2)
            
            with open("users.json", "w") as f:
                json.dump(self.users, f, indent=2)
            
            # Also save blockchain data
            self.save_blockchain_data()
            
            print("Data saved successfully")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def save_blockchain_data(self):
        """Save blockchain data to files"""
        try:
            # Create directory if it doesn't exist
            if not os.path.exists("blockchain_data"):
                os.makedirs("blockchain_data")
            
            # Save blockchain data for each bank
            for bank_name, blockchain in self.blockchains.items():
                filename = f"blockchain_data/{bank_name}_blockchain.json"
                with open(filename, "w") as f:
                    # Serialize blockchain data
                    chain_data = [block.serialize() for block in blockchain.chain]
                    json.dump(chain_data, f, indent=2)
            
            print("Blockchain data saved successfully")
        except Exception as e:
            print(f"Error saving blockchain data: {e}")
    
    def load_blockchain_data(self):
        """Load blockchain data from files"""
        try:
            # Check if blockchain_data directory exists
            if not os.path.exists("blockchain_data"):
                print("No blockchain data found")
                return
            
            # Load blockchain data for each bank
            for bank_name in self.blockchains.keys():
                filename = f"blockchain_data/{bank_name}_blockchain.json"
                if os.path.exists(filename):
                    with open(filename, "r") as f:
                        chain_data = json.load(f)
                        # Deserialize and rebuild blockchain
                        self.blockchains[bank_name].rebuild_chain(chain_data)
                    print(f"Loaded blockchain for {bank_name}")
        except Exception as e:
            print(f"Error loading blockchain data: {e}")
    
    def register_merchant(self, data):
        """Register a new merchant"""
        required_fields = ["name", "ifsc_code", "password", "initial_balance"]
        for field in required_fields:
            if field not in data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Check if IFSC code is valid
        bank_name = get_bank_from_ifsc(data["ifsc_code"])
        if not bank_name:
            return {"status": "error", "message": "Invalid IFSC code"}
        
        # Generate Merchant ID
        timestamp = time.time()
        mid = generate_merchant_id(data["name"], data["password"], timestamp)
        
        # Store merchant data
        self.merchants[mid] = {
            "name": data["name"],
            "ifsc_code": data["ifsc_code"],
            "password_hash": data["password"],  # In real app, we would hash the password
            "balance": float(data["initial_balance"]),
            "bank": bank_name,
            "created_at": timestamp
        }
        
        # Save data
        self.save_data()
        
        return {
            "status": "success", 
            "message": "Merchant registered successfully", 
            "merchant_id": mid
        }
    
    def register_user(self, data):
        """Register a new user"""
        required_fields = ["name", "ifsc_code", "password", "initial_balance", "pin", "mobile_number"]
        for field in required_fields:
            if field not in data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Check if IFSC code is valid
        bank_name = get_bank_from_ifsc(data["ifsc_code"])
        if not bank_name:
            return {"status": "error", "message": "Invalid IFSC code"}
        
        # Generate User ID
        timestamp = time.time()
        uid = generate_user_id(data["name"], data["password"], timestamp)
        
        # Generate MMID
        mmid = generate_mmid(uid, data["mobile_number"])
        
        # Store user data
        self.users[uid] = {
            "name": data["name"],
            "ifsc_code": data["ifsc_code"],
            "password_hash": data["password"],  # In real app, we would hash the password
            "pin": data["pin"],  # In real app, we would hash the pin
            "balance": float(data["initial_balance"]),
            "bank": bank_name,
            "mobile_number": data["mobile_number"],
            "mmid": mmid,
            "created_at": timestamp
        }
        
        # Update MMID to UID mapping
        self.mmid_to_uid[mmid] = uid
        
        # Save data
        self.save_data()
        
        return {
            "status": "success", 
            "message": "User registered successfully", 
            "user_id": uid,
            "mmid": mmid
        }
    
    def process_transaction(self, data):
        """Process a transaction from UPI machine"""
        required_fields = ["mid", "mmid", "amount", "pin"]
        for field in required_fields:
            if field not in data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Get user ID from MMID
        uid = self.mmid_to_uid.get(data["mmid"])
        if not uid:
            return {"status": "error", "message": "Invalid MMID"}
        
        # Verify PIN
        user = self.users.get(uid)
        if not user or user["pin"] != data["pin"]:
            return {"status": "error", "message": "Invalid PIN"}
        
        # Check if merchant exists
        merchant = self.merchants.get(data["mid"])
        if not merchant:
            return {"status": "error", "message": "Invalid Merchant ID"}
        
        # Check if user has sufficient balance
        amount = float(data["amount"])
        if user["balance"] < amount:
            return {"status": "error", "message": "Insufficient balance"}
        
        # Quantum attack simulation on PIN (for educational purposes)
        # This would normally not be part of a real system
        if "simulate_quantum_attack" in data and data["simulate_quantum_attack"]:
            attack_success = simulate_quantum_attack(user["pin"], uid)
            # If simulating, still proceed with transaction
        
        # Process the transaction
        user["balance"] -= amount
        merchant["balance"] += amount
        
        # Create transaction record
        timestamp = time.time()
        transaction_id = f"{uid}_{data['mid']}_{timestamp}"
        transaction_data = {
            "transaction_id": transaction_id,
            "from_user": uid,
            "to_merchant": data["mid"],
            "amount": amount,
            "timestamp": timestamp,
            "user_bank": user["bank"],
            "merchant_bank": merchant["bank"]
        }
        
        # Add transaction to blockchain
        user_bank = user["bank"]
        merchant_bank = merchant["bank"]
        
        # Add to user's bank blockchain
        self.blockchains[user_bank].add_transaction(transaction_data)
        
        # If merchant is in a different bank, add to merchant's bank blockchain too
        if user_bank != merchant_bank:
            self.blockchains[merchant_bank].add_transaction(transaction_data)
        
        # Save updated data
        self.save_data()
        
        return {
            "status": "success",
            "message": "Transaction processed successfully",
            "transaction_id": transaction_id,
            "amount": amount,
            "timestamp": timestamp,
            "user_balance": user["balance"],
            "merchant_balance": merchant["balance"]
        }
    
    def validate_merchant(self, mid, password):
        """Validate merchant credentials"""
        merchant = self.merchants.get(mid)
        if not merchant or merchant["password_hash"] != password:
            return False
        return True
    
    def generate_vmid(self, mid):
        """Generate Virtual Merchant ID using LWC"""
        merchant = self.merchants.get(mid)
        if not merchant:
            return {"status": "error", "message": "Invalid Merchant ID"}
        
        # Use SPECK for lightweight encryption
        speck = SPECK(mid)  # Use merchant ID as the key
        timestamp = str(time.time())
        vmid = speck.encrypt(f"{mid}_{timestamp}")
        
        return {
            "status": "success",
            "vmid": vmid,
            "mid": mid,
            "timestamp": timestamp
        }
    
    def decode_vmid(self, vmid, mid):
        """Decode Virtual Merchant ID using LWC"""
        # Use SPECK for lightweight decryption
        speck = SPECK(mid)  # Use merchant ID as the key
        try:
            decrypted = speck.decrypt(vmid)
            # Verify the decrypted data contains the original MID
            if mid in decrypted:
                return {
                    "status": "success",
                    "mid": mid
                }
            return {"status": "error", "message": "Invalid VMID"}
        except Exception as e:
            return {"status": "error", "message": f"Decryption error: {e}"}
    
    def get_merchant_balance(self, mid):
        """Get merchant balance"""
        merchant = self.merchants.get(mid)
        if not merchant:
            return {"status": "error", "message": "Invalid Merchant ID"}
        
        return {
            "status": "success",
            "balance": merchant["balance"]
        }
    
    def get_user_balance(self, mmid, pin):
        """Get user balance"""
        uid = self.mmid_to_uid.get(mmid)
        if not uid:
            return {"status": "error", "message": "Invalid MMID"}
        
        user = self.users.get(uid)
        if not user or user["pin"] != pin:
            return {"status": "error", "message": "Invalid PIN"}
        
        return {
            "status": "success",
            "balance": user["balance"]
        }
    
    def get_user_transactions(self, mmid, pin):
        """Get user transactions"""
        uid = self.mmid_to_uid.get(mmid)
        if not uid:
            return {"status": "error", "message": "Invalid MMID"}
        
        user = self.users.get(uid)
        if not user or user["pin"] != pin:
            return {"status": "error", "message": "Invalid PIN"}
        
        # Get transactions from blockchain
        bank_name = user["bank"]
        transactions = self.blockchains[bank_name].get_transactions_by_user(uid)
        
        return {
            "status": "success",
            "transactions": transactions
        }
    
    def get_merchant_transactions(self, mid, password):
        """Get merchant transactions"""
        merchant = self.merchants.get(mid)
        if not merchant or merchant["password_hash"] != password:
            return {"status": "error", "message": "Invalid credentials"}
        
        # Get transactions from blockchain
        bank_name = merchant["bank"]
        transactions = self.blockchains[bank_name].get_transactions_by_merchant(mid)
        
        return {
            "status": "success",
            "transactions": transactions
        }
    
    def get_transaction_history(self, bank_name=None, uid=None, mid=None):
        """
        View transaction history with optional filtering by bank, user, or merchant
        
        Args:
            bank_name (str, optional): Filter by bank name (HDFC, ICICI, SBI)
            uid (str, optional): Filter by user ID
            mid (str, optional): Filter by merchant ID
            
        Returns:
            List of transactions matching the filter criteria
        """
        all_transactions = []
        seen_transaction_ids = set()
        
        # Determine which blockchains to check
        if bank_name and bank_name in self.blockchains:
            blockchains_to_check = {bank_name: self.blockchains[bank_name]}
        else:
            blockchains_to_check = self.blockchains
        
        # Get transactions from each blockchain
        for bank, blockchain in blockchains_to_check.items():
            if uid:
                # Get transactions for specific user
                transactions = blockchain.get_transactions_by_user(uid)
            elif mid:
                # Get transactions for specific merchant
                transactions = blockchain.get_transactions_by_merchant(mid)
            else:
                # Get all transactions
                transactions = blockchain.get_all_transactions()
            
            # Add bank name to each transaction for clarity
            for transaction in transactions:
                transaction_id = transaction.get('transaction_id', '')
                if transaction_id not in seen_transaction_ids:
                    transaction['bank'] = bank
                    all_transactions.append(transaction)
                    seen_transaction_ids.add(transaction_id)
        
        # Sort transactions by timestamp (most recent first)
        all_transactions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return all_transactions
    
    def view_transaction_history_ui(self):
        """UI for viewing transaction history with improved display and export options"""
        print("\n----- View Transaction History -----")
        print("Filter options:")
        print("1. View all transactions")
        print("2. Filter by bank")
        print("3. Filter by user")
        print("4. Filter by merchant")
        
        choice = input("Enter your choice (1-4): ")
        
        bank_name = None
        uid = None
        mid = None
        
        if choice == "2":
            print("\nSelect a bank:")
            print("1. HDFC Bank")
            print("2. ICICI Bank")
            print("3. SBI Bank")
            
            bank_choice = input("Enter your choice (1-3): ")
            bank_map = {"1": "HDFC", "2": "ICICI", "3": "SBI"}
            
            if bank_choice in bank_map:
                bank_name = bank_map[bank_choice]
            else:
                print("Invalid choice.")
                return
        
        elif choice == "3":
            uid = input("Enter User ID (UID): ")
            if uid not in self.users:
                print("User not found.")
                return
        
        elif choice == "4":
            mid = input("Enter Merchant ID (MID): ")
            if mid not in self.merchants:
                print("Merchant not found.")
                return
        
        elif choice != "1":
            print("Invalid choice.")
            return
        
        # Get transaction history
        transactions = self.get_transaction_history(bank_name, uid, mid)
        
        if not transactions:
            print("\nNo transactions found matching the criteria.")
            return
        
        # Display options
        print(f"\nFound {len(transactions)} transactions.")
        print("Display options:")
        print("1. Display all transactions")
        print("2. Display and save")
        
        display_choice = input("Enter your choice (1-2): ")
        
        # Create a formatted transaction list
        formatted_transactions = []
        for transaction in transactions:
            # Convert timestamp to readable date/time
            timestamp = transaction.get('timestamp', 0)
            date_time = "Unknown"
            if timestamp:
                from datetime import datetime
                date_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            formatted_tx = {
                "id": transaction.get('transaction_id', 'Unknown'),
                "bank": transaction.get('bank', 'Unknown'),
                "from_user": transaction.get('from_user', 'Unknown'),
                "to_merchant": transaction.get('to_merchant', 'Unknown'),
                "amount": f"₹{float(transaction.get('amount', 0)):.2f}",
                "date_time": date_time,
                "user_bank": transaction.get('user_bank', 'Unknown'),
                "merchant_bank": transaction.get('merchant_bank', 'Unknown')
            }
            formatted_transactions.append(formatted_tx)
        
        # Display all transactions
        if display_choice in ["1", "2"]:
            self._display_all_transactions(formatted_transactions)
        
        # Save to JSON file
        if display_choice in ["2"]:
            self._save_transactions_to_json(transactions)
    
    def _display_all_transactions(self, transactions):
        """Display all transactions in a formatted way"""
        print("\n----- Transaction History -----")
        
        # Print table header
        print(f"{'ID':<15} {'Date/Time':<20} {'From':<15} {'To':<15} {'Amount':<12} {'Bank':<10}")
        print("-" * 90)
        
        # Print each transaction
        for tx in transactions:
            print(f"{tx['id'][:12]:<15} {tx['date_time']:<20} {tx['from_user'][:12]:<15} "
                  f"{tx['to_merchant'][:12]:<15} {tx['amount']:<12} {tx['bank']:<10}")
        
        print("\nFor more details on a specific transaction, use the 'get_user_transactions' or 'get_merchant_transactions' commands.")
    
    def _save_transactions_to_json(self, transactions):
        """Save transactions to a JSON file"""
        import json
        from datetime import datetime
        
        # Create a directory for transaction history if it doesn't exist
        if not os.path.exists("transaction_history"):
            os.makedirs("transaction_history")
        
        # Create a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transaction_history/transaction_history_{timestamp}.json"
        
        try:
            with open(filename, "w") as f:
                json.dump(transactions, f, indent=2)
            print(f"\nTransaction history successfully saved to {filename}")
        except Exception as e:
            print(f"\nError saving transaction history: {e}")
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            # Receive data from client
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            
            # Process request
            response = {"status": "error", "message": "Unknown request type"}
            
            if "type" in request:
                if request["type"] == "register_merchant":
                    response = self.register_merchant(request["data"])
                elif request["type"] == "register_user":
                    response = self.register_user(request["data"])
                elif request["type"] == "process_transaction":
                    response = self.process_transaction(request["data"])
                elif request["type"] == "validate_merchant":
                    valid = self.validate_merchant(request["mid"], request["password"])
                    response = {"status": "success" if valid else "error", 
                               "message": "Valid credentials" if valid else "Invalid credentials"}
                elif request["type"] == "generate_vmid":
                    response = self.generate_vmid(request["mid"])
                elif request["type"] == "decode_vmid":
                    response = self.decode_vmid(request["vmid"], request["mid"])
                elif request["type"] == "get_merchant_balance":
                    response = self.get_merchant_balance(request["mid"])
                elif request["type"] == "get_user_balance":
                    response = self.get_user_balance(request["mmid"], request["pin"])
                elif request["type"] == "get_user_transactions":
                    response = self.get_user_transactions(request["mmid"], request["pin"])
                elif request["type"] == "get_merchant_transactions":
                    response = self.get_merchant_transactions(request["mid"], request["password"])
                elif request["type"] == "list_merchants":
                    # Just for testing
                    response = {"status": "success", "merchants": self.merchants}
                elif request["type"] == "list_users":
                    # Just for testing
                    response = {"status": "success", "users": self.users}
                
            # Send response
            client_socket.sendall(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error handling client: {e}")
            try:
                error_response = {"status": "error", "message": f"Server error: {str(e)}"}
                client_socket.sendall(json.dumps(error_response).encode())
            except:
                pass
        finally:
            client_socket.close()
    
    def start_server(self):
        """Start the bank server"""
        print("Bank Server is running. Waiting for connections...")
        
        try:
            while True:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"Connection from {addr}")
                    
                    # Handle client in a separate thread
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
                        self.server_socket.bind(('0.0.0.0', PORT_BANK))
                        self.server_socket.listen(5)
                        continue
                    else:
                        raise
        except KeyboardInterrupt:
            print("Bank Server shutting down...")
        finally:
            if hasattr(self, 'server_socket') and self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
            self.save_data()
    
    def start(self):
        """Start the bank terminal UI"""
        while True:
            print("\n===== Bank Terminal =====")
            print("1. List All Banks")
            print("2. List All Merchants")
            print("3. List All Users")
            print("4. View Blockchain for a Bank")
            print("5. Validate Blockchain Integrity")
            print("6. Register New Merchant")
            print("7. Register New User")
            print("8. View Transaction History")
            print("9. Simulate Quantum Attack")
            print("10. Exit")
            
            choice = input("Enter your choice (1-10): ")
            
            if choice == "1":
                self.list_banks()
            elif choice == "2":
                self.list_merchants()
            elif choice == "3":
                self.list_users()
            elif choice == "4":
                self.view_blockchain()
            elif choice == "5":
                self.validate_blockchain()
            elif choice == "6":
                self.register_merchant_ui()
            elif choice == "7":
                self.register_user_ui()
            elif choice == "8":
                self.view_transaction_history_ui()
            elif choice == "9":
                self.simulate_quantum_attack_ui()
            elif choice == "10":
                print("Exiting Bank Terminal...")
                self.save_data()
                break
            else:
                print("Invalid choice. Please try again.")
    
    def list_banks(self):
        """List all banks in the system"""
        print("\n----- Banks -----")
        for bank_code, bank_data in BANKS.items():
            print(f"Bank: {bank_data['name']} ({bank_code})")
            print("Branches:")
            for ifsc, branch_name in bank_data["branches"].items():
                print(f"  - {branch_name} (IFSC: {ifsc})")
            print()
    
    def list_merchants(self):
        """List all merchants in the system"""
        if not self.merchants:
            print("\nNo merchants registered yet.")
            return
        
        print("\n----- Merchants -----")
        for mid, merchant in self.merchants.items():
            print(f"Merchant ID: {mid}")
            print(f"Name: {merchant['name']}")
            print(f"Bank: {merchant['bank']}")
            print(f"IFSC: {merchant['ifsc_code']}")
            print(f"Balance: ₹{merchant['balance']:.2f}")
            print(f"Created: {datetime.fromtimestamp(merchant['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    def list_users(self):
        """List all users in the system"""
        if not self.users:
            print("\nNo users registered yet.")
            return
        
        print("\n----- Users -----")
        for uid, user in self.users.items():
            print(f"User ID: {uid}")
            print(f"Name: {user['name']}")
            print(f"Bank: {user['bank']}")
            print(f"IFSC: {user['ifsc_code']}")
            print(f"Mobile: {user['mobile_number']}")
            print(f"MMID: {user['mmid']}")
            print(f"Balance: ₹{user['balance']:.2f}")
            print(f"Created: {datetime.fromtimestamp(user['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    def view_blockchain(self):
        """View blockchain for a specific bank"""
        print("\n----- View Blockchain -----")
        print("Select a bank:")
        print("1. HDFC Bank")
        print("2. ICICI Bank")
        print("3. SBI Bank")
        
        choice = input("Enter your choice (1-3): ")
        
        bank_map = {"1": "HDFC", "2": "ICICI", "3": "SBI"}
        if choice in bank_map:
            bank_name = bank_map[choice]
            blockchain = self.blockchains[bank_name]
            
            print(f"\nBlockchain for {bank_name} Bank:")
            blockchain.print_chain()
        else:
            print("Invalid choice.")
    
    def validate_blockchain(self):
        """Validate the integrity of blockchains"""
        print("\n----- Blockchain Validation -----")
        for bank_name, blockchain in self.blockchains.items():
            is_valid = blockchain.is_chain_valid()
            print(f"{bank_name} Bank Blockchain: {'Valid' if is_valid else 'INVALID - TAMPERING DETECTED!'}")
    
    def register_merchant_ui(self):
        """UI for registering a new merchant"""
        print("\n----- Register New Merchant -----")
        
        name = input("Enter merchant name: ")
        
        print("\nAvailable banks and branches:")
        for bank_code, bank_data in BANKS.items():
            print(f"\n{bank_data['name']} ({bank_code}):")
            for ifsc, branch_name in bank_data["branches"].items():
                print(f"  - {branch_name} (IFSC: {ifsc})")
        
        ifsc_code = input("\nEnter IFSC code: ")
        password = input("Enter password: ")
        
        try:
            initial_balance = float(input("Enter initial account balance: "))
        except ValueError:
            print("Invalid amount. Please enter a number.")
            return
        
        data = {
            "name": name,
            "ifsc_code": ifsc_code,
            "password": password,
            "initial_balance": initial_balance
        }
        
        result = self.register_merchant(data)
        
        if result["status"] == "success":
            print(f"\nMerchant registered successfully!")
            print(f"Merchant ID: {result['merchant_id']}")
        else:
            print(f"\nError: {result['message']}")
        
    def register_user_ui(self):
        """UI for registering a new user"""
        print("\n----- Register New User -----")
        
        name = input("Enter user name: ")
        
        print("\nAvailable banks and branches:")
        for bank_code, bank_data in BANKS.items():
            print(f"\n{bank_data['name']} ({bank_code}):")
            for ifsc, branch_name in bank_data["branches"].items():
                print(f"  - {branch_name} (IFSC: {ifsc})")
        
        ifsc_code = input("\nEnter IFSC code: ")
        password = input("Enter password: ")
        mobile_number = input("Enter mobile number: ")
        pin = input("Enter UPI PIN (4 digits): ")
        
        try:
            initial_balance = float(input("Enter initial account balance: "))
        except ValueError:
            print("Invalid amount. Please enter a number.")
            return
        
        
        data = {
            "name": name,
            "ifsc_code": ifsc_code,
            "password": password,
            "mobile_number": mobile_number,
            "pin": pin,
            "initial_balance": initial_balance
        }
        
        result = self.register_user(data)
        
        if result["status"] == "success":
            print(f"\nUser registered successfully!")
            print(f"User ID: {result['user_id']}")
            print(f"MMID: {result['mmid']}")
        else:
            print(f"\nError: {result['message']}")
    
    def simulate_quantum_attack_ui(self):
        """UI for simulating quantum attack on user credentials"""
        print("\n----- Simulate Quantum Attack -----")
        
        if not self.users:
            print("No users registered yet.")
            return
        
        mmid = input("Enter user MMID to target: ")
        
        uid = self.mmid_to_uid.get(mmid)
        if not uid:
            print("Invalid MMID.")
            return
        
        user = self.users.get(uid)
        if not user:
            print("User not found.")
            return
        
        print(f"\nTargeting user: {user['name']}")
        simulate_quantum_attack(user['pin'], uid)