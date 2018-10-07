import random
import time
import simpy
import logging
import copy
import numpy as np
import pandas as pd
from tasks import task
from blocks import Block
from network_state_graph import network_creator

NO_NODES = 4
MEAN_TRANS_GEN_TIME= 10
SD_TRANS_GEN_TIME= 0.5
MINING_TIME= 2
BLOCKSIZE= 5
txpool_SIZE= 10
BLOCKTIME = 20
logging.basicConfig(filename='logs/blockchain.csv',level=logging.DEBUG)
logger = logging.getLogger()
curr = time.ctime()
MESSAGE_COUNT=0
max_latency=5
#logger.info("-----------------------------------Start of the new Session at %s-------------------------------"%curr)
BLOCKID= 99900


class nodes():
    
    def __init__(self,nodeID):
        self.nodeID= nodeID
        self.env= env
        self.txpool= []
        self.pendingpool = []
        self.block_gas_limit = 5000 
        self.block_list= []
        self.current_gas=0
        self.current_size=0
        self.known_blocks=[]
        self.known_tx=[]
        self.res= simpy.Resource(env,capacity=1)
        self.mine_process = env.process(self.mining())
        print("Node generated with node ID: %d " % self.nodeID)
        #logger.debug('%d , generated, %d'%(self.nodeID,env.now))
    
    def add_task(self,tx):
        
        self.broadcaster(tx,self.nodeID,0,0)
        self.txpool.append(tx)
        self.known_tx.append(tx.id)
        #logger.debug('%d , Tx incoming, %d'%(self.nodeID,env.now))
    
    '''
     type= 0 :transactions
     type= 1 :blocks
    '''

    def receiver(self,data,type,sent_by):
        #If it is a transaction, add it to the pool; Later on verify if the tx has already happened
        global MESSAGE_COUNT
        MESSAGE_COUNT -=1
        #check if the transaction if 0 and if the transaction is already included in the blockchain
        if type==0 and (data.id not in self.known_tx):
            self.txpool.append(data)
            self.known_tx.append(data.id)
            print("%d received transaction %d at %d"%(self.nodeID,data.id,self.env.now))
            self.broadcaster(data,self.nodeID,0,sent_by)
        #check if the block if 0 and if the block is already included in the blockchain
        elif type==1 and (data.id not in self.known_blocks):
            self.intr_data= data
            self.known_blocks.append(data.id)
            self.broadcaster(data,self.nodeID,1,sent_by)
            print("%d received block %d at %d"%(self.nodeID,data.id,self.env.now))
            #self.mine_process.interrupt()
        pass

    def broadcaster(self,data,nodeID,type,sent_by):
        global MESSAGE_COUNT
        # Broadcast to neighbour node. For now, broadcast to all.
        #logger.debug('%d , broadcasting, %d'%(self.nodeID,env.now))
        def propagation(delay,each,data,type): 
            yield self.env.timeout(delay)
            each.receiver(data,type,nodeID)

        for each in node_map:
            # Dont send to self and to the node which sent the message
            if (each.nodeID != self.nodeID) and (each.nodeID != sent_by):                
                #insert delay using nodemap
                print("%d broadcasting data %d to %d"%(self.nodeID,data.id,each.nodeID))
                latency = node_network.loc[self.nodeID,each.nodeID]
                MESSAGE_COUNT +=1
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
                            #self.broadcaster(block,self.nodeID,1,0)
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
               


def node_generator(env):
    global nodeID
    nodeID= random.sample(range(1000,1000+NO_NODES),NO_NODES)
    global node_map
    node_map = [nodes(each) for each in nodeID]
    #import ipdb; ipdb.set_trace()
    print("%d nodes generated:"% NO_NODES)
    global node_network
    node_network=network_creator(nodeID,max_latency)


       
def trans_generator(env):
    global txID
    txID = 2300
    while True:
        TX_SIZE = random.randint(2300,4000)
        TX_GAS = random.randint(1000,2000)
        
        txID  += 1
        print("Generating |  %d  | time %d ."% (txID,env.now))
        #logger.debug("Generating |  %d  | time %d ."% (txID,env.now))
        Task = task(TX_GAS,TX_SIZE,txID)
        # Choose a node randomly from the nodelist
        node = random.choice(nodeID)
        # Assign the task to the node; Find the node object with the nodeID
        for i in node_map:
            if i.nodeID==node:
                print("Transaction %d appended to the node %d "%(txID,i.nodeID))
                i.add_task(Task)
        yield env.timeout(random.gauss(MEAN_TRANS_GEN_TIME,SD_TRANS_GEN_TIME))
             
def monitor(env):
    prev_tx = 2300
    prev_block = 99900
    avg_pending_tx= 0
    while True:
        print("Current MEssages in the system: %d "%MESSAGE_COUNT)
        logger.info(",%d,%d"%(env.now,MESSAGE_COUNT))
        yield env.timeout(2)
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
                
        #logger.info(",%d,%d"%(env.now,len(len_list)))
        

    
if __name__== "__main__":
    #env = simpy.rt.RealtimeEnvironment(factor=0.5)
    env=simpy.Environment()
    node_generator(env)
    env.process(trans_generator(env))
    env.process(monitor(env))
    env.run(until=50)
    print("Simulation ended")
    for each in node_map:
        print("Blocks in node %d " %each.nodeID)
        #for one in each.block_list:
            #one.view_blocks()