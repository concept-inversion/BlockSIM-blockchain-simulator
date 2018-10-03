import random
import time
import simpy
import logging
import copy
import numpy as np
import pandas as pd
from tasks import task
from blocks import Block

NO_NODES = 10
MEAN_TRANS_GEN_TIME= 2
SD_TRANS_GEN_TIME= 0.5
MINING_TIME= 2
BLOCKSIZE= 5
txpool_SIZE= 10
BLOCKTIME = 20
logging.basicConfig(filename='logs/blockchain.csv',level=logging.DEBUG)
logger = logging.getLogger()
curr = time.ctime()
#logger.info("-----------------------------------Start of the new Session at %s-------------------------------"%curr)
BLOCKID= 99900
class nodes():
    
    def __init__(self,nodeID,cable):
        self.nodeID= nodeID
        self.env= env
        self.txpool= []
        self.pendingpool = []
        self.block_gas_limit = 5000 
        self.block_list= []
        self.cable= cable
        self.current_gas=0
        self.current_size=0
        self.res= simpy.Resource(env,capacity=1)
        self.mine_process = env.process(self.mining())
        print("Node generated with node ID: %d " % self.nodeID)
        #logger.debug('%d , generated, %d'%(self.nodeID,env.now))
    
    def add_task(self,tx):
        self.broadcaster(tx,None,0)
        self.txpool.append(tx)
        #logger.debug('%d , Tx incoming, %d'%(self.nodeID,env.now))
    
    '''
     type= 0 :transactions
     type= 1 :blocks
    '''

    def receiver(self,data,type):
        #If it is a transaction, add it to the pool; Later on verify if the tx has already happened
        print("%d received data at %d"%(self.nodeID,self.env.now))
        if type==0:
            self.txpool.append(data)
        elif type==1:
            self.intr_data= data
            self.mine_process.interrupt()
        pass

    def broadcaster(self,data,nodeID,type):
        # Broadcast to neighbour node. For now, broadcast to all.
        print("%d broadcasting data to other nodes"%self.nodeID)
        #logger.debug('%d , broadcasting, %d'%(self.nodeID,env.now))
        def propagation(delay,each,data,type): 
            yield self.env.timeout(latency)
            each.receiver(data,type)

        for each in node_map:
            if each.nodeID != self.nodeID:                
                #insert delay using nodemap
                latency = node_network.loc[self.nodeID,each.nodeID]
                self.env.process(propagation(latency,each,data,type))
                 
        pass

    def mining(self):
        '''
         Starts mining/verification of the transactions and handles interrupt for updating the blocks.
         1. Add task send interrupts to this process.
         2. After INTR, it sums the gas size.
         3. Check if the gas size is out of limit.
         4. If out of limit, hold the last task,builds a block with tx in the pool, and broadcasts it.
         
        '''
    
        while True:
            try:
                yield env.timeout(1)   
                if len(self.txpool) != 0:
                    for each_tx in self.txpool:
                        self.current_gas += each_tx.gas
                        self.current_size = each_tx.size
                        if self.current_gas < self.block_gas_limit:
                            self.pendingpool.append(self.txpool.pop(0))
                            #print("added task to the pending pool")
                        
                        else:
                            print("%d Create a block" %self.nodeID)
                            #logger.debug('%d , Creating block, %d'%(self.nodeID,env.now))
                            global BLOCKID
                            BLOCKID+= 1
                            # could this pass for pending pool be pass by refere3nce ? 
                            block = Block(self.current_size,BLOCKID,self.pendingpool,self.nodeID) 
                            print("The created block is: ")
                            print(block)
                            self.block_list.insert(0,block)
                            print("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
                            self.broadcaster(block,self.nodeID,1)
                            self.current_gas=0
                            self.current_size=0
                            self.pendingpool=[]
            except simpy.Interrupt:
                print("%d is interrupted " %self.nodeID)
                #logger.debug('%d , Interrupted, %d'%(self.nodeID,env.now))
                # use this for verification
                '''
                #verify here
                #print("hash of tx is")
                check=self.intr_data.validator(self.pendingpool)
                if check == True:
                    print("block match")
                '''
                self.block_list.insert(0,self.intr_data)
                print("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
                self.txpool=[]
                self.intr_data=None
                self.current_gas=0

                #     request = self.res.request()
                #     yield request
                #     self.cable.put(task,self.nodeID)
                #     self.block_list.append(task)
                #     self.res.release(request)
               


def node_generator(env,cable):
    global nodeID
    nodeID= random.sample(range(1000,1000+NO_NODES),NO_NODES)
    global node_map
    node_map = [nodes(each,cable) for each in nodeID]
    #import ipdb; ipdb.set_trace()
    print("%d nodes generated:"% NO_NODES)
    network_creator()

def network_creator():
    dimension= len(nodeID)
    np.random.seed(7)
    x=np.random.randint(20, size=(dimension, dimension))
    global node_network
    node_network= pd.DataFrame(x,columns=nodeID,index=nodeID)
    print(node_network)
       
def trans_generator(env):
    global txID
    txID = 2300
    while True:
        TX_SIZE = random.randint(2300,4000)
        TX_GAS = random.randint(1000,2000)
        yield env.timeout(random.gauss(MEAN_TRANS_GEN_TIME,SD_TRANS_GEN_TIME))
        txID  += 1
        print("Generating |  %d  | time %d ."% (txID,env.now))
        #logger.debug("Generating |  %d  | time %d ."% (txID,env.now))
        Task = task(TX_GAS,TX_SIZE,txID)
        # Choose a node randomly from the nodelist
        node = random.choice(nodeID)
        # Assign the task to the node; Find the node object with the nodeID
        for i in node_map:
            if i.nodeID==node:
                i.add_task(Task)
                print("Transaction %d appended to the node %d : "%(txID,i.nodeID))

class Network():
    def __init__(self, env):
        self.env = env
        self.delay = 5
        self.store = simpy.Store(env)

    def latency(self, value, nodeID): 
        yield self.env.timeout(self.delay)
        
    def put(self, value, nodeID):
        print("Node %d broadcasted a block " %(nodeID))
        self.env.process(self.latency(value,nodeID))

def monitor(env):
    prev_tx = 2300
    prev_block = 99900
    avg_pending_tx= 0
    while True:
        yield env.timeout(10)
        print("at step %d "%env.now)

        #Transaction per second(Throughput)
        avg_tx= txID-prev_tx
        prev_tx=txID
        #logger.info(",%d,%d"%(env.now,avg_tx))

        #Avg Block created
        avg_block= BLOCKID-prev_block
        prev_block=BLOCKID
        #logger.info(",%d,%d"%(env.now,avg_block))
        
        #State of the netowork 
        for each in node_map:
            avg_pending_tx+= len(each.pendingpool)
        average= avg_pending_tx/len(node_map)
        #logger.info(",%d,%d"%(env.now,average))
        avg_pending_tx=0

        # Eventual Consistency
        hash_list = set()
        len_list = set()
        for each in node_map:
            len_list.add(len(each.block_list))
            for block in each.block_list:
                hash_list.add(block.hash)
                
        logger.info(",%d,%d"%(env.now,len(len_list)))
        

class Broadcast():
    '''
    Broadcaster is not used due to complexity in modelling the network latency.
    '''
    def __init__(self, env,capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.pipes = []
        
    def put(self, value):
        import ipdb; ipdb.set_trace()
        if not self.pipes:
            raise RuntimeError('There are no output pipes.')
        events = [store.put(value) for store in self.pipes]
        for node in node_map:
            node.process.interrupt()
        
        return self.env.all_of(events)

    def get_output_conn(self):
        pipe = simpy.Store(self.env, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe
    
if __name__== "__main__":
    #env = simpy.rt.RealtimeEnvironment(factor=0.5)
    env=simpy.Environment()
    cable = Network(env)
    node_generator(env,cable)
    env.process(trans_generator(env))
    env.process(monitor(env))
    env.run(until=200)
    print("Simulation ended")
    for each in node_map:
        print("Blocks in node %d " %each.nodeID)
        #for one in each.block_list:
            #one.view_blocks()