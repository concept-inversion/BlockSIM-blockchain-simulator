import hashlib

class block():
    def __init__(self,gas,size,id):
        self.size = size
        self.hash = None
        self.type = 2
        self.generated_by= None
    
    def __repr__(self):
        return self.hash

    def hash_generator(self,tasks):
        '''
        https://stackoverflow.com/questions/20416468/fastest-way-to-get-a-hash-from-a-list-in-python
        '''
        r = [(each.id) for each in tasks ]
        p = ','.join(map(str, r)).encode('utf-8')
        print("hash is: ")
        print(hashlib.md5(p).hexdigest())
        # list comprehension for generating hash 
        pass

    def validator(self):
        # create hash of transactions
        # check it with the block hash
        pass