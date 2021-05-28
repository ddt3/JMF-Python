"""
Contains a number of examples on how PRISMAsync jmf/jdf can be used for e.g. job management and printer status
"""
import base64
import re
import sys
import time
import uuid
import xml.dom.minidom
import requests
from base64io import Base64IO
from pathlib import Path

# a few files are needed as part, using pathlib, so it will work on both Windows and linux
basepath=Path(__file__).resolve().parent
jmf_QueueStatus_msg=basepath.joinpath("QueueStatus.jmf")
jmf_SubmitQueueEntry_msg=basepath.joinpath("SubmitQueueEntry.jmf")
jmf_RemoveQueueEntry_msg=basepath.joinpath("RemoveQueueEntry.jmf")
jdf_template=basepath.joinpath("Template.jdf")

# This library contains contains examples of how jmf can be used to send command to PRISMAsync and obtain information from PRISMAsync
# All jmf messages are send mime-encoded. Note that no libary is used for mime-encoding, messages are mime-encoded "by hand"


# Mime header used for sending jmf
mimeheader_jmf = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="I_Love_PRISMAsync"

--I_Love_PRISMAsync
Content-ID: part1@cpp.canon
Content-Type: application/vnd.cip4-jmf+xml
content-transfer-encoding:7bit 
Content-Disposition: attachment

"""

# Mime header used for sending jdf
mimeheader_jdf = """
--I_Love_PRISMAsync
Content-ID: part2@cpp.canon 
content-transfer-encoding:7bit 
content-type: application/vnd.cip4-jdf+xml; charset="us-ascii" 
content-disposition: attachment; filename="Ticket.jdf"

"""
# Mime header used for sending pdf
mimeheader_pdf = """
--I_Love_PRISMAsync
Content-ID: part3@cpp.canon
Content-Type: application/octet-stream; name=Job1.pdf
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=Job1.pdf

