# Centralized UPI Payment Gateway System

## Overview
The Centralized UPI Payment Gateway System is a comprehensive simulation of India's Unified Payments Interface (UPI) ecosystem. This system implements a three-component architecture with advanced security features including blockchain ledger, SHA-256 hashing, SPECK encryption, and quantum attack simulation.

## System Architecture
The system consists of three primary components:

- **Bank Server** (Port 5001): Acts as the central authority that manages user accounts, merchant accounts, transaction processing, and maintains the blockchain ledger.

- **UPI Machine** (Port 5002): Simulates a merchant payment terminal that generates QR codes for transactions.

- **User Client** (Port 5003): Simulates a mobile banking application that allows users to scan QR codes and make payments.

Additionally, there's a **Data Sync Server** (Port 5005) that facilitates data sharing between distributed components when running on multiple devices.

Here's the GitHub link to view the project https://github.com/nith49/Cryptography_Assignment.git


## Prerequisites
Before beginning the implementation, ensure you have:
- Windows operating system
- Python 3.8 or higher installed
- Administrator privileges (for firewall configuration)
- Network connectivity between devices (if using multiple devices)

## Installation Guide

### Step 1: Install Required Python Packages
Open Command Prompt and run:
```
pip install qrcode pillow
```

These packages are essential for QR code generation and image processing.

### Step 2: Create Project Directory Structure
Create a new folder for the project and organize it with the following structure:
```
upi_payment_system/
├── bank_server/
│   ├── __init__.py
│   └── bank_server.py
│   └── config.json
├── upi_machine/
│   ├── __init__.py
│   └── upi_machine.py
├── user_client/
│   ├── __init__.py
│   └── user_client.py
├── blockchain.py
├── common_utils.py
├── main.py
├── shared_data.py
├── setup_firewall.bat
├── network_config.json
├── users.json
└── merchants.json
```

Note: The main.py script will automatically create the required directories and init.py files if they don't exist.

### Step 3: Configure Network Settings
Create or modify network_config.json with the appropriate IP addresses for each component:
```json
{
  "bank_server": {
    "host": "192.168.20.198",
    "port": 5001
  },
  "upi_machine": {
    "host": "192.168.20.38",
    "port": 5002
  },
  "user_client": {
    "host": "192.168.20.1",
    "port": 5003
  }
}
```

To find your IP address, run 'ipconfig' in Command Prompt and look for the IPv4 address under your active network connection.

### Step 4: Configure Windows Firewall
Run the setup_firewall.bat script as administrator to configure the necessary firewall rules:
- Right-click on the script and select "Run as administrator"
- Confirm the UAC prompt if it appears
- The script will add the necessary firewall rules for ports 5001, 5002, 5003, and 5005

If you prefer to manually configure the firewall, run these commands in an Administrator PowerShell window:
```powershell
# Allow incoming connections for Bank Server
netsh advfirewall firewall add rule name="UPI Bank Server" dir=in action=allow protocol=TCP localport=5001

# Allow incoming connections for UPI Machine
netsh advfirewall firewall add rule name="UPI Machine" dir=in action=allow protocol=TCP localport=5002

# Allow incoming connections for User Client
netsh advfirewall firewall add rule name="UPI User Client" dir=in action=allow protocol=TCP localport=5003

# Allow incoming connections for Data Sync Server
netsh advfirewall firewall add rule name="UPI Data Sync" dir=in action=allow protocol=TCP localport=5005
```

## Deployment Options

### Single-Machine Testing
For testing on a single machine, open three separate Command Prompt windows and run:

**Window 1 (Bank Server):**
```
cd path\to\upi_payment_system
python main.py bank
```

**Window 2 (UPI Machine):**
```
cd path\to\upi_payment_system
python main.py upi
```

**Window 3 (User Client):**
```
cd path\to\upi_payment_system
python main.py user
```

### Multi-Device Setup
For deploying across multiple physical devices:
1. Copy the entire project directory to each device
2. Update the network_config.json file on each device with the correct IP addresses
3. Run the appropriate component on each device in the following order:

**Start UPI Machine first:**
```
python main.py upi --host 192.168.20.38 --bank-host 192.168.20.198
```

**Start Bank Server second:**
```
python main.py bank --host 192.168.20.198
```

