"""This example does not need the jmfpython library , but parts of it are reused here. A JMF message is sent to subscribe to Resource information of media in the trays.
The information send by PRISMAsync (signal) is received by a simple webserver. This information is used to fill a simple user interface that contains on overview of allt trays.

This simple example could be used as a starting point for workflows based on jmf subscriptions
"""
# Import all needed modules
import requests, sys, argparse, socket, threading, xml.dom.minidom, copy
from pathlib import Path
from tkinter import *

#from http.server import HTTPServer, BaseHTTPRequestHandler
import http.server
from time import time

# Log some stuff for debugging purposes.
# Write all received signals to a folder called _received
# pathlib is used to make sure this works on linux and Windows
# create folder if it does not exist

################### Constant definitions ###############################
headers={'Content-Type': 'multipart/related'}
  # Standard mime headers and JMF messages
  # Mime Header
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

################### Class definitions ###############################

class StatusFile:

  def __init__(self, signalfile, increment):
    basepath=Path(__file__).resolve().parent   
    self.logdir=basepath.joinpath("_received")
    # create folder if it does not exist
    self.logdir.mkdir(parents=True, exist_ok=True)
    self.basename=Path(signalfile).stem
    self.extension=Path(signalfile).suffix
    self.count=0
    self.increment=increment

  def write(self,data):
    if self.increment:
      filename=self.basename+'-'+str(self.count)+self.extension
      self.count+=1
    else:
      filename=self.basename+self.extension
    self.completepath=Path(self.logdir.joinpath(filename))
    with open(self.completepath, 'wb') as f:
            f.write(data)

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """The actual web server"""
      
    def log_request(self, format, *args):
      if clargs.debug:
        http.server.BaseHTTPRequestHandler.log_request(self, format, *args)


    def do_GET(self):
        log("in GET")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


    def do_POST(self):
        global args
        global TrayWindow, UI_Grid
        global response_file

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
        for Resources in Entries:
            Medias=Resources.getElementsByTagName("Media")
            if len(Medias) > 0:
              # Only one ResourceInfo/Media is allowed, take the MediaName from that one
              MediaName=Medias[0].getAttribute("DescriptiveName")
              PartAmounts=Resources.getElementsByTagName("PartAmount")
              # Media can be available in multiple trays, step through all ResourceInfo/Media/PartAmount
              for PartAmount in PartAmounts:
                Amount=PartAmount.getAttribute("ActualAmount")
                TrayNames=PartAmount.getElementsByTagName("Part")
                # Only one ResourceInfo/Media/PartAmount/Part take the Location from that one
                Trayname=TrayNames[0].getAttribute("Location")
                for x in range(len(TrayLayoutUI)):
                  for y in range(len(TrayLayoutUI[x])):
                    TrayMedia=Trayname+"Mx"
                    if TrayMedia in TrayLayoutUI[x][y]:
                      UI_Grid[x][y].insert(0,MediaName)
                for x in range(len(TrayLayoutUI)):
                  for y in range(len(TrayLayoutUI[x])):
                    TrayMedia=Trayname+"Ax"
                    if TrayMedia in TrayLayoutUI[x][y]:
                      UI_Grid[x][y].insert(0,Amount)

        response_file.write(body)
        TrayWindow.update()

class JMfFiles:
  def __init__(self, folder):
     pass
     
     


################### Function definitions ############################

def pointstoformat(str):
  numsplit=str.split(' ',1)
  w=round(float(numsplit[0]))
  h=round(float(numsplit[1]))
  if w==595:
    if h==842:
      return "A4"

def log(s):
    if clargs.debug:
        print(s)

def clear(root):
    for widget in root.winfo_children():
        if not isinstance(widget, Entry):
            clear(widget)
        elif isinstance(widget, Entry):
            widget.delete(0, END)
           
def retrieve_tray_layout(url):
   pass
   
def subscribe_resource (url, sub_url):
  """Send a subscription message to PRISMAsync with url, subscribes to information using own ipaddress

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    
    Returns:
    
  """
  # Subscription JMF Messages
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
  log("Data:\n%s"%data)
  try:
    response=requests.post(url=url,data=data,headers=headers)
  except:
    print("Unexpected reply from", url)
    print(sys.exc_info()[0], "occurred.")
    return -1

  reply=response.content
  textreply=reply.decode()
  x=textreply.find("Subscription request denied")
  response_file.write(reply)

  if  x != -1:
    return -1
  else:
    return response
  # End subscribe_resource

