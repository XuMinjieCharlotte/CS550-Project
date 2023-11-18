import hashlib
import base58
import os
import socket
from transaction import Transaction

class Transaction:
    def __init__(self, sender_address, recipient_address, value, timestamp, transaction_id, signature):
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.value = value
        self.timestamp = timestamp
        self.transaction_id = transaction_id
        self.signature = signature
    
    def serialize(self):
        # Serialize the transaction object into bytes
        transaction_data = struct.pack('32s32sdbl16s32s',
                                       self.sender_address,
                                       self.recipient_address,
                                       self.value,
                                       self.timestamp,
                                       self.transaction_id,
                                       self.signature)
        return transaction_data
    
    @classmethod
    def deserialize(cls, data):
        # Deserialize the bytes into a transaction object
        transaction_fields = struct.unpack('32s32sdbl16s32s', data)
        transaction = cls(*transaction_fields)
        return transaction

class Block:
    def __init__(self, block_size, version, previous_block_hash, block_id, timestamp, difficulty_target, nonce, transactions):
        self.block_size = block_size
        self.version = version
        self.previous_block_hash = previous_block_hash
        self.block_id = block_id
        self.timestamp = timestamp
        self.difficulty_target = difficulty_target
        self.nonce = nonce
        self.transactions = transactions
    
    def serialize(self):
        # Serialize the block object into bytes
        block_header = struct.pack('I56s', self.version, self.previous_block_hash)
        block_data = struct.pack('I', self.block_size) + block_header
        block_data += struct.pack('IqHQB64s', self.block_id, self.timestamp, self.difficulty_target, self.nonce, 0, b'')
        
        for transaction in self.transactions:
            block_data += transaction.serialize()
        
        return block_data
    
    @classmethod
    def deserialize(cls, data):
        # Deserialize the bytes into a block object
        block_size = struct.unpack('I', data[:4])[0]
        version, previous_block_hash = struct.unpack('I56s', data[4:60])
        block_id, timestamp, difficulty_target, nonce = struct.unpack('IqHQB', data[60:81])
        
        transactions_data = data[81:]
        transactions = []
        transaction_size = 128
        for i in range(block_size):
            transaction_data = transactions_data[i * transaction_size: (i + 1) * transaction_size]
            transaction = Transaction.deserialize(transaction_data)
            transactions.append(transaction)
        
        block = cls(block_size, version, previous_block_hash, block_id, timestamp, difficulty_target, nonce, transactions)
        return block




def create_wallet():
    # Implementation to create a wallet
     # Generate a random 256-bit private key
    private_key = os.urandom(32)

    # Calculate the corresponding public key using SHA256
    public_key = hashlib.sha256(private_key).digest()

    # Encode the keys in Base58 format
    encoded_private_key = base58.b58encode(private_key)
    encoded_public_key = base58.b58encode(public_key)

    # Create a dictionary to store the keys
    wallet = {
        'public_key': encoded_public_key,
        'private_key': encoded_private_key
    }

    return wallet


def send_transaction():
    # Gather inputs for the transaction
    sender_address = input("Enter sender's public address: ")
    recipient_address = input("Enter recipient's public address: ")
    value = float(input("Enter value: "))
    timestamp = int(input("Enter timestamp: "))
    transaction_id = input("Enter transaction ID: ")
    signature = input("Enter signature: ")

    # Create a Transaction object
    transaction = Transaction(sender_address, recipient_address, value, timestamp, transaction_id, signature)

    # Serialize the Transaction object into bytes
    transaction_data = transaction.serialize()

    # Establish a socket connection with the desired component
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.connect(('component_ip', component_port))

    # Send the transaction data over the socket connection
    socket_connection.send(transaction_data)

    # Receive a response or acknowledgment from the component
    response = socket_connection.recv(1024)
    # Process the response here

    socket_connection.close()

def view_balance():
    # Implementation to view balance
    if os.path.isfile(WALLET_FILE):
        with open(WALLET_FILE, 'r') as file:
            for line in file:
                if line.startswith('balance'):
                    balance = int(line.split(':')[1].strip())
                    print(f"Balance: {balance} coins")
                    return
    else:
        print("Wallet does not exist.")

# Establish a socket connection with the desired component
wallet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
wallet_socket.connect(('component_ip', component_port))

import struct



while True:
    # User interaction or programmatically trigger actions
    action = input("Enter action (create/send/view): ")

    if action == "create":
        create_wallet()
        # Store the keys in a configuration file
        # save the key to the wallet.cfg
        with open('wallet.cfg', 'w') as file:
            file.write(f"public_key: {wallet['public_key'].decode()}\n")
            file.write(f"private_key: {wallet['private_key'].decode()}\n")
        print("Wallet created and keys stored in wallet.cfg.")

        # Send a message to the component to create a wallet
        wallet_socket.send(b'CREATE_WALLET')

    elif action == "send":
        send_transaction()
        # Send a message to the component to send a transaction
        wallet_socket.send(b'SEND_TRANSACTION')

    elif action == "view":
        view_balance()
        # Send a message to the component to view balance
        wallet_socket.send(b'VIEW_BALANCE')

    # Receive and process the response from the component
    response = wallet_socket.recv(1024)
    # Process the response here

wallet_socket.close()