class task():
    def __init__(self,gas,size,id):
        self.gas = gas
        self.size = size
        self.id = id
        self.type = 1
    
    def __repr__(self):
        return self.id