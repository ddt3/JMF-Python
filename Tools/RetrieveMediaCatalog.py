import requests, sys, argparse, socket
from pathlib import Path

# Write response to a folder called _received
# pathlib is used to make sure this works on linux and Windows
basepath=Path(__file__).resolve().parent
logdir=basepath.joinpath("_received")
# create folder if it does not exist
logdir.mkdir(parents=True, exist_ok=True)


#Mime header
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


# Actual JMF message to query-resource
jmf_subscribe="""<?xml version="1.0" encoding="UTF-8"?>
<JMF xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SenderID="HDOK Python" TimeStamp="2022-07-21T13:30:23+02:00" Version="1.3">
  <Query ID="MYQUERY_20220721133023" Type="Resource" xsi:type="QueryResource">
    <ResourceQuParams Classes="Consumable Handling" Exact="true" />
  </Query>
</JMF>
"""

def retrieve_media_catalog(url):
  """Retrieve the media catalog from PRISMAsync with url

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    
    Returns:
    
  """
  headers={'Content-Type': 'multipart/related'}
  # Create a jmf message to retrieve the media catalog   
  data=mimeheader_jmf+jmf_subscribe+mimefooter
  try:
    response=requests.post(url=url,data=data,headers=headers)
  except:
    print("Unexpected reply from", url)
    print(sys.exc_info()[0], "occurred.")
    return -1
  return response
filename=logdir.joinpath("media.xml")

with open(filename, 'wb') as f:
            f.write(retrieve_media_catalog("http://fat-cep-620.ocevenlo.oce.net:8010").content)