def unsubscribe_resource (url, sub_url):
  """Send an unsubscribe message to PRISMAsync with url, unsubscribes an earlier subscription

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    
    Returns:
    
  """
  # Subscription JMF Messages
  # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses   

  jmf_unsubscribe="""<?xml version="1.0" encoding="UTF-8"?>
<JMF SenderID="Me" Version="1.3" TimeStamp="INF" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
  <Command ID="ALCES_AYGJAJ_9_20221220100059" Type="StopPersistentChannel" xsi:type="CommandStopPersistentChannel">
    <StopPersChParams URL="SUBURL" />
  </Command>
</JMF>
"""
  jmf_unsubscribe = jmf_unsubscribe.replace("SUBURL",sub_url)
  jmf_unsubscribe = jmf_unsubscribe.replace("QUERYUUID",query_id)
  data=mimeheader_jmf+jmf_unsubscribe+mimefooter
  log("Data:\n%s"%data)
  try:
    response=requests.post(url=url,data=data,headers=headers)
  except:
    print("Unexpected reply from", url)
    print(sys.exc_info()[0], "occurred.")
    return -1
  reply=response.content

  response_file.write(reply)# End subscribe_resource

def getStatuscode(url):
    ConnectionTimeout=2
    try:
        r = requests.get(url,timeout=ConnectionTimeout) # it is faster to only request the header
        return (r.status_code)
    except:
        return -1

################### Defaults ########################################
# Determine own ipaddress, it is needed to subscribe to PRISMAsync information
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IpAddress=s.getsockname()[0]
query_id="anidofanquery"
defaultfilename="signal.xml"

################### Defaults ########################################
# Parse command line arguments and generate help information
parser = argparse.ArgumentParser(description='Subscribe to QueueStatus of PRISMAsync ')
parser.add_argument('--url', type=str,
                    help='full url to PRISMAsync jmf interface.')
parser.add_argument('--ip', type=str, default=IpAddress,
                    help='Provide ip adress of current system (default: '+IpAddress+')')
parser.add_argument('--port', type=int, default=9090,

                    help='Provide ip adress of current system (default: 9090')                    
parser.add_argument('--file',  type=str, default=defaultfilename,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+defaultfilename+')')
parser.add_argument('--inc', '-i', action='store_true',
                    help='Add signal count to filename')
parser.add_argument('--debug', '-d', action='store_true',
                    help='Do not print any output just subscribe and write to '+ defaultfilename)
clargs = parser.parse_args()

log("Ip-address of this system: %s" % IpAddress)
response_file=StatusFile(clargs.file, clargs.inc)

### first check if it is possible to connect to PRISMAsync
if getStatuscode(clargs.url) == -1:
   print("Cannot connect to PRISMAsync:%s" %clargs.url)
   exit()

# The following table translates to how the user trays are shown in the created user interface
TrayLayoutUI=[
           #   0            1             2               3            4              5               6             7              8 
          ["TrayLx-1",  "Media NameLx-1",  "AmountLx-1",  "TrayLx-2",   "Media NameLx-2",  "AmountLx-2",  "TrayLx-3",   "Media NameLx-3",  "AmountLx-3"], # 0
          ["Tray-1Lx",  "Tray-1Mx",   "Tray-1Ax",    "Tray-11Lx",  "Tray-11Mx",  "Tray-11Ax",   "Tray-21Lx",  "Tray-21Mx",  "Tray-21Ax" ], # 1
          ["Tray-2Lx",  "Tray-2Mx",   "Tray-2Ax",    "Tray-12Lx",  "Tray-12Mx",  "Tray-12Ax",   "Tray-22Lx",  "Tray-22Mx",  "Tray-22Ax" ], # 2
          ["Tray-3Lx",  "Tray-3Mx",   "Tray-3Ax",    "Tray-13Lx",  "Tray-13Mx",  "Tray-13Ax",   "Tray-23Lx",  "Tray-23Mx",  "Tray-23Ax" ], # 3
          ["Tray-4Lx",  "Tray-4Mx",   "Tray-4Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"        ], # 4
          ["Tray-5Lx",  "Tray-5Mx",   "Tray-5Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"        ], # 5
          ["Tray-6Lx",  "Tray-6Mx",   "Tray-6Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"        ]  # 6
        ]