"""

# Mime Footer
mimefooter = """
--I_Love_PRISMAsync--"""


def read_jmfjdf (message_file):
  """Read a jmf or jdf file from disk into a string

    Parameters:
    Filename

    Returns:
    string:Content of file

  """
  try:

    file = open(message_file)
    message=file.read()
    file.close
  except :
    print ("ERR: Trouble reading: ", message_file)
    exit()
  return message
  
def read_pdf (pdf_file):
  try:

    file = open(pdf_file)
    pdf=file.read()
    file.close
  except :
    print ("ERR: Trouble reading: ", pdf_file)
    exit()
  return pdf

def ReturnQueueEntries (url, status):
  """Return all queue entries with the given states

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    status: states that need to be reported (e.g. "Completed Aborted") use " " to not filter at all and receive all queue entries

    Returns:
    array of QueueEntryIDs

  """
  headers={'Content-Type': 'multipart/related'}
  # Create a jmf message to retrieve the queue status that Filters on job status, it is allowed to mention multiple job statuses   
  
  jmf_message=read_jmfjdf(jmf_QueueStatus_msg)
  jmf_message=jmf_message.replace("STATUS",status)
  data=mimeheader_jmf+jmf_message+mimefooter

  try:
    response=requests.post(url=url,data=data,headers=headers)
    root = xml.dom.minidom.parseString(response.content)
  except:
    print("Unexpected reply from", url)
    print(sys.exc_info()[0], "occurred.")
    return 0
  Entries=root.getElementsByTagName("QueueEntry")
  id_array=[]
  for qid in Entries:
    id_array.append(qid.getAttribute("QueueEntryID"))
  return id_array

example_job="cid:Job1.pdf"

def RemoveQueueEntries (url, status):
  """Removes all queue entries with the given states

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    status: String of job states. Jobs in this state will be removed: (e.g. "Completed Aborted")

    Returns:
    int:Number of removed queueentries

  """
  # First request QueueEntryIDs having a specific state
  queue_ids=ReturnQueueEntries(url,status)
  nrjobs=len(queue_ids)
  if nrjobs:  
    to_delete=""
    # Add a line mentioning the QueueEntryID for each found QueueEntryID
    for i in range(nrjobs):
      to_delete+="<QueueEntryDef QueueEntryID=\""+queue_ids[i]+"\" />\n"

    # Read a  template RemoveQueueEntry jmf message 
    jmf_message=read_jmfjdf(jmf_RemoveQueueEntry_msg) 
    # In this template replace QueueEntryID line with the QueueEntryIDs to_delete
    jmf_message=jmf_message.replace("<QueueEntryDef QueueEntryID=\"QUEUEENTRY\" />",to_delete)
    headers={'Content-Type': 'multipart/related'}
    # Wrap jmf message in mime
    deletemessage=mimeheader_jmf+jmf_message+mimefooter
    
    try:
      # Send delete message to PRISMAsync and wait for response
      delresponse =  requests.post(url=url,data=deletemessage, headers=headers)
      root = xml.dom.minidom.parseString(delresponse.content)
    except:
      print("Unexpected reply from", url)
      print(sys.exc_info()[0], "occurred.")
      return 0
    # WHY?
    entries=root.getElementsByTagName("Comment")
    if  entries:
      for qid in entries:
        print(qid.firstChild.nodeValue)
        nrjobs-=1
    return nrjobs

def CreateMimePackage (jmf_file, jdf_file,pdf_url) :
  """Creates a mime pacakge from the provided files

    Parameters:
    jmf_file: Path to jmf file (first file in mime)
    jdf_file: Path to jdf file (second file in mime)
    pdf_url:  Url to PDF file. 
              use file:// url to base64 encode the PDF and add it to the mime package (third file in mime)
              in all other cases the pdf_url will be used for JDF FileSpec URL
    Returns:
    Filename of created mime package 
  """
  # unique_filename = str(uuid.uuid4())+".mjm"
  encoded_filename="EN-"+str(uuid.uuid4())

  # First determine if PDF needs to be included in mime of referenced by url 
  # If it needs to be included in mime: encode the PDF in base64 format
  sendmime="file://" in pdf_url
  pdf_file=str(pdf_url).replace("file://","")
  if sendmime:
    #PDF needs to be read from disk using filename provided
    try:
      with open(pdf_file, "rb") as source, open(encoded_filename, "wb") as target:
          # Create base64 encoded file from PDF
          with Base64IO(target) as encoded_target:
              for line in source:
                  encoded_target.write(line)
    except:
      print("File", sendmime, "could not be opened")
      return ""

  else:
    pass
    #PDF file is referred to using https, no additional actions needed

  # Now create complete mime package in 2 parts (without base64 PDF) or 3 parts (with base64 PDF)
  time_string=time.strftime('%Y-%m-%d_%H-%M-%S')
  i=0  
  unique_filename = time_string+"_"+str(i)+".mjm"
  while Path(unique_filename).exists():
    i+=1
    unique_filename=time_string+"_"+str(i)+".mjm"
  
  with open(unique_filename, 'w') as outfile:
    # Part 1: JMF messages 
    # Start with JMF mimeheader
    outfile.write(mimeheader_jmf)
    # Add jmf file
    with open(jmf_file,'r') as tempfile:
      jmf_message=tempfile.read()
      # In this JMF message, include refrence to JDF file: JDF file is part2 of this mime pacakge. 
      jmf_message=re.sub("URL=\".*\"","URL=\"cid:part2@cpp.canon\"",jmf_message)
    outfile.write(jmf_message)
    
    # Part 2: JDF ticket
    # Start with JDF mimeheader
    outfile.write(mimeheader_jdf)
    # Add jdf file
    with open(jdf_file, 'r') as tempfile:
      jdf_message=tempfile.read()
      # In this JDF ticket, include refrence to PDF file: PDF file is either part3 of this mime pacakge or reference to using url. 
      if sendmime :
        jdf_message=re.sub("URL=\".*\"","URL=\"cid:part3@cpp.canon\"",jdf_message)
      else :
        jdf_message=re.sub("URL=\".*\"","URL=\""+pdf_url+"\"",jdf_message)
      
      #Adding the current time to the JDF ticket ID and PARTID, to make job easy to find in PRISMAsync jmf logging.
      jdf_message=jdf_message.replace("REPLACE_ID",time.asctime())
      jdf_message=jdf_message.replace("REPLACE_JOBID",pdf_url.rsplit('/', 1)[-1])
      jdf_message=jdf_message.replace("REPLACE_JOBPARTID",time.asctime())
    outfile.write(jdf_message)

    # Part 3: PDF file
    if sendmime :
      # Needs to be send in mime package, adding it
      # Start with PDF mimeheader
      outfile.write(mimeheader_pdf)
      # Add pdf file
      with open(encoded_filename,'r') as tempfile:
        for line in tempfile:
          outfile.write(line)
      Path(encoded_filename).unlink()
    outfile.write(mimefooter)

  #outfile closed, return mime file name
  return unique_filename

def SendJob(url,pdfurl, *jdf_file_param):
  """Sends a job to the given url

    Parameters:
    url: full link to printer jmf interface e.g. http://prismasync.lan:8010
    pdf: URL for PDF file to be send (either file: or http: URL )
    optional: path to JDF file, if this parameter is not provided , Template.jdf is used.

    Returns:
    id:QueueEntryID of submitted job

  """
  # First the mime package for submission is created
  if jdf_file_param:
    jdf_file=jdf_file_param[0]
  else:
    jdf_file=jdf_template

  mime_file=CreateMimePackage(jmf_SubmitQueueEntry_msg,jdf_file,pdfurl)
  id_array=SendMimeJob(url,mime_file)
  if id_array :
    Path(mime_file).unlink()
    return id_array
  else:
    return 0

def SendMimeJob(url,mime_file):
  """Sends a mime file to the given url

    Parameters:
    url: Full link to printer jmf interface e.g. http://prismasync.lan:8010
    mime_file: Path to mime file mime (containing JMF,JDF and optionally a PDF).

    Returns:
    id:QueueEntryID of submitted job

  """  
  with open(mime_file,'r') as datafile:
    headers={'Content-Type': 'multipart/related'}
    try:
      # Submit the mime message to PRISMAsync and wait for the response
      response=requests.post(url=url, data=datafile.read(), headers=headers)
      root = xml.dom.minidom.parseString(response.content)
    except:
      print("Unexpected reply from", url)
      print(sys.exc_info()[0], "occurred.")
      return 0
    # When submission is successfull reply JMF will contain submitted queueentries, the latest QueueEntryID is the one just submitted, return this id.
    try:
      Entries=root.getElementsByTagName("QueueEntry")
      return_id_array=Entries[0].getAttribute("QueueEntryID")
    except:
      print ("Job could not be submitted keeping mime package:",mime_file )
      print ("PRISMAsync returned: \"", root.getElementsByTagName("Comment")[0].firstChild.nodeValue, "\"")
      
      return 0
    return return_id_array
