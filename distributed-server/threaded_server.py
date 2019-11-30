import socket as skt
from _thread import*
import threading
from datetime import datetime

request_queue = list()
nums = list([3, 9, 6, 1, 10, 5, 2, 7, 4, 8])

IP = skt.gethostname()
PORT = 8000

serversocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
serversocket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
serversocket.bind((IP, PORT))

def swap(i, j):
    if i < 10 and j < 10:
        nums[i], nums[j] = nums[j], nums[i]
        # successful swap, valid indi
        return 1
    else:
        return 0

# Use a re-entrant lock in case same thread tries to acquire lock multiple times
q_lock = threading.RLock()

def update_nums(rq1, rq2):

    request_queue.append(rq1)
    request_queue.append(rq2)

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
    print("data: " + str(data))
    if data:
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
    else:
        print("Need data! Closing connection with {}\n".format(addr))
    clientsock.close()

    # returning from function kills the thread
    print("Thread closed. Current queue is: {}\n\n".format(str(request_queue)))

def sync_mode():
    


def Main():
    serversocket.listen(7)
    print("Server is listening...\n")

    while True:
        (client, address) = serversocket.accept()
        print("Connected to client ", address[0], ":", address[1])
        start_new_thread(process_client_request, (client, address))
        
    serversocket.close()


if __name__ == '__main__':
    Main()