**Start User Client last:**
```
python main.py user --host 192.168.20.1 --bank-host 192.168.20.198 --upi-host 192.168.20.38
```

Replace the IP addresses with your actual device IP addresses.

### Testing Connections
To verify that all components can communicate with each other:
```
python main.py [component] --test
```

Replace [component] with bank, upi, or user depending on which component you're testing.

Once all components are running, perform these tests:

1. **Register a Merchant** (on Bank Server):
   - Choose option to register a new merchant
   - Note the Merchant ID

2. **Generate QR Code** (on UPI Machine):
   - Enter the Merchant ID to generate a QR code
   - The QR code will be displayed and saved

3. **Make a Payment** (on User Client):
   - Login with user credentials or register a new user
   - Choose "Scan QR Code & Pay"
   - Enter the QR code data (displayed on UPI Machine)
   - Enter payment amount and complete transaction

## System Usage

### Available Banks
The system comes pre-configured with the following banks and branches:
- **HDFC Bank (HDFC)**:
  - Mumbai Branch (IFSC: HDFC0001)
  - Delhi Branch (IFSC: HDFC0002)
  - Bangalore Branch (IFSC: HDFC0003)

- **ICICI Bank (ICICI)**:
  - Mumbai Branch (IFSC: ICIC0001)
  - Delhi Branch (IFSC: ICIC0002)
  - Bangalore Branch (IFSC: ICIC0003)

- **State Bank of India (SBI)**:
  - Mumbai Branch (IFSC: SBIN0001)
  - Delhi Branch (IFSC: SBIN0002)
  - Bangalore Branch (IFSC: SBIN0003)

### Bank Server Functions
The Bank Server provides the following options:
1. List All Banks
2. List All Merchants
3. List All Users
4. View Blockchain for a Bank
5. Validate Blockchain Integrity
6. Register New Merchant
7. Register New User
8. View Transaction History
9. Simulate Quantum Attack
10. Exit

**Example of Registering a New User:**
```
===== Bank Terminal =====
Enter your choice (1-10): 7
----- Register New User -----
Enter user name: kaushik2
Available banks and branches:
...
Enter IFSC code: ICIC0003
Enter password: 12348
Enter mobile number: 9908595468
Enter UPI PIN (4 digits): 1678
Enter initial account balance: 34500
User registered successfully!
User ID: f5185f42dd952853
MMID: 23dfa5ca02f77c4e
```

**Example of Registering a New Merchant:**
```
===== Bank Terminal =====
Enter your choice (1-10): 6
----- Register New Merchant -----
Enter merchant name: Rayudu
Available banks and branches:
HDFC Bank (HDFC):
  - Mumbai Branch (IFSC: HDFC0001)
  - Delhi Branch (IFSC: HDFC0002)
  - Bangalore Branch (IFSC: HDFC0003)
ICICI Bank (ICICI):
  - Mumbai Branch (IFSC: ICIC0001)
  - Delhi Branch (IFSC: ICIC0002)
  - Bangalore Branch (IFSC: ICIC0003)
State Bank of India (SBI):
  - Mumbai Branch (IFSC: SBIN0001)
  - Delhi Branch (IFSC: SBIN0002)
  - Bangalore Branch (IFSC: SBIN0003)
Enter IFSC code: HDFC0002
Enter password: nithi2345
Enter initial account balance: 100000
Blockchain data saved successfully
Data saved successfully
Merchant registered successfully!
Merchant ID: 7664d3cf409c94cd
```

### Merchant Side (UPI Machine)
1. Start the UPI Machine
2. Select option to generate a QR code
3. Enter merchant ID (e.g., "29587d3c346a5fef" for Nithin)
4. A QR code will be generated and displayed

### User Side (User Client)
1. Start the User Client
2. Log in with MMID and PIN (e.g., "23dfa5ca02f77c4e" and "1678" for the newly created user)
3. Select option to scan QR code and make payment
4. Enter the QR code data (displayed on UPI Machine)
5. Enter payment amount
6. Optionally choose to simulate a quantum attack
7. Confirm the transaction

### Pre-configured Accounts

#### Users
- **Pavan**: SBI account with a balance of ₹571,210 (MMID: 21eb5a5459c694a0, PIN: 2476)
- **Veeresh**: ICICI account with a balance of ₹8,522 (MMID: 714c0cffbf20cd66, PIN: 5430)

