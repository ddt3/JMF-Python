import jmfmessages

printer="http://PRISMAsync.cpp.canon:8010"

print(jmfmessages.RemoveQueueEntries(printer, " "), "QueueEntries have been removed")