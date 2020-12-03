import requests
import xml.dom.minidom
import time
from jmfmessages import SendJob

# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to send jobs to PRISMAsync 

print("Job was submitted and has QueueEntryID:",SendJob("http://hq-cep3.oce.nl:8010", "file://jmfjdf/Test.pdf"))
print("Job was submitted and has QueueEntryID:",SendJob("http://hq-cep3.oce.nl:8010", "http://ubuntu-hdok.ocevenlo.oce.net/pdf/PosterFashionWomanplusTextSample.pdf"))
