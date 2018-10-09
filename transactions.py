import time

class Transaction():
    '''
    Arguments:
    1. gas: gas of the transaction
    2. size: size of the transaction
    3. id: global id of the transaction
    4. type: 1 for transaction
    5. gen_time: Timestamp when the transaction was generated
    TODO: (Not used till now)
    6. appended_time: Time when it was appended to a node
    7. blocked_time: Time when the transaction was added to the blockchain
    '''
    def __init__(self,gas,size,id):
        self.gas = gas
        self.size = size
        self.id = id
        self.type = 1
        self.gen_time = time.ctime()
        self.appended_time = None
        self.blocked_time = None
    
    def __repr__(self):
        return str(self.id)