"""This example does not need the jmfpython library , but parts of it are reused here. A JMF message is sent to subscribe to Resource information of media in the trays.
The information send by PRISMAsync (signal) is received by a simple webserver. This information is used to fill a simple user interface that contains on overview of allt trays.

This simple example could be used as a starting point for workflows based on jmf subscriptions
"""
import re
import requests, sys, argparse, socket
import threading
from pathlib import Path
import xml.dom.minidom
from tkinter import *


# Write all received signals to a folder called _received
# pathlib is used to make sure this works on linux and Windows
basepath=Path(__file__).resolve().parent
logdir=basepath.joinpath("_received")
# create folder if it does not exist
logdir.mkdir(parents=True, exist_ok=True)

query_id="anidofanquery"

def placement_x(item): 
  for xi in range(len(PlacementDesign)):
    for yi in range(len(PlacementDesign[xi])):
      if PlacementDesign[xi][yi] == item:
        x=xi
        y=yi
        break
  return x

def placement_y(item): 
  for xi in range(len(PlacementDesign)):
    for yi in range(len(PlacementDesign[xi])):
      if PlacementDesign[xi][yi] == item:
        x=xi
        y=yi
        break
  return y

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

jmf_devcap= """
<?xml version="1.0" encoding="UTF-8"?>
<JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" MaxVersion="1.3" SenderID="The Dokter" TimeStamp="2022-12-15T09:40:06+02:00" Version="1.3" xsi:type="JMFRootMessage">
  <Query ID="cap1" Type="KnownDevices" xsi:type="QueryKnownDevices">
    <DeviceFilter DeviceDetails="Full" />
  </Query>
</JMF>"""
##

PlacementDesign=[
           #   0            1             2               3            4              5               6             7              8 
          ["TrayLx-1",  "MediaLx-1",  "AmountLx-1",  "TrayLx-2",   "MediaLx-2",  "AmountLx-2",  "TrayLx-3",   "MediaLx-3",  "AmountLx-3"], # 0
          ["Tray-1Lx",  "Tray-1Mx",   "Tray-1Ax",    "Tray-11Lx",  "Tray-11Mx",  "Tray-11Ax",   "Tray-21Lx",  "Tray-21Mx",  "Tray-21Ax"],   # 1
          ["Tray-2Lx",  "Tray-2Mx",   "Tray-2Ax",    "Tray-12Lx",  "Tray-12Mx",  "Tray-12Ax",   "Tray-22Lx",  "Tray-22Mx",  "Tray-22Ax"],   # 2
          ["Tray-3Lx",  "Tray-3Mx",   "Tray-3Ax",    "Tray-13Lx",  "Tray-13Mx",  "Tray-13Ax",   "Tray-23Lx",  "Tray-23Mx",  "Tray-23Ax"],   # 3
          ["Tray-4Lx",  "Tray-4Mx",   "Tray-4Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"],          # 4
          ["Tray-5Lx",  "Tray-5Mx",   "Tray-5Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"],          # 5
          ["Tray-6Lx",  "Tray-6Mx",   "Tray-6Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"]           # 6
        ]
UI_Grid=[
           #   0            1             2               3            4              5               6             7              8 
          ["TrayLx-1",  "MediaLx-1",  "AmountLx-1",  "TrayLx-2",   "MediaLx-2",  "AmountLx-2",  "TrayLx-3",   "MediaLx-3",  "AmountLx-3"], # 0
          ["Tray-1Lx",  "Tray-1Mx",   "Tray-1Ax",    "Tray-11Lx",  "Tray-11Mx",  "Tray-11Ax",   "Tray-21Lx",  "Tray-21Mx",  "Tray-21Ax"],   # 1
          ["Tray-2Lx",  "Tray-2Mx",   "Tray-2Ax",    "Tray-12Lx",  "Tray-12Mx",  "Tray-12Ax",   "Tray-22Lx",  "Tray-22Mx",  "Tray-22Ax"],   # 2
          ["Tray-3Lx",  "Tray-3Mx",   "Tray-3Ax",    "Tray-13Lx",  "Tray-13Mx",  "Tray-13Ax",   "Tray-23Lx",  "Tray-23Mx",  "Tray-23Ax"],   # 3
          ["Tray-4Lx",  "Tray-4Mx",   "Tray-4Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"],          # 4
          ["Tray-5Lx",  "Tray-5Mx",   "Tray-5Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"],          # 5
          ["Tray-6Lx",  "Tray-6Mx",   "Tray-6Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"]           # 6
        ]
TrayWindow=Tk()


for x in range(len(PlacementDesign)):
  for y in range(len(PlacementDesign[x])):
    if "Lx" in PlacementDesign[x][y]:
      Label(TrayWindow, text=PlacementDesign[x][y].split('L', 1)[0], font="Times 16").grid(row=x, column=y)
    elif "Mx" in PlacementDesign[x][y]:
      UI_Grid[x][y] = Entry(TrayWindow)
      UI_Grid[x][y].grid(row=x, column=y)
    elif "Ax" in PlacementDesign[x][y]:
      UI_Grid[x][y] = Entry(TrayWindow)
      UI_Grid[x][y].grid(row=x, column=y)
Button(TrayWindow, text='Quit', command=TrayWindow.destroy).grid(row=8, column=1, sticky=W, pady=4)

def clear(root):
    for widget in root.winfo_children():
        if not isinstance(widget, Entry):
            clear(widget)
        elif isinstance(widget, Entry):
            widget.delete(0, END)

from http.server import HTTPServer, BaseHTTPRequestHandler
import http.server

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
        global TrayWindow, UI_Grid

        log("in POST")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        # you can do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        clear(TrayWindow)

        root = xml.dom.minidom.parseString(body)
        Entries=root.getElementsByTagName("ResourceInfo")
        for resources in Entries:
          Medias=resources.getElementsByTagName("Media")
          MediaName=Medias[0].getAttribute("DescriptiveName")
          Locations=resources.getElementsByTagName("Part")
          for tray in Locations:
            Trayname=tray.getAttribute("Location")
            for x in range(len(PlacementDesign)):
              for y in range(len(PlacementDesign[x])):
                TrayMedia=Trayname+"Mx"
                if TrayMedia in PlacementDesign[x][y]:

                  UI_Grid[x][y].insert(0,MediaName)

        Statusfile=Path(args.file)
        if args.inc:
          folder=Statusfile.parent
          name=Statusfile.stem
          ext=Statusfile.suffix     
          file=name+"-"+str(count)+ext
          Statusfile=folder.joinpath(file)
          
        with open(Statusfile, 'wb') as f:
            f.write(body)
        TrayWindow.update()
           
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
  httpd=http.server.ThreadingHTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  thread = threading.Thread(target=httpd.serve_forever)
  thread.daemon = True
  # httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  print("Listening on port %s..." %port)
  print("Writing signals to: "+args.file)
  # httpd.serve_forever()
  thread.start()
else:
    print("Subscribed failed")
TrayWindow.mainloop()