#### Merchants
- **Nithin**: HDFC account with a balance of ₹50,013,378 (MID: 29587d3c346a5fef)
- **Abhi**: ICICI account with a balance of ₹203,037,629 (MID: 85cf1c60d850a8ca)

## Security Features
The system implements several advanced security features:
- **SHA-256 Hashing**: Used for generating merchant IDs (MIDs), user IDs (UIDs), and mobile money IDs (MMIDs).
- **SPECK Encryption**: A lightweight block cipher implemented for encrypting QR code data.
- **Blockchain Ledger**: All transactions are recorded in an immutable blockchain, providing an audit trail and ensuring transaction integrity.
- **Simulated Quantum Attack**: The system includes a simulation of how quantum computing might threaten traditional PIN security.

## Code Structure
The project is organized with a modular architecture as follows:
```
├── blockchain.py           # Blockchain implementation for transaction ledger
├── common_utils.py         # Shared utilities and cryptographic functions
├── main.py                 # Main entry point for starting components
├── merchants.json          # Merchant database
├── network_config.json     # Network configuration
├── README.md               # Project documentation
├── setup_firewall.bat      # Windows firewall configuration script
├── shared_data.py          # Data synchronization between components
├── users.json              # User database
│
├── bank_server/            # Bank server implementation
│   └── bank_server.py      # Bank component implementation
│
├── blockchain_data/        # Blockchain ledgers for each bank
│   ├── HDFC_blockchain.json
│   ├── ICICI_blockchain.json
│   └── SBI_blockchain.json
│
├── qr_codes/               # Generated QR codes for merchants
│
├── transaction_history/    # Exported transaction records
│
├── upi_machine/            # UPI machine implementation
│   └── upi_machine.py      # Merchant terminal component
│
└── user_client/            # User client implementation
    └── user_client.py      # Mobile app simulation component
```

### Core Components
**Blockchain Implementation (blockchain.py):**
- Implements Block and Blockchain classes
- Provides methods for adding transactions, validating chain integrity
- Maintains immutable transaction records

**Cryptographic Utilities (common_utils.py):**
- SPECK encryption algorithm for lightweight cryptography
- SHA-256 hashing for generating IDs
- QR code generation and processing
- Quantum attack simulation

**Data Synchronization (shared_data.py):**
- Enables data sharing between distributed components
- Provides a DataSyncServer for cross-device communication

**Component Implementation:**
- bank_server.py: Implements the central authority
- upi_machine.py: Handles merchant QR code generation
- user_client.py: Provides user interface for making payments

## Transaction Management

### Viewing Transaction History
The system allows for viewing transaction history with various filtering options:
```
===== Bank Terminal =====
Enter your choice (1-10): 8
----- View Transaction History -----
Filter options:
1. View all transactions
2. Filter by bank
3. Filter by user
4. Filter by merchant
Enter your choice (1-4): 1
Found 2 transactions.
Display options:
1. Display all transactions
2. Display and save
Enter your choice (1-2): 2
----- Transaction History -----
ID              Date/Time            From            To              Amount       Bank
------------------------------------------------------------------------------------------
44cabdf0cbf7    2025-04-09 15:47:55  44cabdf0cbf7    85cf1c60d850    ₹45.00       ICICI
44cabdf0cbf7    2025-04-05 13:42:24  44cabdf0cbf7    29587d3c346a    ₹678.00      HDFC
For more details on a specific transaction, use the 'get_user_transactions' or 'get_merchant_transactions' commands.
Transaction history successfully saved to transaction_history/transaction_history_20250411_220230.json
```

### Transaction Filtering
You can filter transactions by:
- **Bank**: View transactions processed by a specific bank
- **User**: View all transactions made by a specific user
- **Merchant**: View all transactions received by a specific merchant

Example of filtering by bank:
```
----- View Transaction History -----
Filter options:
1. View all transactions
2. Filter by bank
3. Filter by user
4. Filter by merchant
Enter your choice (1-4): 2
Select a bank:
1. HDFC Bank
2. ICICI Bank
3. SBI Bank
Enter your choice (1-3): 1
Found 1 transactions.
Display options:
1. Display all transactions
2. Display and save
Enter your choice (1-2): 2
```

