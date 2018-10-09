# blockchain-simulator
A blockchain simulator based on SimPy in python 3. 

## Steps to Install:

1. Clone this project or download

2. Create a new virtualenv for this project

3. Install all the python package requirements:

        pip install -r requirements.txt

## Files:

1. transactions.py : A class for Transactions representation

2. blocks.py : A class for Block representation

3. network_state_graph.py: A class for creating network topology with latency

4. blockchain_simulation.py: Main script for running the simulator

## How to run:

Open Terminal(Linux) or Command(Windows) and type:
    
        python blockchain_simulation.py

## Parameters
Currently, for changing the parameters of the simulation, we need to change the value of parameters in the blockchain_simulation.py
   
## Format of Log:

        Time |  nodeID  |  Event   | Data Type  | Data ID  