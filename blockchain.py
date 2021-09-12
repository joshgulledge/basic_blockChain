# Module 1 - Creation of blockchain

# Imports 
import datetime
import hashlib
import json
from flask import Flask, jsonify


# build the chain

class Blockchain:
    # make the "chain" and the genesis block
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    # creates a new block and adds it to the chain
    def create_block(self, proof, previous_hash):
        # you can add a data field and as many others as you want to the chain
        block = { 'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash }
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
    
    
# Module 2 Mining the blockchain

# Create the web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
    #with the new hash we can create a new block that now has the previous hash
    new_block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Mine is complete',
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'proof': new_block['proof'],
                'previous_hash': new_block['previous_hash']}
    return jsonify(response), 200


# Get the full chain
@app.route('/get_full_chain', methods = ['GET'])
def get_full_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Run the App
app.run(host = '0.0.0.0', port = 5000)











