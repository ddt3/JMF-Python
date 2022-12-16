"""This example does not need the jmfpython library , but parts of it are reused here. A JMF message is sent to subscribe to Resource information. 
The information send by PRISMAsync (signal) is received by a simple webserver. Resource information is send to file.

This simple example could be used as a starting point for workflows based on jmf subscriptions
"""
import re
import requests, sys, argparse, socket
from pathlib import Path

# Write all received signals to a folder called _received
# pathlib is used to make sure this works on linux and Windows
basepath=Path(__file__).resolve().parent
logdir=basepath.joinpath("_received")
# create folder if it does not exist
logdir.mkdir(parents=True, exist_ok=True)

query_id="anidofanquery"
count=0

# Defaults
# Determine own ipaddress, it is needed to subscribe to PRISMAsync information
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IpAddress=s.getsockname()[0]
Statusfile=logdir.joinpath("signal.xml")

# Parse command line arguments
parser = argparse.ArgumentParser(description='Subscribe to QueueStatus of PRISMAsync ')
parser.add_argument('--url', type=str,
                    help='full url to PRISMAsync jmf interface.')
parser.add_argument('--ip', type=str, default=IpAddress,
                    help='Provide ip adress of current system (default: '+IpAddress+')')
parser.add_argument('--port', type=int, default=9090,

                    help='Provide ip adress of current system (default: 9090')                    
parser.add_argument('--file',  type=str, default=str(Statusfile),
                    help='Provide filename for JDF ticket used for submissiuon (default: '+str(Statusfile)+')')
parser.add_argument('--inc', '-i', action='store_true',
                    help='Add signal count to filename')
parser.add_argument('--debug', '-d', action='store_true',
                    help='Do not print any output just subscribe and write to '+str(Statusfile))
args = parser.parse_args()

# Log some stuff for debugging purposes.
def log(s):
    if args.debug:
        print(s)

# Standard mime headers and JMF messages
mimeheader_jmf = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="I_Love_PRISMAsync"

--I_Love_PRISMAsync
Content-ID: part1@cpp.canon
Content-Type: application/vnd.cip4-jmf+xml
content-transfer-encoding:7bit 
Content-Disposition: attachment

"""

# Mime Footer
mimefooter = """
--I_Love_PRISMAsync--"""


from http.server import HTTPServer, BaseHTTPRequestHandler

from time import time
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """The actual web server"""
      
    def do_GET(self):
        log("in GET")
        self.send_response(200)
        self.end_headers()
        #self.wfile.write(b'Hello, world!')

    def do_POST(self):
        global count
        global Statusfile
        global args
        global TrayWindow

        log("in POST")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        # you can do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        
        Statusfile=Path(args.file)
        if args.inc:
          folder=Statusfile.parent
          name=Statusfile.stem
          ext=Statusfile.suffix     
          file=name+"-"+str(count)+ext
          Statusfile=folder.joinpath(file)
          
        with open(Statusfile, 'wb') as f:
            f.write(body)

           
def subscribe_resource (url, sub_url):
  """Send a subscription message to PRISMAsync with url, subscribes to information using own ipaddress

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    
    Returns:
    
  """
  headers={'Content-Type': 'multipart/related'}
  # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses   
  jmf_subscribe="""<?xml version="1.0" encoding="UTF-8"?>
<JMF SenderID="Me" Version="1.3" TimeStamp="INF" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
	<Query ID="QUERYUUID" Type="Resource" xsi:type="QueryResource">
        <Subscription URL="SUBURL"/>
		<ResourceQuParams Classes="Consumable" ResourceName="Media" Scope="Present"/>
	</Query>
</JMF>
"""
  jmf_subscribe = jmf_subscribe.replace("SUBURL",sub_url)
  jmf_subscribe = jmf_subscribe.replace("QUERYUUID",query_id)
  data=mimeheader_jmf+jmf_subscribe+mimefooter
  try:
    response=requests.post(url=url,data=data,headers=headers)
  except:
    print("Unexpected reply from", url)
    print(sys.exc_info()[0], "occurred.")
    return -1

  reply=response.content
  textreply=reply.decode()
  x=textreply.find("Subscription request denied")

  if  x != -1:
    return -1
  else:
    return response

# form sunbcription url from parameters
subs_url="http://"+str(args.ip)+":"+str(args.port)
# subscribe to resources, PRISMAsync returns a result on a subscription request, wrate that to file
result=subscribe_resource(args.url,subs_url)
data=result.content
with open(args.file,'wb') as resultfile:
  resultfile.write(data)


# if subscription request successfull
if result != -1:
# start web server
  port = args.port
  httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  print("Listening on port %s..." %port)
  print("Writing signals to: "+args.file)
  httpd.serve_forever()
else:
    print("Subscribed failed")