"""
Send jobs to PRISMAsync using JMF
"""
import argparse
from jmfjdf.jmfmessages import SendJob, SendMimeJob, basepath

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
genericgrp=parser.add_argument_group('Generic arguments','')

genericgrp.add_argument('--silent', '-s', action='store_true',
                    help='Do not print ID just submit and stay silent')

genericgrp.add_argument('--url', type=str, default=PRINTERURL,
                    help='full url to PRISMAsync jmf interface. (default: '+PRINTERURL+')')

creategrp=parser.add_argument_group('Create arguments', '')
creategrp.add_argument('--jmf', '-j', type=str, default=JMFFILE,
                    help='Provide filename for JMF messages used for submissiuon (default: '+JMFFILE+')')
creategrp.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+JDFFILE+')')
creategrp.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help='Provide URL for PDF starting with either http:// or file://. '+
                    'If file:// is used PDF will be part of mime pacakge (default: '+PDFURL+')')

gathergrp=parser.add_argument_group('Gather arguments', '')
gathergrp.add_argument('--input', '-i', type=str, help='JDF ticket to take as input to create Mime')

mimegrp=parser.add_argument_group('Mime arguments', '')
mimegrp.add_argument('--mime', '-m', type=str, help='Send a mime package to PRISMAsync directly, ')


args = parser.parse_args()
if args.mime:
  QueueEntryID=SendMimeJob(args.url, args.mime)
else:
  QueueEntryID=SendJob(args.url, args.pdf, args.jdf)
if not args.silent :
  print("Job submitted, got QueueEntryID: ", QueueEntryID)
