"""
JMFSubmitter can be used to easily submit a job to PRISMAsync using JMF.
Upon exit it will return the returned QueueEntryID
"""
import argparse
from pathlib import Path
from prismasyncjmfjdf import SendJob, SendMime

#############################################################################################################
#First some defaults are set to make usage easier when e.g. only one printer is used                        #
#                                                                                                           #
#############################################################################################################

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010. make sure to enable jmf support in the PRISMAsync settings editor

PRISMASYNCADDRESS="http://PRISMAsync.cpp.canon:8010"

basepath=Path(__file__).resolve().parent
configpath=basepath.joinpath(".config")
# first check if a .config folder exists in the same folder as this script
if Path.exists(configpath) :
    jmffile=configpath.joinpath("SubmitQueueEntry.jmf")
    jdffile=configpath.joinpath("Template.jdf")
    pdffile=configpath.joinpath("Test.pdf")
    if not jmffile.exists:
        SUBMITJMF=None
    else:
        SUBMITJMF=str(jmffile)
    if not jdffile.exists:
        JDFFILE=None
    else:
        JDFFILE=str(jdffile)
    if not pdffile.exists:
        PDFURL=None
    else:
        PDFURL=f'file://{str(pdffile)}'

# # Which JMF file to use for submission in the examples
# SUBMITJMF='\"jmfjdf/SubmitQueueEntry.jmf\"'

# # Which JdF file to use for submission in the examples
# JDFFILE='\"jmfjdf/Template.jdf\"'

# # Which Jdf file to use for submission in the examples, either using a path to a file (file://) or to a webserver (http://)
# PDFURL='file:\"//jmfjdf/Test.pdf\"'

# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Submit JMF, JDF, and PDF to PRISMAsync. Create a .config folder to add defaults for: SubmitQueueEntry.jmf, Template.jdf, and Test.pdf')
parser.add_argument('--url', type=str, default=PRISMASYNCADDRESS,
                    help='full url to PRISMAsync jmf interface (default: '+PRISMASYNCADDRESS+')')
parser.add_argument('--jmf', '-j', type=str, default=SUBMITJMF,
                    help='Provide filename for JMF messages used for submission (default: \"'+SUBMITJMF+'\")')
parser.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+JDFFILE+')')
parser.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help='Provide URL for PDF starting with either http:// or file://.'+
                    ' If file:// is used PDF will be part of mime pacakge (default: '+PDFURL+')')
parser.add_argument('--silent', '-s', action='store_true',
                    help='Do not print ID just submit and stay silent')
parser.add_argument('--mime', '-m', type=str, default=None,
                    help='Mime package to send, takes priority over all other settings (default: no mime package)')
args = parser.parse_args()

# Perform sanity checks on command line arguments
# Check if pdf argument starts with http(s):// or file://
if args.mime is None :
    if args.pdf.startswith("http://") or args.pdf.startswith("https://") :
        pass
    elif args.pdf.startswith("file://"):
        pass
    else:
        print("Cannot send: PDF URL must start with http://, https:// or file://")
        exit()
else :
    # Check if mime filename argument does exist
    if Path(args.mime).is_file():
        pass
    else:
        print(f"Cannot send: Mime package does not exist\n{args.mime}")
        exit()
# First check if mime argument is given, if yes, send mine , else send JDF and PDF
if args.mime is None :
    QueueEntryID=SendJob(args.url, args.pdf, args.jdf)
else :
    QueueEntryID=SendMime(args.url, args.mime)
if not args.silent :
    print("Job submitted, got QueueEntryID: ", QueueEntryID)
