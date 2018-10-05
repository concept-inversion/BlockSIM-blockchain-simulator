import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import random
# use graphviz

def show_network(data,labels):
    
    pass

def network_creator(nodeID,max_latency):
    '''
    For future improvements, make sure to handle an unconnected node.
    '''

    dimension= len(nodeID)
    x=np.random.randint(2, size=(dimension, dimension))
    np.fill_diagonal(x,0)
    graph = nx.from_numpy_matrix(x)
    for (u, v) in graph.edges():
        graph[u][v]['weight'] = random.randint(1,max_latency) 
    netowrk_df= pd.DataFrame(nx.to_numpy_array(graph),columns=nodeID,index=nodeID)
    print("Printing network")
    print(netowrk_df)
    return netowrk_df