ColumnWidth = 17
Font="Arial 16"
# PlacementDesign=[
#            #   0            1             2               3            4              5               6             7              8 
#           ["TrayLx-1",  "MediaLx-1",  "AmountLx-1",  "TrayLx-2",   "MediaLx-2",  "AmountLx-2",  "TrayLx-3",   "MediaLx-3",  "AmountLx-3"],  # 0
#           ["Tray-1Lx",  "Tray-1Mx",   "Tray-1Ax",    "Tray-11Lx",  "Tray-11Mx",  "Tray-11Ax",   "Tray-21Lx",  "Tray-21Mx",  "Tray-21Ax"],   # 1
#           ["Tray-2Lx",  "Tray-2Mx",   "Tray-2Ax",    "Tray-12Lx",  "Tray-12Mx",  "Tray-12Ax",   "Tray-22Lx",  "Tray-22Mx",  "Tray-22Ax"],   # 2
#           ["Tray-3Lx",  "Tray-3Mx",   "Tray-3Ax",    "Tray-13Lx",  "Tray-13Mx",  "Tray-13Ax",   "Tray-23Lx",  "Tray-23Mx",  "Tray-23Ax"],   # 3
#           ["Tray-4Lx",  "Tray-4Mx",   "Tray-4Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"],          # 4
#           ["Tray-5Lx",  "Tray-5Mx",   "Tray-5Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"],          # 5
#           ["Tray-6Lx",  "Tray-6Mx",   "Tray-6Ax",    "NA",         "NA",         "NA",          "NA",         "NA",         "NA"]           # 6
#         ]


UI_Grid=copy.deepcopy(TrayLayoutUI)
TrayWindow=Tk()
# Create Window containing tray information
for x in range(len(TrayLayoutUI)):
  for y in range(len(TrayLayoutUI[x])):
    if "Lx" in TrayLayoutUI[x][y]:
      Label(TrayWindow, text=TrayLayoutUI[x][y].split('L', 1)[0], font=Font).grid(row=x, column=y)
    elif "Mx" in TrayLayoutUI[x][y]:
      UI_Grid[x][y] = Entry(TrayWindow,width=ColumnWidth, font=Font)
      UI_Grid[x][y].grid(row=x, column=y)
    elif "Ax" in TrayLayoutUI[x][y]:
      UI_Grid[x][y] = Entry(TrayWindow, width=ColumnWidth, font=Font)
      UI_Grid[x][y].grid(row=x, column=y)
Button(TrayWindow, text='Quit', command=TrayWindow.destroy).grid(row=8, column=1, sticky=W, pady=4)



# form subscription url from parameters
subs_url="http://"+str(clargs.ip)+":"+str(clargs.port)
log("Subscribe URL: %s"%subs_url)
# subscribe to resources, PRISMAsync returns a result on a subscription request, wrate that to file
result=subscribe_resource(clargs.url,subs_url)

# if subscription request successfull
if result != -1:
  log("Subscribe successfull")
# start web server
  port = clargs.port
  try:
    httpd=http.server.ThreadingHTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  except:
    unsubscribe_resource(clargs.url,subs_url)
    exit(-1)
  thread = threading.Thread(target=httpd.serve_forever)
  thread.daemon = True
  # httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  log("Listening on port %s..." %port)
  log("Writing signals to: "+clargs.file)
  # httpd.serve_forever()
  thread.start()
  TrayWindow.mainloop()
  result=unsubscribe_resource(clargs.url,subs_url)
else:
    # Subscription failed
    print("Subscribed failed, check response file:%s" %response_file.completepath)
    with open(response_file.completepath, 'rt') as f:
      data = f.readlines()
    for line in data:
      if 'Comment' in line:
        print(line)
        break
    
    s=str(line)   
    try:
      subs_url=(s.split("URL ["))[1].split("]")[0]
    except:
      exit (-1)
    log("Unsubscribing: %s" %subs_url)
    result=unsubscribe_resource(clargs.url,subs_url)
    log("Unsubscrib result: \n %s" %result)