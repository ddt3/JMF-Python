from prismasyncjmfjdf import RemoveQueueEntries
import argparse

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010. make sure to enable jmf support in the PRISMAsync settings editor
PRISMASYNCADDRESS = "http://PRISMAsync.cpp.canon:8010"

# Provide the States to filter QueueIDs, possible states: Aborted, Held, Completed. States can be combined, eg "Held Completed"
# To not use any filtering make sure to leave it empty: " "
JOBSTATETOREMOVE = "Aborted"

# The following block is used to take command line options for this tool.
# It needs a printer address and an  opional --status. --help is automatically generated
parser = argparse.ArgumentParser(description='Remove all JMF QueueEntries with the provided status from PRISMAsync.')
parser.add_argument('--url', type=str, default=PRISMASYNCADDRESS,
                    help='Full url to PRISMAsync jmf interface. (default: '+PRISMASYNCADDRESS+')')
parser.add_argument('--status', '-s', type=str, 
                    help='Status of the jobs that need to be removed. \nTo remove all QueueEntries use: \" \"  To remove multiple statuses use: \"Aborted Completed\"')
parser.add_argument('--id', '-i', type=str, 
                    help='\nA QueuEntryID of a single job')
args = parser.parse_args()
url=args.url
if args.status is not None and args.id is None:
    status=args.status
    print(RemoveQueueEntries(url, status=status), "QueueEntries have been removed")
elif args.status is None and args.id is not None:
    QueueEntryID=args.id
    print(RemoveQueueEntries(url, QueueEntryID=QueueEntryID), "QueueEntries have been removed")
else:
    parser.error('Wrong arguments passed')
