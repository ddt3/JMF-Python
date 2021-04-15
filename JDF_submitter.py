from jmfjdf.jmfmessages import SendJob
import argparse

#############################################################################################################
#First some defaults are set to make usage easier when e.g. only one printer is used                        #
#                                                                                                           #
#############################################################################################################

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010. make sure to enable jmf support in the PRISMAsync settings editor
PrinterUrl="http://PRISMAsync.cpp.canon:8010"

# Which JMF file to use for submission in the examples
JMFFile="jmfjdf/SubmitQueueEntry.jmf"

# Which JdF file to use for submission in the examples
JDFFile="jmfjdf/Template.jdf"

# Which Jdf file to use for submission in the examples, either using a path to a file (file://) or to a webserver (http://)
PDFUrl="file://jmfjdf/Test.pdf"

# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Submit JMF, JDF, and PDF to PRISMAsync ')
parser.add_argument('--url', type=str, default=PrinterUrl,
                    help='full url to PRISMAsync jmf interface. (default: '+PrinterUrl+')')
parser.add_argument('--jmf', '-j', type=str, default=JMFFile,
                    help='Provide filename for JMF messages used for submissiuon (default: '+JMFFile+')')
parser.add_argument('--jdf', '-t', type=str, default=JDFFile,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+JDFFile+')')
parser.add_argument('--pdf', '-p', type=str, default=PDFUrl,
                    help='Provide URL for PDF starting with either http:// or file://. If file:// is used PDF will be part of mime pacakge (default: '+PDFUrl+')')
parser.add_argument('--silent', '-s', action='store_true',
                    help='Do not print ID just submit and stay silent')

args = parser.parse_args()

QueueEntryID=SendJob(args.url, args.pdf, args.jdf)
if not args.silent :
    print("Job submitted, got QueueEntryID: ", QueueEntryID)