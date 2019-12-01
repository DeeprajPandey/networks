import socket as skt
from _thread import*
import threading
from datetime import datetime
from operator import itemgetter
import pickle
import schedule
import time

request_queue = []
nums = list([3, 9, 6, 1, 10, 5, 2, 7, 4, 8])

IP = "10.1.16.202"
S1_IP = "10.1.21.15"
S2_IP = "10.1.17.123"
PORT = 8000

# Counter to keep track of the number of times we have sent our request twice
SENT_CTR = 0
# TODO: corner case: if s1 requests twice because s3 didn't request
# check which server is asking (set.unique())

serversocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
serversocket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
serversocket.bind((IP, PORT))

# indices = [i, j]
def swap(indices):
	i = indices[0]
	j = indices[1]

    if i < 10 and j < 10:
        nums[i], nums[j] = nums[j], nums[i]
        # successful swap, valid indi
        return 1
    else:
        return 0

# Use a re-entrant lock in case same thread tries to acquire lock multiple times
q_lock = threading.RLock()

def update_nums(rq1):

    global nums
    global request_queue

    request_queue.append(rq1)
    print(request_queue[0])
    request_queue = sorted(request_queue, key=itemgetter(1))
    
    for tup in request_queue:
        returnval = swap(tup[0])
        
    if SENT_CTR == 2:
        request_queue=[]
        SENT_CTR = 0

def process_client_request(clientsock, addr):
    global SENT_CTR
    global request_queue
    
    data = clientsock.recv(1024).decode()
    data=str(data)
    print("data: " + data)
    if "S" not in data:
        # make a string of the current list of numbers
        number_list = " ".join(str(num) for num in nums)
        # send the list to the client
        clientsock.send(number_list.encode())

        # Expecting "i j" from client now
        data = clientsock.recv(1024).decode()
        # Transform string into list [i, j]
        data = data.split(" ")
        rn = datetime.now().timestamp()
        # tuple of ([i, j], timestamp) representing when server received
        # request to swap ith and jth indices
        swap_req = (data, rn)
        # Acquire lock to append to the request queue
        q_lock.acquire()
        # add a  to request queue
        request_queue.append(swap_req)
        print("Client swap request added to queue.\n")
        q_lock.release()
    elif "S" in data:
        ret_obj = pickle.dumps(request_queue)
        print(ret_obj)
        #send to S1 or S2 depending
        clientsock.send(ret_obj)
        SENT_CTR = SENT_CTR + 1
    else:
        print("Need data! Closing connection with {}\n".format(addr))
    clientsock.close()

    # returning from function kills the thread
    print("Thread closed. Current queue is: {}\n\n".format(str(request_queue)))

#header and server ip
def sync_mode():
    toserver1 = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

    received_queue = list()

    header="S1"
    toserver1.connect((S1_IP,PORT))
    print("Connected to Reuel")
    #send identifying that i am a server
    toserver1.send(header.encode())
    print("Request sent to Reuel")



    #receive the requestq
    rec1 = toserver1.recv(1024)
    data1 = pickle.loads(rec1)
    if len(data1) > 0:
        received_queue = data1

    toserver1.close()
    print("Closed connection with Reuel\n\n")


    toserver2 = skt.socket(skt.AF_INET, skt.SOCK_STREAM)

    header="S2"
    toserver2.connect((S2_IP,PORT))
    print("Connected to Aastha")
    #send identifying that i am a server
    toserver2.send(header.encode())
    print("Request sent to Aastha")

    #receive the requestq
    rec2 = toserver2.recv(1024)
    data2 = pickle.loads(rec2)
    if len(data2) > 0:
        received_queue.append(data1)
        print("")

    toserver2.close()
    print("Closed connection with Aastha\n\n")

    if len(received_queue) > 0:
        print("Received requests from other servers.\nUpdating local list with all requests")
        update_nums(received_queue)
    else:
        print("No request queues from other servers. Business as usual.")
    return

def run_forever():
    print("Sleeping")
    time.sleep(10)
    schedule.every(15).seconds.do(sync_mode)
    print("Calling schedule")
    while True:
        schedule.run_pending()

def Main():
    serversocket.listen(7)
    print("Server is listening...\n")

    start_new_thread(run_forever, ())

    #Start listening to clients
    while True:
        (client, address) = serversocket.accept()
        print("Connected to client ", address[0], ":", address[1])
        start_new_thread(process_client_request, (client, address))
    serversocket.close()

if __name__ == '__main__':
    Main()

