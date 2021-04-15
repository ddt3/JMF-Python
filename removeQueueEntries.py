from jmfjdf.jmfmessages import RemoveQueueEntries
import argparse

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010. make sure to enable jmf support in the PRISMAsync settings editor
PrinterUrl="http://PRISMAsync.cpp.canon:8010"

# Provide the States to filter QueueIDs, possible states: Aborted, Held, Completed. States can be combined, eg "Held Completed"
# To not use any filtering make sure to leave it empty: " "
QueueIDState="Aborted"

# The following block is used to take command line options for this tool.
# It needs a printer address and an  opional --status. --help is automatically generated
parser = argparse.ArgumentParser(description='Remove all JMF QueueEntries with the provided status from PRISMAsync.')
parser.add_argument('--url', type=str, default=PrinterUrl,
                    help='full url to PRISMAsync jmf interface. (default: '+PrinterUrl+')')
parser.add_argument('--status', '-s', type=str, default=QueueIDState,
                    help='The status of the jobs that need to be removed or listed. To remove all QueueEntries use: \" \"  To remove multiple statuses use: \"Aborted Completed\" (default: '+QueueIDState+')')
args = parser.parse_args()
url=args.url
status=args.status

print(RemoveQueueEntries(url, status), "QueueEntries have been removed")