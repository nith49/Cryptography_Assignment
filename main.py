"""
Main execution script for UPI Payment Gateway System
"""

import os
import socket
import sys
import time
import threading
import argparse
import json

def setup_directories():
    """Create necessary directories if they don't exist"""
    # Create directories for each component
    components = ['bank_server', 'upi_machine', 'user_client']
    for component in components:
        if not os.path.exists(component):
            os.makedirs(component)
    
    # Create __init__.py files for Python package imports
    for component in components:
        init_file = os.path.join(component, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Package initialization file\n')

# Setup directories before imports
setup_directories()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_network_config(component, host):
    """Update network configuration with the provided host IP"""
    config_file = 'network_config.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Create default config if it doesn't exist
        config = {
            "bank_server": {"host": "127.0.0.1", "port": 5001},
            "upi_machine": {"host": "127.0.0.1", "port": 5002},
            "user_client": {"host": "127.0.0.1", "port": 5003}
        }
    
    # Update the component's host
    if component == 'bank':
        config["bank_server"]["host"] = host
    elif component == 'upi':
        config["upi_machine"]["host"] = host
    elif component == 'user':
        config["user_client"]["host"] = host
    
    # Save updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Updated network configuration: {component} -> {host}")
    return config

def start_bank_server(host):
    """Start bank server"""
    # Update network configuration
    config = update_network_config('bank', host)
    
    # Import common utils
    import common_utils
    
    # Update common utils with configuration
    common_utils.BANK_SERVER_HOST = host
    common_utils.HOST = host
    
    print(f"Starting Bank Server on {host}:{common_utils.PORT_BANK}")
    
    # Import here to use updated HOST value
    from bank_server import BankServer
    
    # Create new server socket with proper binding
    bank_server = BankServer()
    bank_server.server_socket.close()
    bank_server.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bank_server.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to all interfaces for incoming connections
    bank_server.server_socket.bind(('0.0.0.0', common_utils.PORT_BANK))
    bank_server.server_socket.listen(5)
    
    # Start the server
    print(f"Bank Server ready to accept connections on {host}:{common_utils.PORT_BANK}")
    bank_server.start()

def start_upi_machine(host):
    """Start UPI machine"""
    # Update network configuration
    config = update_network_config('upi', host)
    
    # Import common utils
    import common_utils
    
    # Update common utils with configuration
    common_utils.UPI_MACHINE_HOST = host
    common_utils.HOST = host
    
    print(f"Starting UPI Machine on {host}:{common_utils.PORT_UPI_MACHINE}")
    
    # Import here to use updated HOST value
    from upi_machine import UPIMachine
    
    # Create UPI machine with proper binding
    upi_machine = UPIMachine()
    upi_machine.server_socket.close()
    upi_machine.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upi_machine.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to all interfaces for incoming connections
    upi_machine.server_socket.bind(('0.0.0.0', common_utils.PORT_UPI_MACHINE))
    upi_machine.server_socket.listen(5)
    
    # Start the UPI machine
    print(f"UPI Machine ready to accept connections on {host}:{common_utils.PORT_UPI_MACHINE}")
    upi_machine.start()

def start_user_client(host):
    """Start user client"""
    # Update network configuration
    config = update_network_config('user', host)
    
    # Import common utils
    import common_utils
    
    # Update common utils with configuration
    common_utils.USER_CLIENT_HOST = host
    common_utils.HOST = host
    
    print(f"Starting User Client on {host}:{common_utils.PORT_USER}")
    
    # Import here to use updated HOST value
    from user_client import UserClient
    
    # Create user client
    user_client = UserClient()
    
    # Start the client
    print(f"User Client started on {host}:{common_utils.PORT_USER}")
    user_client.start()

def test_connection(host, port, description):
    """Test connection to a server"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((host, port))
            print(f"✅ Connection to {description} at {host}:{port} successful!")
            return True
    except Exception as e:
        print(f"❌ Connection to {description} at {host}:{port} failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start UPI Payment Gateway System components')
    parser.add_argument('component', choices=['bank', 'upi', 'user'], 
                        help='Component to start (bank, upi, or user)')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host address of this component (default: 127.0.0.1)')
    parser.add_argument('--bank-host', default=None,
                        help='Host address of the Bank Server (for UPI/User components)')
    parser.add_argument('--upi-host', default=None,
                        help='Host address of the UPI Machine (for User component)')
    parser.add_argument('--test', action='store_true',
                        help='Test connections to other components')
    
    args = parser.parse_args()
    
    # Update network configuration with explicit hosts if provided
    if args.bank_host:
        update_network_config('bank', args.bank_host)
    if args.upi_host:
        update_network_config('upi', args.upi_host)
    
    # Test connections if requested
    if args.test:
        # Import config here
        import importlib
        import common_utils
        # Reload to get latest config
        common_utils = importlib.reload(common_utils)
        
        if args.component != 'bank':
            test_connection(common_utils.BANK_SERVER_HOST, common_utils.PORT_BANK, "Bank Server")
        
        if args.component == 'user':
            test_connection(common_utils.UPI_MACHINE_HOST, common_utils.PORT_UPI_MACHINE, "UPI Machine")
    
    # Start the selected component
    if args.component == 'bank':
        start_bank_server(args.host)
    elif args.component == 'upi':
        start_upi_machine(args.host)
    elif args.component == 'user':
        start_user_client(args.host)
    else:
        print(f"Unknown component: {args.component}")
        print("Choose one of: bank, upi, user")
        sys.exit(1)