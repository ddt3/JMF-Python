# Python Examples
## Introduction
These files have been created to serve as examples of how JMF/JDF can be used to manage jobs on PRISMAsync. Because of that these files are provided "as is". This means that e.g. performance, error handling, input validation have not been a priority.  The examples have been written in Python because of the readability and availability of this language. Note that these examples have been created for Python3

## Installation
A version of Python can be downloaded here: https://www.python.org/downloads/   
For Windows: Run the downloaded Python installer and make sure to check "Add Python 3.x to PATH" 

## Configuration
Some Python libraries need to be installed before you can use these examples. To install the needed linraries, run:

```python -m pip install -r requirements.txt```

When behind a proxy use:

```python -m pip install -r requirements.txt --proxy http://proxy.oce.net:81```

## Check installation
If everything is working properly, you should be able to run the following command:

```python CreateMimePackage.py```