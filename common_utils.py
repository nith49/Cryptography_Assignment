"""
Common utilities and functions for the UPI Payment Gateway System
"""

import hashlib
import json
import time
import socket
import threading
import base64
import qrcode
from PIL import Image
import io
import random
import string
import os

# Network Configuration
CONFIG_FILE = 'network_config.json'

def load_config():
    """Load or create network configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default configuration
        config = {
            "bank_server": {"host": "127.0.0.1", "port": 5001},
            "upi_machine": {"host": "127.0.0.1", "port": 5002},
            "user_client": {"host": "127.0.0.1", "port": 5003}
        }
        # Save default config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return config

# Load configuration
CONFIG = load_config()

# Constants
PORT_BANK = CONFIG["bank_server"]["port"]
PORT_UPI_MACHINE = CONFIG["upi_machine"]["port"]
PORT_USER = CONFIG["user_client"]["port"]
HOST = '127.0.0.1'  # Default value, will be updated by main.py

# Actual server addresses for cross-machine communication
BANK_SERVER_HOST = CONFIG["bank_server"]["host"]
UPI_MACHINE_HOST = CONFIG["upi_machine"]["host"]
USER_CLIENT_HOST = CONFIG["user_client"]["host"]

# Bank details
BANKS = {
    "HDFC": {
        "name": "HDFC Bank",
        "branches": {
            "HDFC0001": "Mumbai Branch",
            "HDFC0002": "Delhi Branch",
            "HDFC0003": "Bangalore Branch"
        }
    },
    "ICICI": {
        "name": "ICICI Bank",
        "branches": {
            "ICIC0001": "Mumbai Branch",
            "ICIC0002": "Delhi Branch",
            "ICIC0003": "Bangalore Branch"
        }
    },
    "SBI": {
        "name": "State Bank of India",
        "branches": {
            "SBIN0001": "Mumbai Branch",
            "SBIN0002": "Delhi Branch",
            "SBIN0003": "Bangalore Branch"
        }
    }
}

def get_bank_from_ifsc(ifsc_code):
    """Extract bank name from IFSC code"""
    bank_code = ifsc_code[:4]
    for bank_key, bank_data in BANKS.items():
        for branch_ifsc in bank_data["branches"].keys():
            if branch_ifsc.startswith(bank_code):
                return bank_key
    return None

def generate_sha256_hash(input_str):
    """Generate SHA256 hash for the given input string"""
    return hashlib.sha256(input_str.encode()).hexdigest()

def truncate_hash_to_16(hash_str):
    """Truncate SHA256 hash to 16 characters"""
    return hash_str[:16]

def generate_merchant_id(name, password, timestamp):
    """Generate a 16-digit Merchant ID using SHA256"""
    input_string = f"{name}_{timestamp}_{password}"
    full_hash = generate_sha256_hash(input_string)
    return truncate_hash_to_16(full_hash)

def generate_user_id(name, password, timestamp):
    """Generate a 16-digit User ID using SHA256"""
    input_string = f"{name}_{timestamp}_{password}"
    full_hash = generate_sha256_hash(input_string)
    return truncate_hash_to_16(full_hash)

def generate_mmid(uid, mobile_number):
    """Generate MMID using UID and mobile number"""
    input_string = f"{uid}_{mobile_number}"
    full_hash = generate_sha256_hash(input_string)
    return truncate_hash_to_16(full_hash)

def generate_transaction_id(uid, mid, amount, timestamp):
    """Generate a transaction ID for blockchain"""
    input_string = f"{uid}_{mid}_{amount}_{timestamp}"
    return generate_sha256_hash(input_string)

def send_message(host, port, message):
    """Send a message to the specified host and port"""
    try:
        # Determine which server to connect to based on port
        if port == PORT_BANK:
            target_host = BANK_SERVER_HOST
        elif port == PORT_UPI_MACHINE:
            target_host = UPI_MACHINE_HOST
        elif port == PORT_USER:
            target_host = USER_CLIENT_HOST
        else:
            target_host = host
            
        print(f"Connecting to {target_host}:{port} with message type: {message.get('type', 'unknown')}")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set timeout for connection
            sock.settimeout(10)
            sock.connect((target_host, port))
            sock.sendall(json.dumps(message).encode())
            response = sock.recv(4096).decode()
            return json.loads(response)
    except Exception as e:
        print(f"Error sending message: {e}")
        print(f"Failed connecting to {target_host}:{port}")
        return {"status": "error", "message": str(e)}

# SPECK implementation and rest of the code remains the same
# ...

# The rest of your code remains unchanged
class SPECK:
    """
    SPECK is a family of lightweight block ciphers.
    This is a simplified version for demonstration purposes.
    """
    def __init__(self, key):
        self.key = key.ljust(16, '0')[:16].encode()  # Ensure 16-byte key
        
    def _rotate_right(self, val, r):
        """Rotate right by r bits"""
        return ((val >> r) | (val << (32 - r))) & 0xFFFFFFFF
    
    def _rotate_left(self, val, r):
        """Rotate left by r bits"""
        return ((val << r) | (val >> (32 - r))) & 0xFFFFFFFF
    
    def encrypt(self, text):
        """Encrypt using SPECK algorithm"""
        # Convert input to bytes and pad if necessary
        text_bytes = text.encode()
        padded_text = text_bytes + b'\0' * (8 - len(text_bytes) % 8 if len(text_bytes) % 8 else 0)
        
        # Key schedule
        k = [int.from_bytes(self.key[i:i+4], 'little') for i in range(0, 16, 4)]
        
        result = bytearray()
        
        # Process each block
        for i in range(0, len(padded_text), 8):
            block = padded_text[i:i+8]
            x = int.from_bytes(block[0:4], 'little')
            y = int.from_bytes(block[4:8], 'little')
            
            # Apply encryption rounds
            for _ in range(20):
                x = (self._rotate_right(x, 8) + y) & 0xFFFFFFFF
                x ^= k[0]
                y = self._rotate_left(y, 3) ^ x
                
            # Convert result back to bytes
            result.extend(x.to_bytes(4, 'little'))
            result.extend(y.to_bytes(4, 'little'))
        
        # Return base64 encoded result for easy transmission
        return base64.b64encode(result).decode()
    
    def decrypt(self, cipher_text):
        """Decrypt using SPECK algorithm"""
        # Decode base64
        cipher_bytes = base64.b64decode(cipher_text.encode())
        
        # Key schedule
        k = [int.from_bytes(self.key[i:i+4], 'little') for i in range(0, 16, 4)]
        
        result = bytearray()
        
        # Process each block
        for i in range(0, len(cipher_bytes), 8):
            block = cipher_bytes[i:i+8]
            x = int.from_bytes(block[0:4], 'little')
            y = int.from_bytes(block[4:8], 'little')
            
            # Apply decryption rounds
            for _ in range(20):
                y ^= x
                y = self._rotate_right(y, 3)
                x ^= k[0]
                x = (x - y) & 0xFFFFFFFF
                x = self._rotate_left(x, 8)
                
            # Convert result back to bytes
            result.extend(x.to_bytes(4, 'little'))
            result.extend(y.to_bytes(4, 'little'))
        
        # Remove padding and return as string
        return result.rstrip(b'\0').decode(errors='ignore')

def generate_qr_code(data):
    """Generate QR code for the given data and return as bytes"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def display_qr_code(data):
    """Generate and display a QR code for the given data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_code.png")
    print(f"QR code saved as 'qr_code.png'. Please scan with your device.")
    img.show()

# Quantum attack simulation
def simulate_quantum_attack(pin, uid):
    """
    Simulate a quantum computing attack on PIN and UID
    This is just a demonstration and not a real quantum attack
    """
    print(f"Simulating quantum attack on user credentials...")
    print(f"Target PIN length: {len(str(pin))} digits")
    print(f"Target UID: {uid}")
    
    # Simulate attacks taking different amounts of time
    attack_time = random.randint(2, 5)
    print(f"Quantum attack simulation in progress...")
    time.sleep(attack_time)
    
    # Since this is a simulation, randomly decide if attack was successful
    success = random.choice([True, False])
    
    if success:
        print(f"Quantum attack successful!")
        print(f"Compromised PIN: {pin}")
        probability = random.randint(70, 99)
        print(f"PIN was recovered with {probability}% confidence")
    else:
        print(f"Quantum attack failed to recover credentials")
        print(f"This suggests PIN may be quantum-resistant or additional protection mechanisms are working")
    
    return success