# Module 1 - Creation of blockchain

# Imports 
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# build the chain

class Blockchain:
    # make the "chain" and the genesis block
    def __init__(self):
        self.chain = []
        # make the empty list of transactions first! or the block wont have 
        # access to them before it is created
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    # creates a new block and adds it to the chain
    def create_block(self, proof, previous_hash):
        # you can add a data field and as many others as you want to the chain
        block = { 'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactins' : self.transactions }
        # after transactions are added to block, make them empty again
        self.transactions = []
        #adds the block to the end of the chain
        self.chain.append(block)
        #return the new block that was just added
        return block

    # returns the last block in the "chain"
    def get_previous_block(self):
        return self.chain[-1]
    
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # make a problem to solve 
            # dont add because it would be the same if you reverse the numbers
            proof_combo = new_proof**2 - previous_proof**2
            hash_operation = hashlib.sha256(str(proof_combo).encode()).hexdigest()
            # this checks the index of 0 - 3 (given index is not included)
            if hash_operation[:4] == '0000' :
                check_proof = True
            else:
                new_proof += 1             
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            #make sure the blocks 'previous_hash' matches the previous blocks hash
            #this is what makes sure the chain is intack 
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            # double check that the hash is valid 
            if hash_operation[:4] != '0000':
                return False
            #update the blocks that we are checking
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction (self, sender, reciever, amount):
        self.transactions.append({'sender' : sender,
                                  'reciever' : reciever,
                                  'amount' : amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node (self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain (self):
        network = self.nodes #all nodes that have the chain 
        longest_chain = None #will get updates in loop
        max_length = len(self.chain) #allows compare of chain in nodes
        for node in network:
            response = requests.get(f'http://{node}/get_full_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain: #only has a value when we need to update chain
            self.chain = longest_chain
            return True
        return False
    
# Module 2 Mining the blockchain

# Create the web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create addresses for the nodes
node_address = str(uuid4()).replace('-', '')

# Create the Blockchain
blockchain = Blockchain()

# Mine a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    #first we need the previous block
    previous_block = blockchain.get_previous_block()
    #now we can get the preious proof
    previous_proof = previous_block['proof']
    #with this we can get the proof of work
    proof = blockchain.proof_of_work(previous_proof)
    #now we that we have the new proof we can start hashing
    previous_hash = blockchain.hash(previous_block)
    #include the transaction, give to the miner
    blockchain.add_transaction(node_address, 'Jacob', 1)
    #with the new hash we can create a new block that now has the previous hash
    new_block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Mine is complete',
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'proof': new_block['proof'],
                'previous_hash': new_block['previous_hash'],
                'transactions': new_block['transactions']}
    return jsonify(response), 200


# Get the full chain
@app.route('/get_full_chain', methods = ['GET'])
def get_full_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# validate the chain
@app.route('/validate_chain', methods = ['GET'])
def validate_chain():
    response = {'is_valid': blockchain.is_chain_valid(blockchain.chain)}
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Error: missing elements in transacion', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

# Decentralize the chain

# connectint new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No nodes", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Nodes are connected',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# replace with most up to date chain
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_raplaced = {'replace_chain_needed': blockchain.replace_chain()}
    if is_chain_raplaced:
        response = {'message': 'Chain was replaced with longest chain'}
    else:
        response = {'message': 'Chain was the longest, it stayed the same'}
    return jsonify(response), 200



# Run the App
app.run(host = '0.0.0.0', port = 5002)











