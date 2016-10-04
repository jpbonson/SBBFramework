[![Build Status](https://travis-ci.org/jpbonson/SBBFramework.svg?branch=master)](https://travis-ci.org/jpbonson/SBBFramework)

# SBBFramework
Python implementation of **Symbiotic Bid-Based (SBB)** framework for problem decomposition using Genetic Programming (GP). Algorithm developed by the NIMS laboratory, Dalhousie University, Canada. This implementation can be used as an extendable code to apply GP to reinforcement learning tasks.

[Work in progress...]

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
