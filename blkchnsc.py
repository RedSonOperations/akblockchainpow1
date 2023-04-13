# Import necessary libraries
import hashlib
import json
import time
from flask import Flask, jsonify, redirect, request, render_template

# Define the Block class
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Hashes the block's data using SHA-256 algorithm
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + json.dumps(self.data) + str(self.previous_hash) + str(self.nonce)).encode('utf-8'))
        return sha.hexdigest()

    def mine_block(self, difficulty, reward_address):
        # Mines the block by finding a hash with a certain number of leading zeros
        target = "0" * difficulty
        reward = 0.01  # Reward for mining a block (in cents)
        reward_transaction = {
            "from": "Mining Reward",
            "to": reward_address,
            "amount": reward
        }
        self.data.append(reward_transaction)
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self):
        """Convert block attributes to a dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
# Define the Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # Difficulty level for mining
        self.pending_transactions = []

    def create_genesis_block(self):
        # Creates the first block (genesis block) in the chain
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        # Returns the latest block in the chain
        return self.chain[-1]

    def add_transaction(self, transaction):
        # Adds a transaction to the list of pending transactions
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_reward_address):
        # Mines the pending transactions and adds a new block to the chain
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty, miner_reward_address)
        self.chain.append(new_block)
        self.pending_transactions = []

    def is_chain_valid(self):
        # Checks if the blockchain is valid by verifying the hashes and previous hash of each block
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash() or current_block.previous_hash != previous_block.hash:
                return False
        return True
    
    def get_all_transactions(self):
        # Returns a list of all transactions in the blockchain
        transactions = []
        for block in self.chain:
            transactions.extend(block.data)
        return transactions
    
# Create Flask app
app = Flask(__name__)

# Create instance of Blockchain class
my_chain = Blockchain()

# Define API endpoints
@app.route('/mine', methods=['GET'])
def mine_block():
    # Mine a new block and add it to the blockchain
    my_chain.mine_pending_transactions("Miner Reward Address")
    response = {
        'message': 'Block mined and added to the blockchain',
        'block': {
            'index': my_chain.get_latest_block().index,
            'timestamp': my_chain.get_latest_block().timestamp,
            'data': my_chain.get_latest_block().data,
            'previous_hash': my_chain.get_latest_block().previous_hash,
            'hash': my_chain.get_latest_block().hash,
            'nonce': my_chain.get_latest_block().nonce
            }
        }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
# Add a new transaction to the list of pending transactions
    transaction = request.get_json()  # Get transaction data from POST request
    if transaction is None:
        return "Transaction data is missing", 400

    required_fields = ['sender', 'recipient', 'amount']
    if not all(field in transaction for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    sender = transaction['sender']  # Custom sender field
    recipient = transaction['recipient']  # Custom recipient field
    amount = transaction['amount']

    # Create a transaction dictionary with custom sender and recipient fields
    new_transaction = {
        'from': sender,
        'to': recipient,
        'amount': amount
    }
    my_chain.add_transaction(transaction)
    return 'Transaction added to pending transactions', 201

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({'chain': [block.to_dict() for block in my_chain.chain]})

@app.route('/is_valid', methods=['GET'])
def is_valid():
# Check if the blockchain is valid
    is_valid = my_chain.is_chain_valid()
    if is_valid:
        response = {'message': 'The blockchain is valid'}
    else:
        response = {'message': 'The blockchain is not valid'}
    return jsonify(response), 200

@app.route('/transactions', methods=['GET'])
def get_all_transactions():
    transactions = my_chain.get_all_transactions()
    return jsonify(transactions), 200

@app.route('/', methods=['GET'])
def home():
    # Render the HTML file
    return render_template('index.html')

#Run the Flask app

if __name__ == '__main__':
    app.run(debug=True)
