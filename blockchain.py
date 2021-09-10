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
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    
    
    
    
    
    
    
    
# Mine the block