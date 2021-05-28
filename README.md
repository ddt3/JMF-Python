# Python Examples V1.0
## Introduction
These files have been created to serve as examples of how JMF/JDF can be used to manage jobs on PRISMAsync. These files are provided "as is". This means that e.g. performance, error handling, input validation have not been a priority.  The examples have been written in Python3 because of the readability and availability of this language.

## Installation
A version of Python3 can be downloaded here: https://www.python.org/downloads/   
For Windows: Run the downloaded Python installer and make sure to check "Add Python 3.x to PATH" 

### Configuration
Some Python packages need to be installed before you can use these examples. To install the needed pacakges, run:

```python -m pip install -r requirements.txt --user```

When behind a proxy use e.g.:

```python -m pip install -r requirements.txt --proxy http://proxy.oce.net:81 --user```

### Check installation
If everything is working properly, you should be able to run the following command:

```python CreateMimePackage.py```
It should create a mime package without error messages

## Usage
All the routines that can be used for JMF communication can be found in:
jmfjdf/jmfmessages.py 
```import jmfjdf.jmfmessages```

A detailed description of the jmfmessages module can be generated using python:
```python -m pydoc -w jmfjdf.jmfmessages```
It will generate the html documentation based on the information in the module.

### Examples
Example python files have been added that make use of the jmfmessages module. 
Before using these examples: 
* Enable JMF support on PRISMAsync 
* Make sure to replace the current printer url ( http://PRISMAsync.cpp.canon:8010 ) in some of the examples to the address of your PRISMAsync.

## Change history
### 1.0.2
* Added SendMimeJob, for sending a mime pacakged Job to PRISMAsync 
* Multiple OS compatiblity improved (replaced "os.path" by pathlib in jmfmessages.py) 
* Show PDF file name as job name ( in CreateMimePackage)

## TODO (future enhancements)
* Add asynchronous communication (returnurl, subscriptions, ...)
* Include own webserver for JDF filespec url's

