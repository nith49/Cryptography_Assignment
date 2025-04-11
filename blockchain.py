"""
Blockchain implementation for UPI Payment Gateway System
"""

import hashlib
import json
import time
from datetime import datetime

class Block:
    """Block in the blockchain"""
    def __init__(self, index, timestamp, transaction_data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transaction_data = transaction_data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        """Calculate hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transaction_data": self.transaction_data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def __str__(self):
        """String representation of the block"""
        return f"Block #{self.index}\n" \
               f"Timestamp: {datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n" \
               f"Transaction Data: {json.dumps(self.transaction_data, indent=2)}\n" \
               f"Previous Hash: {self.previous_hash}\n" \
               f"Hash: {self.hash}\n"
    
    def serialize(self):
        """Make the block JSON serializable"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transaction_data': self.transaction_data,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
    
    def rebuild_from_dict(self, block_dict):
        """Rebuild block properties from dictionary"""
        self.index = block_dict['index']
        self.timestamp = block_dict['timestamp']
        self.transaction_data = block_dict['transaction_data']
        self.previous_hash = block_dict['previous_hash']
        self.hash = block_dict['hash']

class Blockchain:
    """Centralized blockchain ledger for the bank"""
    def __init__(self, bank_name):
        self.chain = []
        self.bank_name = bank_name
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, time.time(), {
            "transaction_id": "genesis",
            "bank": self.bank_name,
            "message": f"Genesis Block for {self.bank_name} Bank Blockchain"
        }, "0")
        
        self.chain.append(genesis_block)
        
    def get_latest_block(self):
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction_data):
        """Add a new transaction to the blockchain"""
        # Validate transaction data
        required_fields = ["transaction_id", "from_user", "to_merchant", "amount", "timestamp"]
        for field in required_fields:
            if field not in transaction_data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Create a new block for the transaction
        index = len(self.chain)
        timestamp = time.time()
        previous_hash = self.get_latest_block().hash
        
        new_block = Block(index, timestamp, transaction_data, previous_hash)
        self.chain.append(new_block)
        
        return {
            "status": "success", 
            "message": f"Transaction added to blockchain", 
            "block_hash": new_block.hash,
            "block_index": new_block.index
        }
    
    def is_chain_valid(self):
        """Validate the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_transactions_by_user(self, user_id):
        """Get all transactions involving a user"""
        user_transactions = []
        
        for block in self.chain[1:]:  # Skip genesis block
            if "from_user" in block.transaction_data and block.transaction_data["from_user"] == user_id:
                user_transactions.append(block.transaction_data)
        
        return user_transactions
    
    def get_transactions_by_merchant(self, merchant_id):
        """Get all transactions involving a merchant"""
        merchant_transactions = []
        
        for block in self.chain[1:]:  # Skip genesis block
            if "to_merchant" in block.transaction_data and block.transaction_data["to_merchant"] == merchant_id:
                merchant_transactions.append(block.transaction_data)
        
        return merchant_transactions
    
    def get_all_transactions(self):
        """Get all transactions in the blockchain"""
        transactions = []
        
        for block in self.chain[1:]:  # Skip genesis block
            transactions.append(block.transaction_data)
        
        return transactions
    
    def print_chain(self):
        """Print the entire blockchain"""
        for block in self.chain:
            print(block)
            print("-" * 50)
    
    def rebuild_chain(self, chain_data):
        """Rebuild blockchain from serialized data"""
        # Clear existing chain
        self.chain = []
        
        # Rebuild each block
        for block_data in chain_data:
            block = Block(
                index=0,  # Placeholder, will be overwritten
                timestamp=0,  # Placeholder, will be overwritten
                transaction_data={},  # Placeholder, will be overwritten
                previous_hash=""  # Placeholder, will be overwritten
            )
            block.rebuild_from_dict(block_data)
            self.chain.append(block)