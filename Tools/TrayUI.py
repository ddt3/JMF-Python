# pylint: disable=line-too-long, invalid-name
"""This example does not need the jmfpython library , but parts of it are reused. 
The following steps are performed:
1) A JMF message is sent to subscribe to tesource information of media in the trays (library requests)
2) A Webserver is started to receive the signals that are send by PRISMAsync  (library http.server)
3) The information from these signals is interpreted (library xml.com.minidom)
4) A user interface is filled with the information from step 4 (library tkinter), media name, media size and media weight is shown

This simple example could be used as a starting point for workflows based on jmf subscriptions
"""
import argparse
import copy
import http.server
import socket
import sys
import threading
import xml.dom.minidom
from pathlib import Path
from tkinter import Tk, Entry, Button, Label, END, W
import numpy as np
import requests

################### Constant definitions ###############################
HEADERS = {"Content-Type": "multipart/related"}
# Standard mime headers and JMF messages
# Mime Header
MIMEHEADERJMF = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="I_Love_PRISMAsync"

--I_Love_PRISMAsync
Content-ID: part1@cpp.canon
Content-Type: application/vnd.cip4-jmf+xml
content-transfer-encoding:7bit 
Content-Disposition: attachment

"""

# Mime Footer
MIMEFOOTER = """
--I_Love_PRISMAsync--"""
# base path of this file
BASEPATH=Path(__file__).resolve().parent
################### Class definitions ###############################


class StatusFile:
    """
    Write all received signals to a folder called _received
    pathlib is used to make sure this works on linux and Windows
    create folder if it does not exist
    """

    def __init__(self, signalfile, increment):
        self.logdir = BASEPATH.joinpath("_received")
        # create folder if it does not exist
        self.logdir.mkdir(parents=True, exist_ok=True)
        self.basename = Path(signalfile).stem
        self.extension = Path(signalfile).suffix
        self.count = 0
        self.increment = increment
        self.completepath = Path()

    def write(self, datatowrite):
        """This method is used to write the received signal to a file. The file name is generated based on the signal name."""
        if self.increment:
            filename = self.basename + "-" + str(self.count) + self.extension
            self.count += 1
        else:
            filename = self.basename + self.extension
        self.completepath = Path(self.logdir.joinpath(filename))
        with open(self.completepath, "wb") as writef:
            writef.write(datatowrite)


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """The web server that is used to handle http post requests. It needs to be running in the background to receive PRISMAsync signals"""

    #pylint: disable=arguments-differ
    def log_request(self, logformat, *args):
        """This method overrides the default log_request method. To make sure to only log when debugging is turned on"""
        if clargs.debug:
            http.server.BaseHTTPRequestHandler.log_request(self, logformat, *args)
    #pylint: enable=arguments-differ
    def do_GET(self):
        """This method is called when the web server receives a GET request"""	
        log("in GET")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_POST(self):
        """This method is called when PRISMAsync sends a signal based on the subscription. The signal is send using a POST request
        In this method the signal is received and it is handled:the user interface is updated
        """
        #     global clargs
        #     global TrayWindow, UI_Grid
        #     global response_file

        log("in POST")
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        # you can do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        clear(TrayWindow)

        root = xml.dom.minidom.parseString(body)

        Entries = root.getElementsByTagName("ResourceInfo")
        for Resources in Entries:
            Medias = Resources.getElementsByTagName("Media")
            if len(Medias) > 0:
                # Only one ResourceInfo/Media is allowed, take the MediaName from that one
                MediaName = Medias[0].getAttribute("DescriptiveName")
                MediaSize = PointsToPaperSize(Medias[0].getAttribute("Dimension"))
                MediaWeight = Medias[0].getAttribute("Weight")
                MediaCombinedNme = (
                    MediaName + "," + MediaSize + "," + MediaWeight + "gsm"
                )
                PartAmounts = Resources.getElementsByTagName("PartAmount")
                # Media can be available in multiple trays, step through all ResourceInfo/Media/PartAmount
                for PartAmount in PartAmounts:
                    Amount = PartAmount.getAttribute("ActualAmount")
                    TrayNames = PartAmount.getElementsByTagName("Part")
                    # Only one ResourceInfo/Media/PartAmount/Part take the Location from that one
                    Trayname = TrayNames[0].getAttribute("Location")

                    for i, rowi in enumerate(TrayLayoutUI):
                        for j, cellj in enumerate(rowi):
                            TrayMedia = Trayname + "Mx"
                            if TrayMedia in cellj:
                                UI_Grid[i][j].insert(0, MediaCombinedNme)

                    for i, rowi in enumerate(TrayLayoutUI):
                        for j, cellj in enumerate(rowi):
                            TrayMedia = Trayname + "Ax"
                            if TrayMedia in cellj:
                                UI_Grid[i][j].insert(0, Amount)

        response_file.write(body)
        TrayWindow.update()


################### Function definitions ############################


def PointsToPaperSize(dim):
    """Return a paper size based on the dimensions of the media in points"""
    numsplit = dim.split(" ", 1)
    width = round(float(numsplit[0]))
    height = round(float(numsplit[1]))
    sizes = {
        "Ledger"    : (1224, 792),
        "SRA3"      : (907, 1276),
        "RA3"       : (865, 1219),
        "A3"        : (842, 1191),
        "Tabloid"   : (792, 1224),
        "SRA4"      : (638, 907),
        "Legal"     : (612, 1008),
        "Letter"    : (612, 792),
        "A4 Tab"    : (648, 792),
        "A4"        : (595, 842),
        "Executive" : (522, 756),
        "A5"        : (421, 595),
        "A6"        : (297, 421),
    }

    for size, dimensions in sizes.items():
        if width == dimensions[0] and height == dimensions[1]:
            return size

    return str(width) + "pt x " + str(height) + "pt"


def log(debugs):
    """Write debug information if requested."""
    if clargs.debug:
        print(debugs)


def clear(root):
    """Clear the user interface:
    Remove all information from Entry fields in a Window
    """
    for widget in root.winfo_children():
        if not isinstance(widget, Entry):
            clear(widget)
        elif isinstance(widget, Entry):
            widget.delete(0, END)



def subscribe_resource(url, sub_url, query_id):
    """Send a subscription message to PRISMAsync with url, subscribes to information using own ipaddress

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010

    Returns:
      failed    : -1
      succeeded : http response

    """
    # Subscription JMF Messages
    # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses
    jmf_subscribe = """<?xml version="1.0" encoding="UTF-8"?>
