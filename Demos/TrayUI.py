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

    def __init__(self, SignalFile, Increment):
        self.LogDir = BASEPATH.joinpath("_received")
        # create folder if it does not exist
        self.LogDir.mkdir(parents=True, exist_ok=True)
        self.BaseName = Path(SignalFile).stem
        self.Extension = Path(SignalFile).suffix
        self.Count = 0
        self.Increment = Increment
        self.CompletePath = Path()

    def Write(self, DataToWrite):
        """This method is used to write the received signal to a file. The file name is generated based on the signal name."""
        if self.Increment:
            FileName = self.BaseName + "-" + str(self.Count) + self.Extension
            self.Count += 1
        else:
            FileName = self.BaseName + self.Extension
        self.CompletePath = Path(self.LogDir.joinpath(FileName))
        with open(self.CompletePath, "wb") as WriteF:
            WriteF.write(DataToWrite)


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """The web server that is used to handle http post requests. It needs to be running in the background to receive PRISMAsync signals"""

    #pylint: disable=arguments-differ,invalid-name
    def log_request(self, logformat, *args):
        """This method overrides the default log_request method. To make sure to only log when debugging is turned on"""
        if clargs.debug:
            http.server.BaseHTTPRequestHandler.log_request(self, logformat, *args)
    #pylint: enable=arguments-differ
    def do_GET(self):
        """This method is called when the web server receives a GET request"""	
        Log("in GET")
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

        Log("in POST")
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        # you can do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        Clear(TrayWindow)

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

        Response_File.Write(body)
        TrayWindow.update()
    #pylint: enable=invalid-name


################### Function definitions ############################


def PointsToPaperSize(Dim):
    """Return a paper size based on the dimensions of the media in points"""
    NumSplit = Dim.split(" ", 1)
    Width = round(float(NumSplit[0]))
    Height = round(float(NumSplit[1]))
    Sizes = {
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

    for Size, Dimensions in Sizes.items():
        if Width == Dimensions[0] and Height == Dimensions[1]:
            return Size

    return str(Width) + "pt x " + str(Height) + "pt"


def Log(DebugS):
    """Write debug information if requested."""
    if clargs.debug:
        print(DebugS)


def Clear(Root):
    """Clear the user interface:
    Remove all information from Entry fields in a Window
    """
    for Widget in Root.winfo_children():
        if not isinstance(Widget, Entry):
            Clear(Widget)
        elif isinstance(Widget, Entry):
            Widget.delete(0, END)



def SubscribeResource(Url, SubUrl, QueryID):
    """Send a subscription message to PRISMAsync with url, subscribes to information using own ipaddress

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010

    Returns:
      failed    : -1
      succeeded : http response

    """
    # Subscription JMF Messages
    # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses
    JmfSubscribe = """<?xml version="1.0" encoding="UTF-8"?>
<JMF SenderID="Me" Version="1.3" TimeStamp="INF" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
<Query ID="QUERYUUID" Type="Resource" xsi:type="QueryResource">
      <Subscription URL="SUBURL"/>
  <ResourceQuParams Classes="Consumable" ResourceName="Media" Scope="Present"/>
</Query>
</JMF>
"""
    JmfSubscribe = JmfSubscribe.replace("SUBURL", SubUrl)
    JmfSubscribe = JmfSubscribe.replace("QUERYUUID", QueryID)
    DataM = MIMEHEADERJMF + JmfSubscribe + MIMEFOOTER
    Log(f"Data:\n{DataM}")
    try:
        Response = requests.post(url=Url, data=DataM, headers=HEADERS, timeout=30)
    except requests.exceptions.RequestException:
        print("Unexpected reply from", Url)
        print(sys.exc_info()[0], "occurred.")
        return -1

    Reply = Response.content
    TextReply = Reply.decode()
    SubX = TextReply.find("Subscription request denied")
    Response_File.Write(Reply)

    if SubX != -1:
        return -1
    else:
        return Response
    # End subscribe_resource


def UnsubscribeResource(Url, SubUrl, QueryID):
    """Send an unsubscribe message to PRISMAsync with url, unsubscribes an earlier subscription

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010

    Returns:
      failed    : -1
      succeeded : http response
    """
    # Subscription JMF Messages
    # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses

    JMFUnsubscribe = """<?xml version="1.0" encoding="UTF-8"?>
<JMF SenderID="Me" Version="1.3" TimeStamp="INF" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.CIP4.org/JDFSchema_1_1 http://schema.cip4.org/jdfschema_1_3/JDF.xsd">
  <Command ID="ALCES_AYGJAJ_9_20221220100059" Type="StopPersistentChannel" xsi:type="CommandStopPersistentChannel">
    <StopPersChParams URL="SUBURL" />
  </Command>
</JMF>
"""
    JMFUnsubscribe = JMFUnsubscribe.replace("SUBURL", SubUrl)
    JMFUnsubscribe = JMFUnsubscribe.replace("QUERYUUID", QueryID)
    DataM = MIMEHEADERJMF + JMFUnsubscribe + MIMEFOOTER
    Log(f"Data:\n{DataM}")
    try:
        Response = requests.post(url=Url, data=DataM, headers=HEADERS, timeout=30)
    except requests.exceptions.RequestException:
        print("Unexpected reply from", Url)
        print(sys.exc_info()[0], "occurred.")
        return -1
    Reply = Response.content

    Response_File.Write(Reply)  # End subscribe_resource


def GetStatusCode(Url):
    """Get the network status code when trying to connect to provided PRISMAsync URL. This can serve as a check for the connection status"""
    ConnectionTimeout = 2
    try:
        Req = requests.get(
            Url, timeout=ConnectionTimeout
        )  # it is faster to only request the header
        return Req.status_code
    except requests.exceptions.RequestException:
        return -1


################### Defaults ########################################
# Determine own ipaddress, it is needed to define subscribe url send to PRISMAsync information
S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
S.connect(("8.8.8.8", 80))
IpAddress = S.getsockname()[0]
A_QUERY_ID = "anidofanquery"
DEFAULTFILENAME = "signal.xml"

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
    default=DEFAULTFILENAME,
    help="Provide filename for JDF ticket used for submissiuon (default: "
    + DEFAULTFILENAME
    + ")",
)
parser.add_argument(
    "--inc", "-i", action="store_true", help="Add signal count to filename"
)
parser.add_argument(
    "--debug",
    "-d",
    action="store_true",
    help="Do not print any output just subscribe and write to " + DEFAULTFILENAME,
)
clargs = parser.parse_args()
if clargs.url is None:
    parser.print_help(sys.stderr)
    print("\nProvide a printer url using: --url URL\n")
    exit(-1)


