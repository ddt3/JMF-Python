import argparse

#############################################################################################################
# The defaults that are used in the provided examples, make sure to provide a correct printer address       #
#                                                                                                           #
#############################################################################################################

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010. make sure to enable jmf support in the PRISMAsync settings editor
PrinterUrl="http://PRISMAsync.cpp.canon:8010"

# Provide the States to filter QueueIDs, possible states: Aborted, Held, Completed. States can be combined, eg "Held Completed"
# To not use any filtering make sure to leave it empty: " "
QueueIDState="Aborted"

# Which JMF file to use for submission in the examples
JMFFile="jmfjdf/SubmitQueueEntry.jmf"

# Which JdF file to use for submission in the examples
JDFFile="jmfjdf/Template.jdf"

# Which Jdf file to use for submission in the examples, either using a path to a file (file://) or to a webserver (http://)
PDFUrl="file://jmfjdf/Test.pdf"

#############################################################################################################
# No editing needed beyond this point (unless you would like to add your own options)                       #
#                                                                                                           #
#############################################################################################################

# The following block is used to take command line options for this tool.
# It needs a printer address and an  opional --status. --help is automatically generated
parser = argparse.ArgumentParser(description='Delete all JMF QueueEntries that have the provided status from PRISMAsync')
parser.add_argument('--url', type=str, default=PrinterUrl,
                    help='full url to PRISMAsync jmf interface. (default: '+PrinterUrl+')')
parser.add_argument('--status', '-s', type=str, default=QueueIDState,
                    help='The status of the jobs that need to be removed or listed (default:'+QueueIDState+')')
parser.add_argument('--jmf', '-p', type=str, default=JMFFile,
                    help='Provide filename for JMF messages used for submissiuon (default:'+JMFFile+')')
parser.add_argument('--jdf', '-p', type=str, default=JDFFile,
                    help='Provide filename for JDF ticket used for submissiuon (default:'+JDFFile+')')
parser.add_argument('--pdf', '-p', type=str, default=PDFUrl,
                    help='Provide URL for PDF starting with either http:// or file. (default:'+PDFUrl+')')
args = parser.parse_args()


url=args.url
status=args.status
pdf=args.pdf
removemime=(args.removemime == 'Yes')