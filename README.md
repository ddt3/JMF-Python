# Python Examples V1.1
## Introduction
These files have been created to serve as examples of how JMF/JDF can be used to manage jobs on PRISMAsync. These files are provided "as is". This means that e.g. performance, error handling, input validation have not been a priority.  The examples have been written in Python3 because of the readability and availability of this language.

## Installation
A version of Python3 can be downloaded here: https://www.python.org/downloads/   
For Windows: Run the downloaded Python installer and make sure to check "Add Python 3.x to PATH" 

### Configuration
Some Python packages need to be installed before you can use these examples. 

It is recommended to use a virtual environment in Python. More information on virtual environments can be found here: https://realpython.com/python-virtual-environments-a-primer/
<br>The following powershell commands will create a virtual environment in the current directory and then activate it :
``` 
python -m venv .venv
.\.venv\Scripts\activate.ps1
```

To install the needed python pacakges, run:

```python -m pip install -r requirements.txt --find-links ./imports```

OR, when behind a proxy use e.g.:

```python -m pip install -r requirements.txt --find-links ./imports --proxy http://proxy.server.net:81```

### Check installation
If everything is working properly, you should be able to run the following command:

```python CreateMimePackage.py```

It should create a mime package without error messages

## Included scripts
Included python scripts have been divided into 3 groups: Tools, Tests, Demos

### Tools
Tools contains 3 scripts that 

## Interface
A detailed description of the prismasyncjmfjdf module can be generated using python:
```python -m pydoc -w prismasyncjmfjdf```
It will generate the html documentation based on the information in the module.

### Examples
Example python files have been added that make use of the jmfmessages module. 
Before using these examples: 
* Enable JMF support on PRISMAsync 
* Make sure to replace the current printer url ( http://PRISMAsync.cpp.canon:8010 ) in some of the examples to the address of your PRISMAsync.

## Change history
### 1.1.0In Progress
* BREAKING CHANGE: Renamed SendMimeJob to SendMime for sending a mime pacakge to PRISMAsync
* Added Webserver (Thanks Addi!)

## TODO (future enhancements)
* Add asynchronous communication (returnurl, subscriptions, ...)
* Include own webserver for JDF filespec url's

