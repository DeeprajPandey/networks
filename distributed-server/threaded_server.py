import socket as skt
from _thread import*
import threading
from datetime import datetime
import pickle
import schedule

request_queue = []
nums = list([3, 9, 6, 1, 10, 5, 2, 7, 4, 8])

HOST_IP = skt.gethostname()
S1_IP = "10.1.0.100"
S2_IP = "10.1.0.100"
PORT = 8000

serversocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
serversocket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
serversocket.bind((IP, PORT))


clientsocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)


def swap(i, j):
    if i < 10 and j < 10:
        nums[i], nums[j] = nums[j], nums[i]
        # successful swap, valid indi
        return 1
    else:
        return 0

# Use a re-entrant lock in case same thread tries to acquire lock multiple times
q_lock = threading.RLock()

def update_nums(rq1):

    request_queue.append(rq1)

    request_queue = sorted(request_queue, key=itemgetter(1))
    for i in range(len(request_queue)):
        tuple_to_swap = i[0]
        temp = nums[tuple_to_swap[0]]
        nums[tuple_to_swap[0]] = nums[tuple_to_swap[1]]
        nums[tuple_to_swap[1]] = temp
    request_queue=[]

    return nums

def process_client_request(clientsock, addr):
    # make a string of the current list of numbers
    number_list = " ".join(str(num) for num in nums)
    # send the list to the client
    clientsock.send(number_list.encode())

    # Expecting "i j" from client now
    data = clientsock.recv(1024).decode()
    data=str(data)
    print("data: " + data)
    if "S" not in data:
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
        #send to S1 or S2 depending
    else:
        print("Need data! Closing connection with {}\n".format(addr))
    clientsock.close()

    # returning from function kills the thread
    print("Thread closed. Current queue is: {}\n\n".format(str(request_queue)))

#header and server ip
def sync_mode():

    header="S1"
    clientsocket.connect((S1_IP,PORT))
    #send identifying that i am a server
    clientsocket.send(header.encode())
    #receive the requestq
    s_rq=clientsocket.recv(1024).decode()
    clientsocket.close()

    header="S2"
    clientsocket.connect((S2_IP,PORT))
    #send identifying that i am a server
    clientsocket.send(header.encode())
    #receive the requestq
    s_rq.append(clientsocket.recv(1024).decode())
    clientsocket.close()

    update_nums(s_rq)

def Main():
    serversocket.listen(7)
    print("Server is listening...\n")
    schedule.every(15).seconds.do(sync_mode())

    #Start listening to clients
    while True:
        (client, address) = serversocket.accept()
        print("Connected to client ", address[0], ":", address[1])
        start_new_thread(process_client_request, (client, address))
    serversocket.close()


if __name__ == '__main__':
    Main()
