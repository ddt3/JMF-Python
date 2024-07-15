# Python Examples V1.1
## Introduction
These files have been created to serve as examples of how JMF/JDF can be used to manage jobs on PRISMAsync. These files are provided "as is". This means that e.g. performance, error handling, input validation have not been a priority.  The examples have been written in Python3 because of the readability and availability of this language.

## Included scripts
Included python scripts have been divided into 2 groups: Tools, Demos (in the future more will follow)

### Tools
The tools folder contains some usefull tools when testing JMF/JDF.
Each tool shows a short usage message when using -h or --help as a parameter.
#### CreateMimePackage
Creates a mime package from JMF, JDF and PDF. This mime package  can be send to PRISMAsync.
#### JMFSubmitter
Can be used to submit jobs to PRISMAsync using JMF, it can also be used to send a mime-package. The  QueueEntryID returned by PRISMAsync is reported
#### RemoveQueueEntries
Can be used to clean-up QueueEntryIDs from PRISMAsync. Can be filtered on status (e.g. only remove Aborted jobs)
#### ReceiveSignals
Can be used for testing PRISMAsync JMF Subscriptions, when signals are send from PRISMAsync this python progam will receive these signals and write them to an XML file or XML files

### Demos
#### TrayUI
Shows the media that is assigned to the trays of PRISMAsync in a simple User Interface. By subscribing to a QueryResource this UI is  automatically updated for each change in PRISMAsync.
#### SendJob
Shows a number of different ways to submit a JMF job.

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

```python -m pip install -r requirements.txt ```

OR, when behind a proxy use e.g.:

```python -m pip install -r requirements.txt --proxy http://proxy.server.net:81```

### Check installation
If everything is working properly, you should be able to run the following command:

```python Tools\CreateMimePackage.py```

It should create a mime package without error messages

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
### 1.1.0
* BREAKING CHANGE: Renamed SendMimeJob to SendMime for sending a mime pacakge to PRISMAsync
* Added Webserver (Thanks Addi!)

## TODO (future enhancements)
* Create Tool to remove subscriptions
* ?
