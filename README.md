SBB

# How to install

Ubuntu:
execute:
pip install -r requirement.txt
Obs.: Some packages may need additional installations through apt-get install

Windows:
Install Anaconda for Python 2.7
In the Windows console, type 'anaconda' before running the python commands.

# How to run

python main.py

All configurable options are in the SBB/config.py file, in the variable CONFIG.

# How to Test

To run all tests, execute in the main folder:
nosetests

You can also execute individual tests files regurlarly using the file name:
python tests/unit_tests/unit_tests.py