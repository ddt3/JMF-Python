import jmfmessages
import config
print(jmfmessages.RemoveQueueEntries(config.url, config.status), "QueueEntries have been removed")