<JMF SenderID="Me" Version="1.3" TimeStamp="INF" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
<Query ID="QUERYUUID" Type="Resource" xsi:type="QueryResource">
      <Subscription URL="SUBURL"/>
  <ResourceQuParams Classes="Consumable" ResourceName="Media" Scope="Present"/>
</Query>
</JMF>
"""
    jmf_subscribe = jmf_subscribe.replace("SUBURL", sub_url)
    jmf_subscribe = jmf_subscribe.replace("QUERYUUID", query_id)
    datam = MIMEHEADERJMF + jmf_subscribe + MIMEFOOTER
    log(f"Data:\n{datam}")
    try:
        response = requests.post(url=url, data=datam, headers=HEADERS, timeout=30)
    except requests.exceptions.RequestException:
        print("Unexpected reply from", url)
        print(sys.exc_info()[0], "occurred.")
        return -1

    reply = response.content
    textreply = reply.decode()
    subx = textreply.find("Subscription request denied")
    response_file.write(reply)

    if subx != -1:
        return -1
    else:
        return response
    # End subscribe_resource


def unsubscribe_resource(url, sub_url, query_id):
    """Send an unsubscribe message to PRISMAsync with url, unsubscribes an earlier subscription

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010

    Returns:
      failed    : -1
      succeeded : http response
    """
    # Subscription JMF Messages
    # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses

    jmf_unsubscribe = """<?xml version="1.0" encoding="UTF-8"?>
<JMF SenderID="Me" Version="1.3" TimeStamp="INF" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
  <Command ID="ALCES_AYGJAJ_9_20221220100059" Type="StopPersistentChannel" xsi:type="CommandStopPersistentChannel">
    <StopPersChParams URL="SUBURL" />
  </Command>