### Transaction Storage
Transactions are stored in JSON format in the transaction_history directory. Each transaction contains the following information:
```json
[
  {
    "transaction_id": "44cabdf0cbf7744e_85cf1c60d850a8ca_1744193875.1049576",
    "from_user": "44cabdf0cbf7744e",
    "to_merchant": "85cf1c60d850a8ca",
    "amount": 45.0,
    "timestamp": 1744193875.1049576,
    "user_bank": "ICICI",
    "merchant_bank": "ICICI",
    "bank": "ICICI"
  },
  {
    "transaction_id": "44cabdf0cbf7744e_29587d3c346a5fef_1743840744.448654",
    "from_user": "44cabdf0cbf7744e",
    "to_merchant": "29587d3c346a5fef",
    "amount": 678.0,
    "timestamp": 1743840744.448654,
    "user_bank": "ICICI",
    "merchant_bank": "HDFC",
    "bank": "HDFC"
  }
]
```

### Timestamp Format
Transactions use Unix timestamp format (seconds since January 1, 1970). To convert this to a human-readable format:
- Python: `datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')`
- JavaScript: `new Date(timestamp * 1000).toISOString()`

For example, the timestamp 1744193875.1049576 converts to 2025-04-09 15:47:55.

## Technical Implementation Details

### Blockchain Implementation
The blockchain implementation in blockchain.py consists of:

**Block Class**: Represents individual blocks containing transaction data
- Contains transaction details, timestamp, previous hash, and current hash
- Implements hash calculation using SHA-256
- Provides serialization for storage and reconstruction

**Blockchain Class**: Manages the chain of blocks
- Adds transactions with proper linking between blocks
- Validates chain integrity by verifying hash sequences
- Reconstructs chains from serialized data
- Provides transaction filtering by user, merchant, or bank

Each bank maintains its own blockchain ledger, ensuring transactions are properly recorded across different banking entities. When a transaction occurs between banks, the transaction is recorded in both blockchains, maintaining a complete audit trail.

### SPECK Cipher Implementation
The system implements the SPECK lightweight block cipher in common_utils.py for encrypting sensitive data:

```python
class SPECK:
    """
    SPECK is a family of lightweight block ciphers.
    This is a simplified version for demonstration purposes.
    """
    def __init__(self, key):
        self.key = key.ljust(16, '0')[:16].encode()  # Ensure 16-byte key
        
    def encrypt(self, text):
        # Implementation of SPECK encryption algorithm
        # ...
    
    def decrypt(self, cipher_text):
        # Implementation of SPECK decryption algorithm
        # ...
```

- Provides a good balance between security and performance
- Operates on 32-bit words with a 128-bit key
- Uses simple operations: word rotation, XOR, and modular addition
- Encrypts merchant information in QR codes

### Quantum Attack Simulation
The simulate_quantum_attack function demonstrates how quantum computing could potentially break traditional PIN security:

```python
def simulate_quantum_attack(pin, uid):
    """
    Simulate a quantum computing attack on PIN and UID
    This is just a demonstration and not a real quantum attack
    """
    print(f"Simulating quantum attack on user credentials...")
    print(f"Target PIN length: {len(str(pin))} digits")
    print(f"Target UID: {uid}")
    
    # Simulate attack timing and success probability
    # ...
```

The simulation demonstrates the vulnerability of numeric PINs to quantum computing algorithms like Shor's algorithm, highlighting the need for quantum-resistant cryptography in financial systems.

## Project Status
The project has been successfully implemented with all key features functional:
- Three-component architecture
- Blockchain implementation
- SHA-256 hashing
- SPECK encryption
- QR code generation and scanning
- Quantum attack simulation

## Future Enhancements
- Implement post-quantum cryptography to address vulnerabilities
- Add multi-signature verification for enhanced security
- Develop a mobile application interface
- Implement biometric authentication
- Add support for recurring payments

## Contributors
This project was developed by Group 27 for the Cryptography (BITS F463) course at BITS Pilani.

**Team Members:**
- Naga Siva Nithin Kota
- Pavan Sai Pasala
- Omkar Basani
- Sree Kaushik
- Vamshi Krishna Manchala
