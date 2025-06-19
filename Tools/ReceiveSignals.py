"""This example does not need the jmfpython library , but parts of it are reused. 
The following steps are performed:
1) A Webserver is started to receive the signals that are send by PRISMAsync  (library http.server)
2) When a signal is received, it is written to a file.
3) A user interface shows information on number of signals received, port in use etc.

This simple example could be used as a starting point for workflows based on jmf subscriptions
"""
import argparse
import http.server
import socket
import threading
from pathlib import Path
from tkinter import Tk, Entry, Button, Label, StringVar, W,E,EW
from tkinter.font import Font
from tkinter.ttk import Separator
import xml.dom.minidom
import datetime
import pyperclip


################### Constant definitions ###############################
# FONT = Font(family="Arial", size=11)
# FONTIT = Font(family="Arial", size=11, weight="italic")
# base path of this file
BASEPATH=Path(__file__).resolve().parent

################### Class definitions ###############################
class StatusFile:
    """
    Write all received signals to a folder called _received
    pathlib is used to make sure this works on linux and Windows
    create folder if it does not exist
    """

    def __init__(self, SignalFolder):
        self.LogDir = Path(SignalFolder)
        # create folder if it does not exist
        self.LogDir.mkdir(parents=True, exist_ok=True)
        self.Count = 0
        self.CompletePath = Path()

    def Write(self, DataToWrite):
        """This method is used to write the received signal to a file. The file name is generated based on the signal name."""

        CurrentDateTime = datetime.datetime.now().strftime("%Y%m%d-%H.%M.%S")
        # body contains the acctual xml signal data. From this body refID (Xpath:JMF/Signal/@refID)  needs to be extracted
        RefID = self.GetRefIDFromSignalData(DataToWrite)
        self.Count += 1
        # Create a unique filename that contains date-time and refID
        FileName = RefID + "_" + CurrentDateTime + "_"+ str(self.Count) + ".xml"
        self.CompletePath = Path(self.LogDir.joinpath(FileName))
        with open(self.CompletePath, "wb") as WriteF:
            WriteF.write(DataToWrite)
    def GetRefIDFromSignalData(self, SignalData):
        """
        Extract the refID (xpath:JMF/Signal/@refID) from the signal data.
        """
        # Example:
        # <JMF xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="JMF.xsd">
        #    <Signal refID="ref1" />
        # </JMF>
        try:
            SignalDataXML = xml.dom.minidom.parseString(SignalData)
            SignalElements = SignalDataXML.getElementsByTagName("Signal")
            if SignalElements and len(SignalElements) > 0:
                RefID = SignalElements[0].getAttribute("refID")
                if not RefID:
                    RefID = "unknown_refID"
            else:
                RefID = "no_signal_element"
        except xml.parsers.expat.ExpatError as XmlError:
            # Specific error for XML parsing issues
            if clargs.debug:
                print(f"XML parsing error: {XmlError}")
                print(f"Error at line {XmlError.lineno}, column {XmlError.offset}")
            return f"xml_parse_error_{XmlError.code}"

        except UnicodeDecodeError as UniError:
            # Handle encoding issues
            if clargs.debug:
                print(f"Unicode decode error: {UniError}")
            return "encoding_error"

        except AttributeError as AttrError:
            # Handle issues with accessing attributes or methods
            if clargs.debug:
                print(f"Attribute error: {AttrError}")
            return "attribute_error"

        except Exception as CaughtError:
            if clargs.debug:
                print(f"Error parsing signal data: {CaughtError}")
            return "parse_error"
        return RefID

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

        Response_File.Write(body)
        app.UpdateFileName(Response_File.CompletePath.name)
        app.UpdateSignalsReceived(Response_File.Count)

    #pylint: enable=invalid-name