</JMF>
"""
    jmf_unsubscribe = jmf_unsubscribe.replace("SUBURL", sub_url)
    jmf_unsubscribe = jmf_unsubscribe.replace("QUERYUUID", query_id)
    datam = MIMEHEADERJMF + jmf_unsubscribe + MIMEFOOTER
    log(f"Data:\n{datam}")
    try:
        response = requests.post(url=url, data=datam, headers=HEADERS, timeout=30)
    except requests.exceptions.RequestException:
        print("Unexpected reply from", url)
        print(sys.exc_info()[0], "occurred.")
        return -1
    reply = response.content

    response_file.write(reply)  # End subscribe_resource


def getStatuscode(url):
    """Get the network status code when trying to connect to provided PRISMAsync URL. This can serve as a check for the connection status"""
    ConnectionTimeout = 2
    try:
        r = requests.get(
            url, timeout=ConnectionTimeout
        )  # it is faster to only request the header
        return r.status_code
    except requests.exceptions.RequestException:
        return -1


################### Defaults ########################################
# Determine own ipaddress, it is needed to define subscribe url send to PRISMAsync information
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IpAddress = s.getsockname()[0]
A_QUERY_ID = "anidofanquery"
defaultfilename = "signal.xml"

################### Defaults ########################################
# Parse command line arguments and generate help information
parser = argparse.ArgumentParser(description="Subscribe to QueueStatus of PRISMAsync ")
parser.add_argument("--url", type=str, help="full url to PRISMAsync jmf interface.")
parser.add_argument(
    "--ip",
    type=str,
    default=IpAddress,
    help="Provide ip adress of current system (default: " + IpAddress + ")",
)
parser.add_argument(
    "--port",
    type=int,
    default=9090,
    help="Provide ip adress of current system (default: 9090",
)
parser.add_argument(
    "--file",
    type=str,
    default=defaultfilename,
    help="Provide filename for JDF ticket used for submissiuon (default: "
    + defaultfilename
    + ")",
)
parser.add_argument(
    "--inc", "-i", action="store_true", help="Add signal count to filename"
)
parser.add_argument(
    "--debug",
    "-d",
    action="store_true",
    help="Do not print any output just subscribe and write to " + defaultfilename,
)
clargs = parser.parse_args()

log(f"Ip-address of this system: {IpAddress}")


response_file = StatusFile(clargs.file, clargs.inc)

### first check if it is possible to connect to PRISMAsync
if getStatuscode(clargs.url) == -1:
    print(f"Cannot connect to PRISMAsync:{clargs.url}")
    exit()

# The following table translates to how the  trays are shown in the small user interface
# Lx defines a label e.g. Tray-1Lx result in a label"Tray-1"
# Mx corresponds to the Medianame in the tray, Ax corresponds to tje Amount of media in the Tray
# The names in this layout should correspond to the actual names in the JMF replies
#  As an example from imagePRESS V1350 KnownDevices Query:
# <StringState Name="LocationName">
#
#      <Value AllowedValue="Tray-13" />
#  ....
# </StringState>

uitable=BASEPATH.joinpath("uitable.csv")
TrayLayoutUI=np.genfromtxt(uitable, delimiter=";", dtype=str, comments='#').tolist()




ColumnWidthM = 30
ColumnWidthA = 5
Font = "Arial 11"

UI_Grid = copy.deepcopy(TrayLayoutUI)
TrayWindow = Tk()
# Define a Window based on the layout described in TrayLayoutUI
for x, row in enumerate(TrayLayoutUI):
    for y, cell in enumerate(row):
        if "Lx" in cell:
            Label(TrayWindow, text=cell.split("L", 1)[0], font=Font).grid(
                row=x, column=y
            )
        elif "Mx" in cell:
            UI_Grid[x][y] = Entry(TrayWindow, width=ColumnWidthM, font=Font)
            UI_Grid[x][y].grid(row=x, column=y)
        elif "Ax" in cell:
            UI_Grid[x][y] = Entry(TrayWindow, width=ColumnWidthA, font=Font)
            UI_Grid[x][y].grid(row=x, column=y)

Button(TrayWindow, text="Quit", command=TrayWindow.destroy).grid(
    row=8, column=1, sticky=W, pady=4
)


# Define subscription url (to send to PRISMAsync)  based on command line arguments
subs_url = "http://" + str(clargs.ip) + ":" + str(clargs.port)
log(f"Subscribe URL: {subs_url}")
# subscribe to resources, PRISMAsync returns a result on a subscription request, write that result to file
result = subscribe_resource(clargs.url, subs_url, A_QUERY_ID)

# if subscription request successfull
if result != -1:
    log("Subscribe successfull")
    # Subscribed successfully, PRISMAsync will send signals for the subscribed information
    # Start a web server to receive signals send by PRISMAsync
    port = clargs.port

    # pylint: disable=bare-except
    try:
        httpd = http.server.ThreadingHTTPServer(
            ("0.0.0.0", port), SimpleHTTPRequestHandler
        )
    except OSError as err:
        print("OS error:", err)
        exit(-1)
    except:
        # When starting webserver fails: unsubscribe. If the JMF persistent channel is removed. PRISMAsync will keep using it.
        unsubscribe_resource(clargs.url, subs_url, A_QUERY_ID)
        exit(-1)
    # pylint: enable=bare-except
    # Start HTTP server, run it in a separate thread
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    log(f"Listening on port {port}...")
    log(f"Writing signals to: {clargs.file}")
    thread.start()

    # Show the User interface
    TrayWindow.mainloop()

    # When the user interface is closed, unsubscribe from resource query
    result = unsubscribe_resource(clargs.url, subs_url, A_QUERY_ID)
else:
    # Subscription failed
    print("Subscribed failed, check response file:{response_file.completepath}")
    with open(response_file.completepath, "rt", encoding="utf-8") as f:
        data = f.readlines()
    line=""
    for line in data:
        if "Comment" in line:
            # Print reason for fail (as provided in comments by PRISMAsync)
            print(line)
            break

    # This script always uses the same subscription ID. Which means that if a subscription with that ID already exists,
    # it is a "dangling" subscription from this  script: try to unsubscribe using the subscription ID and subscription ip address
    # This might allow a subsequent subscription to succeed
    try:
        s = str(line)
        # If comment (fail reason) contains a URL, retrieve URL from error message
        subs_url = (s.split("URL ["))[1].split("]")[0]
    finally :
        sys.exit(-1)
    # Unsubscribe using url found in error message
    log(f"Unsubscribing: {subs_url}")
    result = unsubscribe_resource(clargs.url, subs_url, A_QUERY_ID)
    log(f"Unsubscrib result: \n {result}")
