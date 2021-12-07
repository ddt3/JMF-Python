"""
Contains an example on how jmfmessasge module can be used to remove aborted queue entries
"""

from jmfjdf.jmfmessages import RemoveQueueEntries

printer="http://PRISMAsync.cpp.canon:8010"

print(RemoveQueueEntries(printer, "Aborted"), "QueueEntries have been removed")
