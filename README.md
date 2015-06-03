# pSBB
Python implementation of **Symbiotic Bid-Based (SBB)** framework for problem decomposition using Genetic Programming. Developed by the NIMS laboratory, Dalhousie University, Canada. The current implementation can be used to develop teams of programs to solve classification tasks. The next version will apply it to reinforcement learning.

# Index
1. Introduction
2. References
3. How to Install
4. How to Run
5. How to Test
6. Implementation Details
7. SBB Examples

## 1. Introduction
...

## 2. References
**PhD Thesis**

Lichodzijewski, P. (2011) A Symbiotic Bid-Based (SBB) framework for problem decomposition using Genetic Programming, PhD Thesis ([link](http://web.cs.dal.ca/~mheywood/Thesis/PLichodzijewski.pdf))

## 3. How to Install

**Windows:**

Install [Anaconda for Python 2.7](http://continuum.io/downloads)

In the Windows console, type 'anaconda' before running the python commands.

**Ubuntu:**

Execute:
```
pip install -r requirement.txt
```
Obs.: Some packages may need additional installations through apt-get install

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

## 6. Implementation Details

- This implementation uses the default Python random library to control the seed for the runs, and uses the numpy.random.RandomState object to control the seed for the opponents in the reinforcement learning setting.

## 7. SBB Examples
...
