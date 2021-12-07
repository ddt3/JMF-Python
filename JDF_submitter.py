"""
Send jobs to PRISMAsync using JMF
"""
import argparse
from jmfjdf.jmfmessages import SendJob, basepath

####################################################################################################
#First some defaults are set to make usage easier when e.g. only one printer is used               #
#                                                                                                  #
####################################################################################################

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010.
# Make sure to enable jmf support in the PRISMAsync settings editor

PRINTERURL="http://PRISMAsync.cpp.canon:8010"

# Which JMF file to use for submission in the examples
JMFFILE=str(basepath.joinpath("SubmitQueueEntry.jmf"))

# Which JdF file to use for submission in the examples
JDFFILE=str(basepath.joinpath("Template.jdf"))

# Which Jdf file to use for submission in the examples, either using a path to a file (file://)
# or to a webserver (http://)
PDFURL="file://"+str(basepath.joinpath("Test.pdf"))

# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Submit JMF, JDF, and PDF to PRISMAsync ')
parser.add_argument('--url', type=str, default=PRINTERURL,
                    help='full url to PRISMAsync jmf interface. (default: '+PRINTERURL+')')
parser.add_argument('--jmf', '-j', type=str, default=JMFFILE,
                    help='Provide filename for JMF messages used for submissiuon (default: '+JMFFILE+')')
parser.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+JDFFILE+')')
parser.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help='Provide URL for PDF starting with either http:// or file://. '+
                    'If file:// is used PDF will be part of mime pacakge (default: '+PDFURL+')')
parser.add_argument('--silent', '-s', action='store_true',
                    help='Do not print ID just submit and stay silent')

args = parser.parse_args()

QueueEntryID=SendJob(args.url, args.pdf, args.jdf)
if not args.silent :
  print("Job submitted, got QueueEntryID: ", QueueEntryID)
