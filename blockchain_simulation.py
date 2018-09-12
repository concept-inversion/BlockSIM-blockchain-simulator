import random
import simpy

NO_NODES = 20
MEAN_TRANS_GEN_TIME= 8
SD_TRANS_GEN_TIME= 2 

def node_generator():
    global nodeID
    nodeID= random.sample(range(1000,1000+NO_NODES),NO_NODES)

def trans_generator(env):
    txID = 0
    while True:
        yield env.timeout(random.gauss(MEAN_TRANS_GEN_TIME,SD_TRANS_GEN_TIME))
        print("Generating transactions at %d"% env.now)
        txID  += 1
        node = random.choice(nodeID)
        print("Assigned transaction %d to node %d " %(txID, node))
        yield env.timeout(5)

def trans_processor(env):
    pass

node_generator()
env = simpy.Environment()
env.process(trans_generator(env))
env.run(until=30)

