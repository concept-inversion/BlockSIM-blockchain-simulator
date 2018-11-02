import hashlib
import time

class Block():
    def __init__(self,size,id,transactions,node,prev_hash):
        '''
        Arguments:
        1. Size: Sum of size of every transactions
        2. id: Global ID of the block
        3. transactions: a list of transaction
        4. node: ID of node which generated this block
        5. prev_hash: hash of previous block of a node's blockchain which created this block
        '''
        self.size = size
        self.hash = self.hash_generator(transactions)
        self.prev_hash=prev_hash 
        self.type = 2
        self.generated_by= node
        self.id= id
        self.transactions= transactions
        self.timestamp= time.ctime() 
    
    def __repr__(self):
        return str(self.id)

    def hash_generator(self,tasks):
        '''
        Generate a hash for a block when blocks are formed.
        https://stackoverflow.com/questions/20416468/fastest-way-to-get-a-hash-from-a-list-in-python
        '''
        # list comprehension for generating hash
        re = [(each.id) for each in tasks ]
        # Transaction are always sorted based on transaction id to ensure that the order of transaction do not hamper the hash.
        re.sort()
        # Create a string of transaction id
        p = ','.join(map(str, re)).encode('utf-8')
        # Return the hash
        return (hashlib.md5(p).hexdigest())

    def validator(self,tasks):
        '''
        It validates if a block and a list of transaction generate same hash or not.
        TODO: Add complete validation
        '''
        # create hash of transactions
        tnx_hash=self.hash_generator(tasks)
        # check it with the block hash
        if tnx_hash==self.hash:
            return True
        else:
            return False
    
    def view_blocks(self):  
        '''
        Function to display the blocks with block id and transactions contained in it.
        '''
        print(self.id)
        print(self.transactions)
        
        
        