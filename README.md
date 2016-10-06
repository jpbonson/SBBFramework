[![Build Status](https://travis-ci.org/jpbonson/SBBFramework.svg?branch=master)](https://travis-ci.org/jpbonson/SBBFramework)

# SBBFramework
Python implementation of **Symbiotic Bid-Based (SBB)** framework for problem decomposition using Genetic Programming (GP). This algorithm was developed by the NIMS laboratory, Dalhousie University, Canada.

This framework can be used in the following ways:

- reinforcement learning tasks (via sockets): 
implement a socket client that follows SBB socket interface (available below), define a configuration, and run SBB and the client. A simple socket client for tictactoe is available in SBB/tests/system_tests/tictactoe_game/.py. Sample configurations for this task are available in SBB/configs/sockets/
- reinforcement learning tasks (via code extension): implement a class that inherits SBB/environments/default_environment, add the new environment to _initialize_environment in SBB/sbb.py, define a configuration, and run SBB. A simple class implementation for tictactoe is available in SBB/environments/reinforcement/tictactoe/. Sample configurations for this task are available in SBB/configs/tictactoe/ and SBB/configs/poker/
- reinforcement learning tasks (via code extension): 
- classification tasks: add a .train and a .test file to SBB/datasets, define a configuration, and run SBB. Sample configurations for this task are available in SBB/configs/classification/ (Warning: This framework was developed focusing on reinforcement learning, so it is not able to deal with big datasets)

# Index
1. Introduction to SBB
2. References
3. How to Install
4. How to Run
5. How to Test
6. SBB Examples

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