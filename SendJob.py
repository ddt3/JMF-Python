import ipaddress
from jmfjdf.jmfmessages import CreateMimePackage, SendJob, SendMime

# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to send jobs to PRISMAsync 

# Make sure to adapt these lines to your situation: provide PRISMAsync address and web-url to PDF file  before running this python file
PRISMAsyncAddress="http://PRISMAsync.cpp.canon:8010"
# Submit a PDF file as a mime package, template JDF & JMF are used
print("Job was submitted and has QueueEntryID:",SendJob(PRISMAsyncAddress, "file://jmfjdf/Test.pdf"))
# Submit a PDF file using a URL, template JDF & JMF are used
print("Job was submitted and has QueueEntryID:",SendJob(PRISMAsyncAddress, "http://ubuntu-hdok.ocevenlo.oce.net/pdf/PosterFashionWomanplusTextSample.pdf"))
# Submit a PDF file using a URL and provide a JDF, template JMF is used
print("Job was submitted and has QueueEntryID:",SendJob(PRISMAsyncAddress, "file://jmfjdf/Test.pdf", "jmfjdf/Template.jdf" ))
# Create a mimepackage file and send it
SendMime(PRISMAsyncAddress,CreateMimePackage("jmfjdf/SubmitQueueEntry.jmf","jmfjdf/Template.jdf", "file://jmfjdf/Test.pdf"))