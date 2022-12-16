"""This example does not need the jmfpython library , but parts of it are copied here. A JMF message is sent to subscribed to QueueStatus. 
The information send by PRISMAsync is retrieved by a simple webserver. Queue information is send to file.

This simple example could be used as a starting point for workflows based on jmf subscxriptions
"""
import requests, sys, argparse, socket
from pathlib import Path
# Write all received signals to a folder called _received
# pathlib is used to make sure this works on linux and Windows
basepath=Path(__file__).resolve().parent
logdir=basepath.joinpath("_received")
# create folder if it does not exist
logdir.mkdir(parents=True, exist_ok=True)

query_id="anidofanquery"

# Defaults
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IpAddress=s.getsockname()[0]

# responses will ne store in one file (and thus overwritten)
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
parser.add_argument('--silent', '-s', action='store_true',
                    help='Do not print any output just subscribe and write to ' +str(Statusfile))
args = parser.parse_args()

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

# from io import BytesIO
from time import time
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """The actual web server"""

    def do_GET(self):
        #print("in GET")
        self.send_response(200)
        self.end_headers()
        #self.wfile.write(b'Hello, world!')

    def do_POST(self):
        print("in POST")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        print(body)
        # you can do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        with open(Statusfile, 'wb') as f:
            f.write(body)
           
def subscribe_queue_status (url, sub_url):
  """Send a subscription message to PRISMAsync with url

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    
    Returns:
    
  """
  headers={'Content-Type': 'multipart/related'}
  # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses   
  jmf_subscribe="""<?xml version="1.0" encoding="UTF-8"?>
<JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ICSVersions="Base_L1-1.3 Base_L2-1.3 JMF_L1-1.3 JMF_L2-1.3 MIS_L1-1.3 MIS_L2-1.3 MISPRE_L1-1.3 MISPRE_L2-1.3" MaxVersion="1.3" SenderID="Alces Rosenheim-20.08" TimeStamp="2022-07-18T17:05:16+02:00" Version="1.3" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
  <Query ID="QUERYUUID" Type="QueueStatus" xsi:type="QueryQueueStatus">
    <Subscription URL="SUBURL" />
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
  return response


subs_url="http://"+str(args.ip)+":"+str(args.port)
result=subscribe_queue_status(args.url,subs_url)
if result != -1:
  port = args.port
  httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  print("Listening on port %s..." %port)
  httpd.serve_forever()
else:
    print("Subscribed failed")