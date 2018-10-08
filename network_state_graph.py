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
    network_df= pd.DataFrame(nx.to_numpy_array(graph),columns=nodeID,index=nodeID)
    print("Printing network")
    print(network_df)
    #nx.draw(graph)
    #nx.draw(nx.from_numpy_array(network_df.values))
    return network_df
