from prismasyncjmfjdf import RemoveQueueEntries
import argparse
import sys
from urllib.parse import urlparse

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
parser.add_argument('--status', '-s', type=str, default=JOBSTATETOREMOVE,
                    help='Status of the jobs that need to be removed. \nTo remove all QueueEntries use: \" \"  To remove multiple statuses use: \"Aborted Completed\"')
parser.add_argument('--id', '-i', type=str, 
                    help='\nA QueuEntryID of a single job')
args = parser.parse_args()


def _fail(message, exit_code=2):
    print(f"Error: {message}")
    sys.exit(exit_code)


def _is_valid_http_url(url_value):
    parsed = urlparse(url_value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


if not _is_valid_http_url(args.url):
    _fail(f"Invalid PRISMAsync URL: {args.url}. Use http://<host>:<port> or https://<host>:<port>")

url=args.url
if args.status is not None and args.id is not None:
    _fail("Provide either --status or --id, not both")

try:
    if args.id is not None:
        QueueEntryID = args.id.strip()
        if not QueueEntryID:
            _fail("QueueEntryID cannot be empty")
        removed = RemoveQueueEntries(url, QueueEntryID=QueueEntryID)
        print(removed, "QueueEntries have been removed")
    elif args.status is not None:
        status = args.status
        removed = RemoveQueueEntries(url, status=status)
        print(removed, "QueueEntries have been removed")
    else:
        _fail("Either --status or --id must be provided")
except ConnectionError as err:
    _fail(f"Network connection error while removing queue entries: {err}", exit_code=1)
except TimeoutError as err:
    _fail(f"Timeout while removing queue entries: {err}", exit_code=1)
except Exception as err:
    _fail(f"Failed to remove queue entries: {err}", exit_code=1)
