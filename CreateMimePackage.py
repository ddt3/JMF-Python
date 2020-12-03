import requests
import xml.dom.minidom
import time
from jmfmessages import CreateMimePackage

# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to create a full mime package (including PDF)

print("Mime-package created with filename:",CreateMimePackage("jmfjdf/SubmitQueueEntry.jmf","jmfjdf/job1.jdf", "file://jmfjdf/Test.pdf"))
