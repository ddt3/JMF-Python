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

    def __init__(self, SignalFile, Increment):
        self.LogDir = BASEPATH.joinpath("_received")
        # create folder if it does not exist
        self.LogDir.mkdir(parents=True, exist_ok=True)
        self.BaseName = Path(SignalFile).stem
        self.Extension = Path(SignalFile).suffix
        self.Count = 0
        self.Increment = Increment
        self.CompletePath = Path(self.LogDir.joinpath(SignalFile))

    def Write(self, DataToWrite):
        """This method is used to write the received signal to a file. The file name is generated based on the signal name."""
        self.Count += 1
        if self.Increment:
            FileName = self.BaseName + "-" + str(self.Count) + self.Extension
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
       
        Response_File.Write(body)
        app.update_filename(Response_File.CompletePath.name)
        app.update_signals_received(Response_File.Count)
        
    #pylint: enable=invalid-name

class PRISMAsyncSignalReceiverUI:
    def __init__(self, number_of_signals, port_in_use, file_in_use):
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
        self.main_window = Tk()

        self.number_of_signals = number_of_signals
        self.port_in_use = port_in_use
        self.file_in_use = file_in_use
        self.SignalText = StringVar()
        self.SignalsReceivedWidget = Entry(self.main_window, font=Font(family="Arial", size=13, weight="bold"), textvariable=self.SignalText, justify="right")
        self.FilenNameText = StringVar()
        self.FilenameWidget = Entry(self.main_window, font=Font(family="Arial", size=13, weight="normal"), textvariable=self.FilenNameText, justify="right")

        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface for the PRISMAsync Signal Receiver application.
    
        This method initializes and arranges the various UI components in the main window,
        including labels, entry widgets, separators, and buttons.
    
        Parameters:
        None
    
        Returns:
        None
        """
        self.main_window.title("PRISMAsync Signal Receiver")

        # Row 1
        Label(self.main_window, text="Signals received:", font=Font(family="Arial", size=13, weight="bold")).grid(
            row=1,column=1, sticky=W
        )
        self.SignalsReceivedWidget.grid(
            row=1,column=2, sticky=W
        )
        self.update_signals_received(self.number_of_signals)
        # Row 2 
        Separator(self.main_window, orient='horizontal').grid(row=2, columnspan=3,sticky=EW)
        
        # Row 3       
        Label(self.main_window, text="Listening on port:", font=Font(family="Arial", size=11)).grid(
            row=3,column=1, sticky=W
        )
        Label(self.main_window, text=self.port_in_use, font=Font(family="Arial", size=11)).grid(
            row=3,column=2, sticky=E
        )

        # Row 4      
        Label(self.main_window, text="Wrote last signal to:", font=Font(family="Arial", size=11)).grid(
            row=4,column=1, sticky=W
        )
        self.FilenameWidget.grid(
            row=4,column=2, sticky=E
        )
        self.update_filename(self.file_in_use)



        # Row 5
        Button(self.main_window, text="Quit", command=self.main_window.destroy).grid(
            row=5, column=2, sticky=E, pady=4
        )

    def update_signals_received(self, new_number_of_signals):
        self.SignalText.set(new_number_of_signals)
    def update_filename(self, new_file_in_use):
        self.FilenNameText.set(new_file_in_use)
    
    def run(self):
        self.main_window.mainloop()


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

################### Defaults ########################################
# Parse command line arguments and generate help information
parser = argparse.ArgumentParser(description="Receive signals from PRISMAsync and store them in a folder")
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
    help="Provide ip adress of current system (default: 9090)",
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

Log(f"Ip-address of this system: {IpAddress}")

Response_File = StatusFile(clargs.file, clargs.inc)
port = clargs.port
app = PRISMAsyncSignalReceiverUI(Response_File.Count, port,Response_File.CompletePath.name )


# pylint: disable=bare-except
try:
    httpd = http.server.ThreadingHTTPServer(
        ("0.0.0.0", port), SimpleHTTPRequestHandler
    )
except OSError as err:
    print("OS error:", err)
    exit(-1)
# pylint: enable=bare-except
# Start HTTP server, run it in a separate thread
thread = threading.Thread(target=httpd.serve_forever)
thread.daemon = True
Log(f"Listening on port: {port}...")
Log(f"Writing signals to: {clargs.file}")
thread.start()

# Show the User interface
app.run()