class PRISMAsyncSignalReceiverUI:
    """
    The PRISMAsyncSignalReceiverUI class is used to display the number of signals received,
    the port in use, and the file in use in a user-friendly GUI.
    """
    def __init__(self, NumberOfSignals, IPAdressInUse, PortInUse, FileInUse):
        """
        Initialize the PRISMAsyncSignalReceiverUI class.

        This method sets up the main window and initializes the user interface components
        to display the number of signals received, the port in use, and the file in use.

        Parameters:
        number_of_signals (int): The initial number of signals received.
        port_in_use (int): The port number on which the server is listening.
        file_in_use (str): The name of the file where the last signal was written.

        Returns:
        None
        """
        WIDTH=45
        self.MainWindow = Tk()

        self.NumberOfSignals = NumberOfSignals
        self.PortInUse = PortInUse
        self.FileInUse = FileInUse
        self.IPAdressInUse = IPAdressInUse
        self.SignalText = StringVar()
        self.SignalsReceivedWidget = \
            Entry(self.MainWindow, font=Font(family="Arial", size=13, weight="bold"), textvariable=self.SignalText, justify="right", width=WIDTH-5)
        self.SubUrlText = StringVar()
        self.SubUrlWidget = \
            Entry(self.MainWindow, font=Font(family="Arial", size=11, weight="normal"), textvariable=self.SubUrlText, justify="right", width=WIDTH)
        self.FilenNameText = StringVar()
        self.FilenameWidget = \
            Entry(self.MainWindow, font=Font(family="Arial", size=11, weight="normal"), textvariable=self.FilenNameText, justify="right", width=WIDTH)
        self.SubUrl=f"http://{self.IPAdressInUse}:{self.PortInUse}/"
        self.SubUrlText.set(self.SubUrl)
        self.SetupUI()

    def SetupUI(self):
        """
        Set up the user interface for the PRISMAsync Signal Receiver application.
    
        This method initializes and arranges the various UI components in the main window,
        including labels, entry widgets, separators, and buttons.
    
        Parameters:
        None
    
        Returns:
        None
        """
        self.MainWindow.title("PRISMAsync Signal Receiver")

        # Row 1
        Label(self.MainWindow, text="Signals received:", font=Font(family="Arial", size=13, weight="bold")).grid(
            row=1,column=1, sticky=W
        )
        self.SignalsReceivedWidget.grid(
            row=1,column=3, sticky=W
        )
        self.UpdateSignalsReceived(self.NumberOfSignals)
        # Row 2
        Separator(self.MainWindow, orient='horizontal').grid(row=2, columnspan=3,sticky=EW)

        # Row 3
        Label(self.MainWindow, text="Subscription url to use:", font=Font(family="Arial", size=11)).grid(
            row=3,column=1, sticky=W
        )
        Button(self.MainWindow, text="Copy URL", command=self.CopyURL).grid(
            row=3, column=2, sticky=E, pady=4
        )
        self.SubUrlWidget.grid(
            row=3,column=3, sticky=E
        )
        # Label(self.main_window, text=self.port_in_use, font=Font(family="Arial", size=11)).grid(
        #     row=3,column=2, sticky=E
        # )

        # Row 4
        Label(self.MainWindow, text="Wrote last signal to:", font=Font(family="Arial", size=11)).grid(
            row=4,column=1, sticky=W
        )
        self.FilenameWidget.grid(
            row=4,column=3, sticky=E
        )
        self.UpdateFileName(self.FileInUse)



        # Row 5
        Button(self.MainWindow, text="Quit", command=self.MainWindow.destroy).grid(
            row=5, column=3, sticky=E, pady=4
        )


    def UpdateSignalsReceived(self, NewNumberOfSignals):
        """Update the number of signals received in the UI."""
        self.SignalText.set(NewNumberOfSignals)
    def UpdateFileName(self, NewFileInUse):
        """Update the name of the file in use in the UI."""
        self.FilenNameText.set(NewFileInUse)
    def CopyURL(self):
        """Copy the subscription URL to the clipboard."""
        pyperclip.copy(self.SubUrl)

    def Run(self):
        """Run the PRISMASync Signal Receiver application."""
        self.MainWindow.mainloop()


################### Function definitions ############################


def Log(DebugS):
    """Write debug information if requested."""
    if clargs.debug:
        print(DebugS)

################### Defaults ########################################
# Determine own ipaddress, it is needed to define subscribe url send to PRISMAsync information
S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
S.connect(("8.8.8.8", 80))
IpAddress = S.getsockname()[0]
A_QUERY_ID = "anidofanquery"
DEFAULTFILENAME = "signal.xml"
DEFAULTFOLDERNAME = BASEPATH.joinpath("_received")

################### Defaults ########################################
# Parse command line arguments and generate help information
parser = argparse.ArgumentParser(description="This tool can be used to receive signals from PRISMAsync it will write the signal content to disk.\n"\
                                 "The tool will automatically detect the IP address for listening, detected IP this can be overruled.\n" \
                                    "The link for use as an subscription URL  that can be used as a subscription url", \
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument(
    "--ip",
    type=str,
    default=IpAddress,
    help="IP adress to listen on  for signals (default: " + IpAddress + ")",
)
parser.add_argument(
    "--port",
    type=int,
    default=9090,
    help="Port to listen on for signals (default: 9090)",
)
# _received
parser.add_argument(
    "--folder",
    type=str,
    default=DEFAULTFOLDERNAME,
    help="Folder used to store signals in  (default: "
    + str(DEFAULTFOLDERNAME)
    + ")",
)
parser.add_argument(
    "--debug",
    "-d",
    action="store_true",
    help="Do not print any output just subscribe and write received signals to file",
)
clargs = parser.parse_args()

Log(f"Ip-address of this system: {IpAddress}")

Response_File = StatusFile(clargs.folder)
port = clargs.port
app = PRISMAsyncSignalReceiverUI(Response_File.Count, IpAddress, port,Response_File.CompletePath.name )


# pylint: disable=bare-except
try:
    httpd = http.server.ThreadingHTTPServer(
        ("0.0.0.0", port), SimpleHTTPRequestHandler
    )
    Log(f"Successfully started HTTP server on port {port}")

except PermissionError as err:
    print(f"Permission error: {err}")
    print("The port is in use or you may need administrative privileges to bind to this port.")
    exit(-2)
except OSError as err:
    print(f"OS error: {err}")
    print(f"Failed to start server on port {port}. The port may be in use by another application.")
    exit(-1)
except Exception as err:
    print(f"Unexpected error occurred while starting the server: {err}")
    exit(-3)

# pylint: enable=bare-except
# Start HTTP server, run it in a separate thread
thread = threading.Thread(target=httpd.serve_forever)
thread.daemon = True

# Start listening for PRISMAsync signals by starting the HTTP server in a separate thread
Log(f"Subscription URL: http://{IpAddress}:{port}/")
thread.start()

# Show the User interface
app.Run()
