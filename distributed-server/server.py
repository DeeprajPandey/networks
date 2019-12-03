import threading
import socket
import queue
import os

import logging

import time
import pickle
import schedule
from datetime import datetime
from operator import itemgetter

logging.basicConfig(level=logging.DEBUG,
					format='(%(threadName)-9s) %(message)s',)
## lower the number, lower is priority
# 0 = min. priority
# 0 < 1 < 2 ...
client_priority_dict = {
	"10.1.56.110": 1,
	"10.1.21.15": 2
}

IP = "10.1.16.202"
S1_IP = "10.1.21.15"
S2_IP = "10.1.56.110"
PORT = 8001
nums = list([3, 9, 1, 8, 10, 7, 2, 5, 6, 4])

class ThreadedServer():
	def __init__(self):
		self.host = IP
		self.port = 8001
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #the SO_REUSEADDR flag tells the kernel to
		self.s.bind((self.host, self.port))

	def listen(self):
		self.s.listen(7)
		logging.debug('Server is listening...\n\n')
		requests = queue.Queue()

		# This should start only when all 3 servers are up
		sched = threading.Thread(target = self.run_forever, args = (requests,))
		sched.setName('scheduler')
		sched.start()
		
		while True:
			c, addr = self.s.accept()
			c.settimeout(60)
			# start a new thread with the function that handles client
			ch = threading.Thread(target = self.handleClient,args = (c, addr, requests))
			ch.setName('clientHandler')
			ch.start()

	def handleClient(self, c, addr, requests_q):
		block_size = 1024
		# thread_id = threading.current_thread().ident() # get id assigned by kernel
		logging.debug('Connected to client {}'.format(addr))

		# data = ('SERVER', ([i, j], timestamp, addr))
		# data = ('CLIENT', 'i i')
		data_obj = c.recv(block_size)
		data = pickle.loads(data_obj)
		header = data[0]

		if (header == 'C'):
			logging.debug("Received data from client.")
			current_nums = " ".join(str(num) for num in nums)
			c.send(current_nums.encode())

			ij = c.recv(block_size).decode()
			ij = ij.split(" ")
			rn = datetime.now().timestamp()

			priority = self.get_priority(str(addr))
			# tuple of ([i, j], timestamp, priority) goes to request queue
			swap_req = (ij, rn, priority)
			requests_q.put(swap_req)

			# but tuple of ([i, j], timestamp, client_ip_address) goes to other servers
			swap_req = (ij, rn, str(addr))
			# send this to S1 and S2
			tosend = ("SD", swap_req)
			
			toserver1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			toserver2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			toserver1.settimeout(3)
			toserver2.settimeout(3)

			try:
				toserver1.connect((S1_IP,PORT))

			except socket.timeout as e:
				logging.debug("{} connecting to Reuel, check if he's sleeping.\n".format(e))

			else:
				logging.debug("Sending client data to Reuel")
				toserver1.send(pickle.dumps(tosend))
				toserver1.close()
				logging.debug("\tClosed connection with REUEL\n")

			try:
				toserver2.connect((S2_IP,PORT))

			except socket.timeout as e:
				logging.debug("{} connecting to Aastha, check if she's sleeping.\n".format(e))

			else:
				logging.debug("Sending client data to Aastha")
				toserver2.send(pickle.dumps(tosend))
				toserver2.close()
				logging.debug("\tClosed connection with AASTHA\n")

		elif ('S' in header):
			logging.debug("Received data from {}. Adding to queue.".format(header))
			# new_req is ([i, j], timestamp, client_ip_addr)
			recv_req = data[1]

			# get the priority of this ip
			new_priority = self.get_priority(recv_req[2])

			# we can't change recv_req[2] as it's a tuple
			# so, create a new tuple and put the priority instead of IP
			new_req = (recv_req[0], recv_req[1], new_priority)
			requests_q.put(new_req)
		else:
			logging.debug("\tNeed data! Closing connection with {}\n".format(addr))
		return

	def update_nums(self, requests_q):
		if requests_q.empty():
			logging.debug("Request queue is empty, exiting update_nums.")
			return
		logging.debug("Starting update_nums")
		all_requests = list()
		
		while (not requests_q.empty()):
			all_requests.append(requests_q.get())
		requests_q.task_done()
		logging.debug("Let go of queue, starting swap.")
		logging.debug("Size of the queue (should be 0) is {}".format(requests_q.qsize()))
		logging.debug("Local copy of queue is {}".format(str(all_requests)))


		all_requests = sorted(all_requests, key=itemgetter(1))
		all_requests = sorted(all_requests, key=itemgetter(2), reverse = True)
		for tup in all_requests:
			returnval = self.swap(tup[0])
		logging.debug(str(nums))
		logging.debug("End of update_nums.")

	def run_forever(self, requests_q):
		logging.debug("Waking up...")
		schedule.every(10).seconds.do(self.update_nums, requests_q)
		logging.debug("Calling schedule")
		while True:
			schedule.run_pending()

	def swap(self, indices_to_swap):
		global nums
		i = int(indices_to_swap[0])
		j = int(indices_to_swap[1])
		if i < 10 and j < 10:
			nums[i], nums[j] = nums[j], nums[i]
			# successful swap, valid indi
			return 1
		else:
			return 0

	### returns the agreed priority (common to all servers) of a client_ip
	def get_priority(self, client_ip):
		# if the client ip is registered on the server's priority dictionary
		if (client_ip in client_priority_dict.keys()):
			# priority is whatever was agreed upon
			return client_priority_dict[client_ip]
		else:
			# priority is lowest (0)
			return 0

if __name__ == "__main__":
	ThreadedServer().listen()