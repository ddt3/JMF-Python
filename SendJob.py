import requests
import xml.dom.minidom
import time
from jmfmessages import SendJob

# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to send jobs to PRISMAsync 

# Make sure to adapt these lines to your situation: provide PRISMAsync address and web-url to PDF file  before running this python file

# Submit a PDF file as a mime package, template JDF & JMF are used
print("Job was submitted and has QueueEntryID:",SendJob("http://PRISMAsync.cpp.canon:8010", "file://jmfjdf/Test.pdf"))
# Submit a PDF file using a URL, template JDF & JMF are used
print("Job was submitted and has QueueEntryID:",SendJob("http://PRISMAsync.cpp.canon:8010", "http://ubuntu-hdok.ocevenlo.oce.net/pdf/PosterFashionWomanplusTextSample.pdf"))
# Submit a PDF file using a URL and provide a JDF, template JMF is used
print("Job was submitted and has QueueEntryID:",SendJob("http://PRISMAsync.cpp.canon:8010", "file://jmfjdf/Test.pdf", "jmfjdf/Template.jdf" ))

