import random
import time
import simpy
import logging
import copy
import numpy as np
import pandas as pd
from transactions import Transaction
from blocks import Block
from network_state_graph import network_creator
from monitor import creater_logger

NO_NODES = 5
MEAN_TRANS_GEN_TIME= 5
SD_TRANS_GEN_TIME= 0.5
MINING_TIME= 2
BLOCKSIZE= 5
txpool_SIZE= 10
BLOCKTIME = 20
curr = time.ctime()
MESSAGE_COUNT=0
max_latency=5
#logger.info("-----------------------------------Start of the new Session at %s-------------------------------"%curr)
BLOCKID= 99900


class nodes():
    '''
    Properties:
    1. nodeID:      Representing a node
    2. txpool:      A list representing the nodes transaction pool. Its where a new transaction is appended. Acts like a buffer
    3. pendingpool: A list where transaction are stored to form a new block. 
                    Transaction are poped from txpool and are appended to this pool.
    4. block_list:  List of blocks of the node
    5. known_blocks: List of known blocks. It is used for preventing block broadcast forever. It function
                     is defined below in receiver.
    6. known_tx:    List of known Transaction. It is used for preventing block broadcast forever. It function
                     is defined below in receiver.
    7. prev_hash:   Hash of the recent block formed

    8. mine_process: A pointer representing the mining/validator/consensus process. This variable is used to 
                    handle the interrupt.
    

    '''
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
        self.prev_hash=0
        #self.res= simpy.Resource(env,capacity=1)
        self.mine_process = env.process(self.miner())
        print("Node generated with node ID: %d " % self.nodeID)
        logger.debug('%d,%d, generated, node, -'%(env.now,self.nodeID))
    
    def add_transaction(self,tx):

        '''
        Method for appending a transaction to the node's transaction pool
        '''
        self.txpool.append(tx)
        self.known_tx.append(tx.id)
        self.broadcaster(tx,self.nodeID,0,0)
    '''
     type= 0 :transactions
     type= 1 :blocks
    '''

    def receiver(self,data,type,sent_by):
        '''
        Arguments:
        1. data: The data itself. It could be a block or a transaction.
        2. type: Representation of data. 1 for block, 0 for transaction
        3. sent_by: Sender of the message

        Function of the receiver:
        1. Receive the transactions or blocks broadcasted by other nodes. Check if the transaction was 
           already received by the node; checking if the id of data is present in the known_list. 
            1. If it was previously received, then it was already broadcasted. So no need to broadcast.
            2. Else, broadcast the data to other nodes.
        
        2. Generate interrupt if a new block is received.
        '''
       
        global MESSAGE_COUNT
        MESSAGE_COUNT-= 1
        #check if the data is transaction(0) and if the transaction is already included in the blockchain
        if type==0 and (data.id not in self.known_tx):
            self.txpool.append(data)
            # add the transaction to the known list
            self.known_tx.append(data.id)
            print("%d received transaction %d at %d"%(self.nodeID,data.id,self.env.now))
            logger.debug("%d,%d,received,transaction,%d "%(self.env.now,self.nodeID,data.id))
            self.broadcaster(data,self.nodeID,0,sent_by)
        
        #check if the data is block(1) and if the block is already included in the blockchain
        elif type==1 and (data.id not in self.known_blocks):
            # Use a variable intr_data to store the data for interrupt.
            self.intr_data= data
            # add block to the known list
            self.known_blocks.append(data.id)
            self.broadcaster(data,self.nodeID,1,sent_by)
            print("%d,%d, received, block, %d"%(self.env.now,self.nodeID,data.id))
            logger.debug("%d,%d, received, block, %d"%(self.env.now,self.nodeID,data.id))
            # Interrupt the mining process
            self.mine_process.interrupt()
        pass

    def broadcaster(self,data,nodeID,type,sent_by):
        global MESSAGE_COUNT
        # Broadcast to neighbour node. For now, broadcast to all.
        #logger.debug('%d , broadcasting, %d'%(self.nodeID,env.now))
        def propagation(delay,each,data,type): 
            yield self.env.timeout(delay)
            each.receiver(data,type,nodeID)
        print("%d, %d, broadcasting, data, %d"%(env.now,self.nodeID,data.id))
        logger.debug("%d, %d, broadcasting, data, %d"%(env.now,self.nodeID,data.id))
        for each in node_map:
            # Dont send to self and to the node which sent the message
            if (each.nodeID != self.nodeID) and (each.nodeID != sent_by):                
                #insert delay using nodemap
                latency = node_network.loc[self.nodeID,each.nodeID]
                if latency!=0:    
                    MESSAGE_COUNT +=1
                    self.env.process(propagation(latency,each,data,type))
                else:
                    pass
                 
        pass

    def miner(self):
        '''
        Block creation method:
        1. For each transaction, add the gas of the transaction to the current gas.
        2. If the current gas is less than block_gas_limit, add more transaction
        3. Else, hold that transaction and create a new block
        4. For new block, store its hash as previous hash, add that block to know list and broadcast 
            it to the other nodes. 

        Interrupt after receiving block from other nodes:
            If a new block is received, the mining process will be interrupted. After interrupt,
            check if the previous block hash of the node matches the previous hash of the block.
        TODO: 
            What to do if the hash mismatch is happened  
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
                            global BLOCKID
                            BLOCKID+= 1
                            # could this pass for pending pool be pass by refere3nce ? 
                            block = Block(self.current_size,BLOCKID,self.pendingpool,self.nodeID,self.prev_hash)
                            self.prev_hash = block.hash 
                            print('%d, %d, Created, block, %d'%(env.now,self.nodeID,block.id))
                            logger.debug('%d, %d, Created, block, %d'%(env.now,self.nodeID,block.id))
                            print("hash of block is %s"%block.hash)
                            self.block_list.insert(0,block)
                            print("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
                            logger.info("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
                            self.known_blocks.append(block.id)
                            self.broadcaster(block,self.nodeID,1,0)
                            self.current_gas=0
                            self.current_size=0
                            self.pendingpool=[]
            except simpy.Interrupt:
                print("%d,%d, interrupted, block, %d " %(env.now,self.nodeID,self.intr_data.id))
                logger.debug("%d,%d, interrupted, block, %d " %(env.now,self.nodeID,self.intr_data.id))
                # Verify the block:
                #import ipdb; ipdb.set_trace()
                if self.prev_hash == self.intr_data.prev_hash:
                    print("Previous hash match")
                self.block_list.insert(0,self.intr_data)
                print("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
                logger.info("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
                self.txpool=[]
                self.intr_data=None
                self.current_gas=0


def node_generator(env):
    '''
    Generated list of 'n' nodes and network topology with latency using network_creator from 
    network_state_graph based on the parameter NO_NODES
    '''
    global nodeID
    nodeID= random.sample(range(1000,1000+NO_NODES),NO_NODES)
    global node_map
    node_map = [nodes(each) for each in nodeID]
    #import ipdb; ipdb.set_trace()
    print("%d nodes generated:"% NO_NODES)
    global node_network
    node_network=network_creator(nodeID,max_latency)
  
def trans_generator(env):
    '''
    1. Generates transaction in a random time derived from Mean Transaction generation time and its 
    Standard Deviation.
    2. Assigns the transaction to a node radomly from the list of transactions.
    '''
    # Use a global ID for transaction
    global txID
    txID = 2300
    while True:
        # Generate random transaction size and gas
        TX_SIZE = random.randint(2300,4000)
        TX_GAS = random.randint(1000,2000)
        
        txID  += 1
        transaction = Transaction(TX_GAS,TX_SIZE,txID)
        # Choose a node randomly from the nodelist
        node = random.choice(nodeID)
        # Assign the task to the node; Find the node object with the nodeID
        for i in node_map:
            if i.nodeID==node:
                print("%d, %d, Appended, Transaction, %d"%(env.now,i.nodeID,txID))
                logger.debug("%d, %d,Appended, Transaction, %d"%(env.now,i.nodeID,txID))
                i.add_transaction(transaction)
        yield env.timeout(random.gauss(MEAN_TRANS_GEN_TIME,SD_TRANS_GEN_TIME))
             
def monitor(env):
    prev_tx = 2300
    prev_block = 99900
    avg_pending_tx= 0
    while True:
        yield env.timeout(1)
        print("Current MEssages in the system: %d "%MESSAGE_COUNT)
        message_count_logger.info("%d,%d"%(env.now,MESSAGE_COUNT))

        #Transaction per second(Throughput)
        avg_tx= txID-prev_tx
        prev_tx=txID
        #logger.info(",%d,%d"%(env.now,avg_tx))

        #Avg Block created
        avg_block= BLOCKID-prev_block
        prev_block=BLOCKID
        block_creation_logger.info("%d,%d"%(env.now,avg_block))
        

        
        #State of the netowork 
        for each in node_map:
            avg_pending_tx+= len(each.pendingpool)
        average= avg_pending_tx
        pending_transaction_logger.info("%d,%d"%(env.now,average))        
        avg_pending_tx=0

        # Eventual Consistency # Verified
        hash_list = set()
        len_list = set()
        for each in node_map:
            len_list.add(len(each.block_list))
            for block in each.block_list:
                hash_list.add(block.hash)
              
        unique_block_logger.info("%d,%d"%(env.now,len(hash_list)))
           
if __name__== "__main__":
    #env = simpy.rt.RealtimeEnvironment(factor=0.5)
    env=simpy.Environment()
    message_count_logger,block_creation_logger,unique_block_logger,pending_transaction_logger,logger=creater_logger()
    node_generator(env)
    env.process(trans_generator(env))
    env.process(monitor(env))
    env.run(until=10)
    print("----------------------------------------------------------------------------------------------")
    print("Simulation ended")
    logger.info("Simulation ended")
    for each in node_map:
        #logger.info("Blocks in node %d " %each.nodeID)
        print("Blocks in node %d: " %each.nodeID)
        for one in each.block_list:
            print("Created by %d"%one.generated_by)
            one.view_blocks()
            #logger.info(one.view_blocks())
        print("----------------------------------------------")