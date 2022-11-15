"""This example does not need the jmfpython library , but parts of it are copied here. A JMF message is sent to subscribe to QueueStatus. 
The information send by PRISMAsync is retrieved by a simple webserver. Queue information is send to file.

This simple example could be used as a starting point for workflows based on jmf subscxriptions
"""
import time
from uuid import uuid1
import requests, sys, argparse, socket
from pathlib import Path
basepath=Path(__file__).resolve().parent
logdir=basepath.joinpath("_response")
logdir.mkdir(parents=True, exist_ok=True)



# Defaults
time_string=time.strftime('%Y-%m-%d_%H-%M-%S')
i=uuid1()  
unique_filename = "response-" +time_string+".xml"
Resultfile=logdir.joinpath(unique_filename)

PrinterUrl="http://PRISMAsync.cpp.canon:8010"

# Parse command line arguments
parser = argparse.ArgumentParser(description='Subscribe to QueueStatus of PRISMAsync ')
parser.add_argument('--url', type=str, default=PrinterUrl,
                    help='full url to PRISMAsync jmf interface. (default: '+PrinterUrl+')')
parser.add_argument('--output',  type=str, default=str(Resultfile),
                    help='Provide filename to write response from PRISMAsync (default: '+str(Resultfile)+')')
parser.add_argument('jmf_file', type=str,
                    help='File path to jmf file')
parser.add_argument('--debug', '-s', action='store_true',
                    help='Do not print any output just subscribe and write to ' +str(Resultfile))
args = parser.parse_args()

# Standard mime headers and JMF messages
mimeheader_jmf = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="I_Love_PRISMAsync"

--I_Love_PRISMAsync
Content-ID: part1@cpp.canon
Content-Type: application/vnd.cip4-jmf+xml
content-transfer-encoding:7bit 
Content-Disposition: attachment

"""

# Mime Footer
mimefooter = """
--I_Love_PRISMAsync--"""

def log(s):
    if args.debug:
        print(s)


def send_jmf(url,jmf_file):
  """Send a jmf  message to PRISMAsync with url

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    
    Returns:
    
  """
  headers={'Content-Type': 'multipart/related'}
  # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses   
  with open(jmf_file,'r') as tempfile:
      jmf_message=tempfile.read()
  data=mimeheader_jmf+jmf_message+mimefooter
  try:
    response=requests.post(url=url,data=data,headers=headers)
  except:
    print("Unexpected reply from", url)
    print(sys.exc_info()[0], "occurred.")
    return -1
  return response



result=send_jmf(args.url,args.jmf_file)

if result != -1:
  data=result.content
  with open(args.output,'wb') as resultfile:
    resultfile.write(data)
  log(data.decode())
else:
    print("Send failed")