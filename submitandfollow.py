from jmfjdf.jmfmessages import SendMime, SendJob, mimeheader_jmf, mimefooter
from re import sub
PRISMAsyncAddress="http://PRISMAsync.cpp.canon:8010"

jmf_message="""<?xml version="1.0" encoding="utf-8"?>
<JMF SenderID="CpcDcm" Version="1.3" TimeStamp="2014-05-28T13:32:12+06:08" xmlns="http://www.CIP4.org/JDFSchema_1_1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Query Type="Status" xsi:type="QueryStatus" ID="QFS150811162034_223_000019">
        <Subscription URL="http://10.93.12.173:9090" />
        <StatusQuParams DeviceDetails="None" JobDetails="Brief" QueueInfo="true" QueueEntryID="QUEUE_ENTRY_ID" />
    </Query>
</JMF>
"""
mimepackage=mimeheader_jmf+jmf_message+mimefooter
QueEntryID=SendJob(PRISMAsyncAddress, "file://jmfjdf/Test.pdf")
mimepackage=sub("QUEUE_ENTRY_ID",QueEntryID,mimepackage)
mime_file = open("file.mime", "w")
mime_file.write(mimepackage)
mime_file.close()
#start hier de website
SendMime(PRISMAsyncAddress,"file.mime")


# wacht tot 