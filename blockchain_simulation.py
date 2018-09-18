import random
import simpy

NO_NODES = 3
MEAN_TRANS_GEN_TIME= 5
SD_TRANS_GEN_TIME= 1 
MINING_TIME= 2
BLOCKSIZE= 5
MEMPOOL_SIZE= 10

class nodes():
    def __init__(self,nodeID,cable):
        self.nodeID= nodeID
        self.env= env
        self.task_list = []
        self.mempool_size = 10
        self.block_list= []
        self.cable= cable
        self.res = simpy.Resource(env,capacity=1)
        self.process= None
        #self.process = env.process(self.mining(self.bc_pipe))
        print("Node generated with node ID: %d " % self.nodeID)
        
    def run(self):
        yield env.timeout(5)
        print("Running node id %d at time %d"% (self.nodeID,env.now))
    
    def add_task(self,txID):
        self.task_list.append(txID)
        #print("task number %d added to the node %d " %(txID,self.nodeID))
        self.process=env.process(self.mining())
    
    def mining(self):
        # Starts mining/verification of the transactions and handles interrupt for updating the blocks
            if len(self.task_list) != 0:
                request = self.res.request()
                yield request
                task=self.task_list.pop(0)
                print("Mining  | task %d | node %d | time %d " % (task, self.nodeID,env.now))
                yield env.timeout(13)
                self.cable.put(task,self.nodeID)
                self.block_list.append(task)
                self.res.release(request)
                print("Completed |  %d | node %d | time %d" %(task,self.nodeID,env.now))
            else:
                self.mining()

def node_generator(env,cable):
    global nodeID
    nodeID= random.sample(range(1000,1000+NO_NODES),NO_NODES)
    global node_map
    node_map = [nodes(each,cable) for each in nodeID]
    #import ipdb; ipdb.set_trace()
    print("%d nodes generated:"% NO_NODES)

def trans_generator(env):
    txID = 2300
    while True:
        yield env.timeout(random.gauss(MEAN_TRANS_GEN_TIME,SD_TRANS_GEN_TIME))
        txID  += 1
        print("Generating |  %d  | time %d ."% (txID,env.now))
        node = random.choice(nodeID)
        #import ipdb; ipdb.set_trace()
        for i in node_map:
            if i.nodeID==node:
                i.add_task(txID)
                #print("Transaction %d appended to the node %d : "%(txID,i.nodeID))

class Network():
    def __init__(self, env):
        self.env = env
        self.delay = 5
        self.store = simpy.Store(env)

    def latency(self, value, nodeID):
        yield self.env.timeout(self.delay)
        print("interrupting by nodeID  %d......." %nodeID)
        #import ipdb; ipdb.set_trace()
        for node in node_map:
            if node.nodeID != nodeID:
                node.process.interrupt()

    def put(self, value, nodeID):
        print("Node %d broadcasted value %d " %(nodeID,value))
        self.env.process(self.latency(value,nodeID))

#Broadcaster Not used due to complexity in modelling the network latency
class Broadcaster():
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
    env = simpy.Environment()
    bc_pipe = Broadcaster(env)
    cable = Network(env)
    node_generator(env,cable)
    env.process(trans_generator(env))
    # for node in node_map:
    #     env.process(node.mining(bc_pipe))
    env.run(until=100)