Log(f"Ip-address of this system: {IpAddress}")


Response_File = StatusFile(clargs.file, clargs.inc)

### first check if it is possible to connect to PRISMAsync
if GetStatusCode(clargs.url) == -1:
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




COLUMNWIDTHM = 30
COLUMNWIDTHA = 5
FONT = "Arial 11"

UI_Grid = copy.deepcopy(TrayLayoutUI)
TrayWindow = Tk()
# Define a Window based on the layout described in TrayLayoutUI
for x, row in enumerate(TrayLayoutUI):
    for y, cell in enumerate(row):
        if "Lx" in cell:
            Label(TrayWindow, text=cell.split("L", 1)[0], font=FONT).grid(
                row=x, column=y
            )
        elif "Mx" in cell:
            UI_Grid[x][y] = Entry(TrayWindow, width=COLUMNWIDTHM, font=FONT)
            UI_Grid[x][y].grid(row=x, column=y)
        elif "Ax" in cell:
            UI_Grid[x][y] = Entry(TrayWindow, width=COLUMNWIDTHA, font=FONT)
            UI_Grid[x][y].grid(row=x, column=y)

Button(TrayWindow, text="Quit", command=TrayWindow.destroy).grid(
    row=8, column=1, sticky=W, pady=4
)


# Define subscription url (to send to PRISMAsync)  based on command line arguments
SUBSURL = "http://" + str(clargs.ip) + ":" + str(clargs.port)
Log(f"Subscribe URL: {SUBSURL}")
# subscribe to resources, PRISMAsync returns a result on a subscription request, write that result to file
Result = SubscribeResource(clargs.url, SUBSURL, A_QUERY_ID)

# if subscription request successfull
if Result != -1:
    Log("Subscribe successfull")
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
        UnsubscribeResource(clargs.url, SUBSURL, A_QUERY_ID)
        exit(-1)
    # pylint: enable=bare-except
    # Start HTTP server, run it in a separate thread
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    Log(f"Listening on port {port}...")
    Log(f"Writing signals to: {clargs.file}")
    thread.start()

    # Show the User interface
    TrayWindow.mainloop()

    # When the user interface is closed, unsubscribe from resource query
    Result = UnsubscribeResource(clargs.url, SUBSURL, A_QUERY_ID)
else:
    # Subscription failed
    print("Subscribed failed, check response file:{response_file.completepath}")
    with open(Response_File.CompletePath, "rt", encoding="utf-8") as f:
        data = f.readlines()
    Line=""
    for Line in data:
        if "Comment" in Line:
            # Print reason for fail (as provided in comments by PRISMAsync)
            print(Line)
            break

    # This script always uses the same subscription ID. Which means that if a subscription with that ID already exists,
    # it is a "dangling" subscription from this  script: try to unsubscribe using the subscription ID and subscription ip address
    # This might allow a subsequent subscription to succeed
    try:
        S = str(Line)
        # If comment (fail reason) contains a URL, retrieve URL from error message
        SUBSURL = (S.split("URL ["))[1].split("]")[0]
    finally :
        sys.exit(-1)
    # Unsubscribe using url found in error message
    Log(f"Unsubscribing: {SUBSURL}")
    Result = UnsubscribeResource(clargs.url, SUBSURL, A_QUERY_ID)
    Log(f"Unsubscrib result: \n {Result}")
