[![Build Status](https://travis-ci.org/jpbonson/SBBFramework.svg?branch=master)](https://travis-ci.org/jpbonson/SBBFramework) [![Coverage Status](https://coveralls.io/repos/github/jpbonson/SBBFramework/badge.svg?branch=master)](https://coveralls.io/github/jpbonson/SBBFramework?branch=master)

# SBBFramework
Python implementation of **Symbiotic Bid-Based (SBB)** framework for problem decomposition using Genetic Programming (GP). This algorithm was developed by the NIMS laboratory, Dalhousie University, Canada.

This framework can be used in the following ways:

**Reinforcement Learning tasks (via sockets)**

1. implement a socket client that follows SBB socket interface (available below)

2. define a configuration

3. run SBB and the client

- a simple socket client for tictactoe is available in SBB/tests/system_tests/tictactoe_game/

- sample configurations for this task are available in SBB/configs/sockets/

**Reinforcement Learning tasks (via code extension)**

1. implement a class that inherits SBB/environments/default_environment

2. add the new environment to _initialize_environment in SBB/sbb.py

3. define a configuration

4. run SBB

- a simple class implementation for tictactoe is available in SBB/environments/reinforcement/tictactoe/

- sample configurations for this task are available in SBB/configs/tictactoe/ and SBB/configs/poker/

**Classification tasks**

1. add a .train and a .test file to SBB/datasets

2. define a configuration

3. run SBB

- sample configurations for this task are available in SBB/configs/classification/
- *warning: This framework was developed focusing on reinforcement learning, so it is not able to deal with big datasets*


# Index
1. Introduction to SBB
2. References
3. How to Install
4. How to Run
5. How to Test
6. Socket Interface

## 1. Introduction to SBB
[TODO]

## 2. References

Below there are a few of the publications about SBB.

**Papers**

P. Lichodzijewski and M. I. Heywood. Symbiosis, complexification and simplicity under GP. In Proceedings of the ACM Genetic and Evolutionary Computation Conference, pages 853–860, 2010.

J. A. Doucette, P. Lichodzijewski, and M. I. Heywood. Hierarchical task decomposition through symbiosis in reinforcement learning. In ACM Genetic and Evolutionary Computation Conference, pages 97–104, 2012.

S. Kelly, P. Lichodzijewski, and M. I. Heywood. On run time libraries and hierarchical symbiosis. In Evolutionary Computation (CEC), 2012 IEEE Congress on, pages 1–8. IEEE, 2012.

J. P. C. Bonson, A. Mcintyre, and M. I. Heywood. On Novelty Driven Evolution in Poker. In Computational Intelligence, 2016 IEEE Symposium Series on. IEEE, 2016.

**Master Thesis**

J. P. C. Bonson. Diversity and Novelty as Objectives in Poker, 2016. ([link](http://web.cs.dal.ca/~mheywood/Thesis/JPCBonson.pdf))

**PhD Thesis**

P. Lichodzijewski. A Symbiotic Bid-Based (SBB) framework for problem decomposition using Genetic Programming, 2011. ([link](http://web.cs.dal.ca/~mheywood/Thesis/PLichodzijewski.pdf))

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
sudo apt-get install build-essential python-dev pkg-config python-setuptools python-numpy python-scipy  libatlas-dev libatlas3gf-base libfreetype6-dev
```

Obs.: You should also install the library 'python-pypoker-eval' if you intend to generate poker hands.

Then execute:
```
sudo pip install -r requirements.txt
```
Obs.: You also have the option to use Anaconda for Ubuntu.

## 4. How to Run

```
python main.py -f CONFIG_FILE
```

Various predefined configuration files are available in SBB/configs/

## 5. How to Test

```
nosetests
```

## 6. Socket Interface

[TODO]
