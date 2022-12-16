"""This example does not need the jmfpython library , but parts of it are copied here. A JMF message is sent to subscribed to QueueStatus. 
The information send by PRISMAsync is retrieved by a simple webserver. Queue information is send to file.

This simple example could be used as a starting point for workflows based on jmf subscxriptions
"""
import argparse
import socket
import sys
import xml.dom.minidom
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from time import time

import requests

# Write all received signals to a folder called _received
# pathlib is used to make sure this works on linux and Windows
basepath=Path(__file__).resolve().parent
logdir=basepath.joinpath("_received")
# create folder if it does not exist
logdir.mkdir(parents=True, exist_ok=True)

# Defaults
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IpAddress=s.getsockname()[0]

# Parse command line arguments
parser = argparse.ArgumentParser(description='Receive information from PRISMAsync ')
parser.add_argument('--port', type=int, default=9090,
                    help='Provide port used for receiver (default: 9090')
parser.add_argument('--debug', '-d', action='store_true',
                    help='Do not print any output just write to file')
args = parser.parse_args()

# Log some stuff for debugging purposes.
def log(s):
    if args.debug:
        print(s)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """The actual web server"""

    def do_GET(self):
        log("in GET")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        log("in POST")
        themoment=datetime.utcnow().strftime('%Y-%m-%d#%H_%M_%S.%f')[:-3]
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        log(body)
        root = xml.dom.minidom.parseString(body)

        # In case it is a returned JDF the received information will contain PhaseTime and an Id
        # Otherwise it is a Singal with an Id
        Entries=root.getElementsByTagName("PhaseTime")
        id_array=[]
        for qid in Entries:           
          id_array.append(qid.getAttribute("QueueEntryID"))
        if not id_array:
          Entries=root.getElementsByTagName("Signal")
          id_array=[]
          for qid in Entries:           
            id_array.append(qid.getAttribute("Id"))
        if id_array:
          log(id_array[0])      
          Statusfile=str(id_array[0])
        else:
          Statusfile="no-id"
          
        Statusfile=logdir.joinpath(themoment+"#"+Statusfile+".xml")
        log("Write to"+str(Statusfile))


        # you can do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        with open(Statusfile, 'wb') as f:
            f.write(body)

port = args.port
httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
print("Listening on... "+str(IpAddress)+":"+str(port))
httpd.serve_forever()
