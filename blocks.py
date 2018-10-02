import hashlib
import time

class Block():
    def __init__(self,size,id,transactions,node):
        self.size = size
        self.hash = self.hash_generator(transactions)
        self.type = 2
        self.generated_by= node
        self.id= id
        self.transactions= transactions
        self.timestamp= time.ctime() 
    
    def __repr__(self):
        return str(self.id)

    def hash_generator(self,tasks):
        '''
        https://stackoverflow.com/questions/20416468/fastest-way-to-get-a-hash-from-a-list-in-python
        '''
        # list comprehension for generating hash
        r = [(each.id) for each in tasks ]
        p = ','.join(map(str, r)).encode('utf-8')
        self.hash=hashlib.md5(p).hexdigest()
         
        pass

    def validator(self,tasks):
        # create hash of transactions
        tnx_hash=self.hash_generator(tasks)
        # check it with the block hash
        if tnx_hash==self.hash:
            return True
        else:
            return False
    
    def view_blocks(self):
        print(self.id)
        print(self.transactions)
        
        
        