import jmfmessages

printer="http://PRISMAsync.cpp.canon:8010"

print(jmfmessages.RemoveQueueEntries(printer, "Aborted"), "QueueEntries have been removed")