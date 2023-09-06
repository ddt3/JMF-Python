"""
This short script removes all queue entries from the printer: PRISMAsync.cpp.canon
"""
from jmfjdf.jmfmessages import RemoveQueueEntries

PRINTER="http://PRISMAsync.cpp.canon:8010"

print(RemoveQueueEntries(PRINTER, " "), "QueueEntries have been removed")
