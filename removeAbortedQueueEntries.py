from jmfjdf.jmfmessages import RemoveQueueEntries

printer="http://PRISMAsync.cpp.canon:8010"

print(RemoveQueueEntries(printer, "Aborted"), "QueueEntries have been removed")