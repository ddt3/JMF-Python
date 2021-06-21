import os
import sys
import urllib.request

from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from time import time
from threading import Thread


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        #print("in GET")
        self.send_response(200)
        self.end_headers()
        #self.wfile.write(b'Hello, world!')

    def do_POST(self):
        #print("in POST")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        
        # you can do anything with the body, even save it to disk :)
        # for now, just use time in milisec to make sure the file name is unique
        with open("signal_%s.status" %time(), 'wb') as f:
            f.write(body)
           
        #response = BytesIO()
        #response.write(b'This is POST request. ')
        #response.write(b'Received: ')
        #response.write(body)
        #self.wfile.write(response.getvalue())
        #print(body)


# configure and start/stop the server. path = '.' will start the server in the curent dir, provide a different path for a different directory  
def getServer(host='localhost', port=9090, path='.'):

    # create the server
    try:
        server = HTTPServer((host, port), SimpleHTTPRequestHandler)
        #server.serve_forever(0.5)
    except OSError as err:
        print("OS error: {0}".format(err))
        print('Please check that the local ip address ({}) and port number ({}) are correct!'.format(host, port))
        sys.exit()
    except:
        # re-throw any other error
        raise

    #create a new thread to run the server
    server_thread = Thread(target=server.serve_forever, args=(0.1,))
    server_thread.deamon = False

    #save curent dir to revert back to it
    cwd = os.getcwd()

    # start the server (by starting the newly created thread)
    def start():
        os.chdir(path)
        print('Starting server...')
        server_thread.start()
        print(' - Server is listening on: {} port:{}'.format(*server.server_address))

    # stop the server and close the socket
    def stop():
        os.chdir(cwd)
        print(' - Stopping server on: {} port:{}'.format(*server.server_address))
        server.shutdown()
        server.socket.close()
        server.server_close()
        print('Stopped...')

    return start, stop


#usage example
port = 9090
address = '0.0.0.0'

#create the server
startServer, stopServer = getServer(address, port)

#start the server
startServer()

# make a test request
urllib.request.urlopen("http://localhost:{}/test_request.html".format(port))

# keep the main thread waiting...
input("\n~ Press <Enter> to stop the server ~\n\n")

#stop the server
stopServer()
