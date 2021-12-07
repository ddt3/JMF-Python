"""
Contains an example on how jmfmessasge module can be used to remove all queue entries
"""
from jmfjdf.jmfmessages import RemoveQueueEntries

printer="http://PRISMAsync.cpp.canon:8010"

print(RemoveQueueEntries(printer, " "), "QueueEntries have been removed")
