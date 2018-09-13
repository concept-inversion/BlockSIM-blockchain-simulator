import random
import simpy

NO_NODES = 1
MEAN_TRANS_GEN_TIME= 4
SD_TRANS_GEN_TIME= 1 
MINING_TIME= 2
BLOCKSIZE= 5
MEMPOOL_SIZE= 10

class nodes():
    def __init__(self,nodeID):
        self.nodeID= nodeID
        self.env= env
        self.task_list = []
        self.mempool_size = 10
        self.block_list= []
        print("Node generated with node ID: %d " % self.nodeID)
        
        
    def run(self):
        yield env.timeout(5)
        print("Running node id %d at time %d"% (self.nodeID,env.now))
    def add_task(self,txID):
        self.task_list.append(txID)
        #print("task number %d added to the node %d " %(txID,self.nodeID))
        env.process(self.mining())

    def broadcast(self):
        pass
    
    def mining(self):
        # Starts mining/verification of the transactions and handles interrupt for updating the blocks
        task=self.task_list.pop()
        print("Miner started for task %d at node %d at time %d " % (task, self.nodeID,env.now))
        yield env.timeout(13)
        print("task %d done by node %d in time %d" %(task,self.nodeID,env.now))
        
def node_generator(env):
    global nodeID
    nodeID= random.sample(range(1000,1000+NO_NODES),NO_NODES)
    global node_map
    node_map = [nodes(each) for each in nodeID]
    #import ipdb; ipdb.set_trace()
    print("%d nodes generated:"% NO_NODES)

def trans_generator(env):
    txID = 2300
    while True:
        yield env.timeout(random.gauss(MEAN_TRANS_GEN_TIME,SD_TRANS_GEN_TIME))
        txID  += 1
        print("Generating %d transactions at %d tick."% (txID,env.now))
        node = random.choice(nodeID)
        #import ipdb; ipdb.set_trace()
        for i in node_map:
            if i.nodeID==node:
                i.add_task(txID)
                #print("Transaction %d appended to the node %d : "%(txID,i.nodeID))
        yield env.timeout(5)

env = simpy.Environment()
node_generator(env)

env.process(trans_generator(env))
env.run(until=50)

