# Import all needed modules
import requests, sys, argparse, socket, threading, xml.dom.minidom, copy
from pathlib import Path
from tkinter import *

#from http.server import HTTPServer, BaseHTTPRequestHandler
import http.server
from time import time
files_dict={
   "QueryResource" : "QueryResource.jmf",
   "QueryKnownDevices" : "QueryKnownDevices.jmf"
   "QueryResourceMediaTypes" : "QueryResourceMediaTypes.jmf"
}

class JMfFiles:
  def __init__(self, folder):
    basepath=Path(__file__).resolve().parent   
    self.jmfdir=basepath.joinpath(folder)
    if not self.jmfdir.exists():
        print("Folder does not exist")
        exit(1)
    
