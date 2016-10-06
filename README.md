[![Build Status](https://travis-ci.org/jpbonson/SBBFramework.svg?branch=master)](https://travis-ci.org/jpbonson/SBBFramework) [![Coverage Status](https://coveralls.io/repos/github/jpbonson/SBBFramework/badge.svg?branch=master)](https://coveralls.io/github/jpbonson/SBBFramework?branch=master)

# SBBFramework
Python implementation of **Symbiotic Bid-Based (SBB)** framework for problem decomposition using Genetic Programming (GP). This algorithm was developed by the NIMS laboratory, Dalhousie University, Canada.

This framework can be used in the following ways:

- reinforcement learning tasks (via sockets): 
implement a socket client that follows SBB socket interface (available below), define a configuration, and run SBB and the client. A simple socket client for tictactoe is available in SBB/tests/system_tests/tictactoe_game/.py. Sample configurations for this task are available in SBB/configs/sockets/
- reinforcement learning tasks (via code extension): implement a class that inherits SBB/environments/default_environment, add the new environment to _initialize_environment in SBB/sbb.py, define a configuration, and run SBB. A simple class implementation for tictactoe is available in SBB/environments/reinforcement/tictactoe/. Sample configurations for this task are available in SBB/configs/tictactoe/ and SBB/configs/poker/
- reinforcement learning tasks (via code extension): 
- classification tasks: add a .train and a .test file to SBB/datasets, define a configuration, and run SBB. Sample configurations for this task are available in SBB/configs/classification/ (Warning: This framework was developed focusing on reinforcement learning, so it is not able to deal with big datasets)

# Index
1. Introduction
2. References
3. How to Install
4. How to Run
5. How to Test
6. SBB Examples

## 1. Introduction
...

## 2. References
**PhD Thesis**

Lichodzijewski, P. (2011) A Symbiotic Bid-Based (SBB) framework for problem decomposition using Genetic Programming, PhD Thesis ([link](http://web.cs.dal.ca/~mheywood/Thesis/PLichodzijewski.pdf))

## 3. How to Install

**Windows:**

Install [Anaconda for Python 2.7](http://continuum.io/downloads)

In the Windows console, type 'anaconda' before running the python commands.

Obs.: You should also install the library 'python-pypoker-eval' if you intend to generate poker hands.

**Ubuntu:**

First, you must have pip installed:
```
sudo apt-get install python-pip
```

Install the dependencies:
```
sudo apt-get install build-essential python-dev pkg-config python-setuptools python-numpy python-scipy  libatlas-dev libatlas3gf-base libfreetype6-dev python-pypoker-eval
```

Obs.: You only need to install 'python-pypoker-eval' if you intend to generate poker hands.

Then execute:
```
sudo pip install -r requirements.txt
```
Obs.: You also have the option to use Anaconda for Ubuntu.

## 4. How to Run

```
python main.py
```

All configurable options are in the SBB/config.py file, in the variable CONFIG.

## 5. How to Test

To run all tests, execute in the main folder:
```
nosetests
```

You can also execute individual tests files using the file name, for example:
```
python tests/unit_tests/unit_tests.py
```

## 6. SBB Examples
...
