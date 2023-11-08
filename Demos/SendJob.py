"""
SendJob is een example of how the libraries can be used to submit jobs to PRISMAsync  
"""
from prismasyncjmfjdf import CreateMimePackage, SendJob, SendMime
from pathlib import Path

# First determine path of *this* file
basepath=Path(__file__).resolve().parent
# look for .config folder in same folder as *this* file 
ConfigDir=str(basepath.joinpath(".config"))


# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to send jobs to PRISMAsync

# Make sure to adapt these lines to your situation: provide PRISMAsync address and web-url to PDF file  before running this python file
PRISMASYNCADDRESS="http://PRISMAsync.cpp.canon:8010"
# Submit a PDF file as a mime package, template JDF & JMF are used
print("Job was submitted and has QueueEntryID:",SendJob(PRISMASYNCADDRESS,
      "file://"+ConfigDir+"/Test.pdf"))
# Submit a PDF file using a URL, template JDF & JMF are used
print("Job was submitted and has QueueEntryID:",SendJob(PRISMASYNCADDRESS,
      "http://ubuntu-hdok.ocevenlo.oce.net/pdf/PosterFashionWomanplusTextSample.pdf"))
# Submit a PDF file using a URL and provide a JDF, template JMF is used
print("Job was submitted and has QueueEntryID:",SendJob(PRISMASYNCADDRESS,
      "file://"+ConfigDir+"/Test.pdf", ConfigDir+"/Template.jdf" ))
# Create a mimepackage file and send it
print("Job was submitted and has QueueEntryID:",SendMime(PRISMASYNCADDRESS,
         CreateMimePackage(ConfigDir+"/SubmitQueueEntry.jmf",ConfigDir+"/Template.jdf", "file://"+ConfigDir+"/Test.pdf")))
