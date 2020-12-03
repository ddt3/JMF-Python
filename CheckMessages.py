import time,jmfmessages
nroftest = 30
nrofthreads = 30

def loopqueue ():
    for x in range(nroftest):
        start_time = time.time()
        nrentries=len(jmfmessages.ReturnQueueEntries(printer," "))
        timeused=time.time()-start_time
        print("Time:",start_time,"ReturnQueueEntries:",nrentries,"Pass:",x+1,"Time:",timeused)
def sendjob ():
    for x in range(nroftest):
        start_time = time.time()
        nrentries=jmfmessages.SendJob(printer)
        timeused=time.time()-start_time
        print("Time:",start_time,"SendJob:",nrentries,"Pass:",x+1, timeused)
 
printer="http://fat-cep-601.ocevenlo.oce.net:8010"

# print("SendJob:",jmfmessages.SendJob(printer,1,1))
# print("ReturnQueueEntries",len(jmfmessages.ReturnQueueEntries(printer," ")))

from threading import Thread

if __name__ == '__main__':
    list_threads = []
    for tnr in range (0,nrofthreads): 
        t1 = Thread(target = sendjob)
        t2 = Thread(target = loopqueue)
        list_threads.append(t1)
        list_threads.append(t2)
    for t in list_threads:
        t.start()
    for t in list_threads:
        t.join()

print("Removed:",jmfmessages.RemoveQueueEntries(printer, " "))