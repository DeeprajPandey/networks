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

IP = "10.1.16.202"
S1_IP = "10.1.21.15"
S2_IP = "10.1.56.110"
PORT = 8001

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

		# data = ('SERVER', ([i, j], timestamp))
		# data = ('CLIENT', 'i j')
		data_obj = c.recv(block_size)
		data = pickle.loads(data_obj)
		header = data[0]

		if (header == 'C'):
			logging.debug("Received data from client.")
			current_nums = " ".join(str(num) for num in nums)
			c.send(current_nums.encode())

			ij = data[1]
			ij = ij.split(" ")
			rn = datetime.now().timestamp()

			# tuple of ([i, j], timestamp) representing when server received
			# request to swap ith and jth indices
			swap_req = (ij, rn)
			# put the current request on the queue
			requests_q.put(swap_req)

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
				toserver2.connect((S1_IP,PORT))

			except socket.timeout as e:
				logging.debug("{} connecting to Reuel, check if he's sleeping.\n".format(e))

			else:
				logging.debug("Sending client data to Aastha")
				toserver2.send(pickle.dumps(tosend))
				toserver2.close()
				logging.debug("\tClosed connection with AASTHA\n")

		elif ('S' in header):
			logging.debug("Received data from {}. Adding to queue.".format(header))
			new_req = pickle.loads(data[1])
			requests_q.put(new_req)
		else:
			logging.debug("\tNeed data! Closing connection with {}\n".format(addr))

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

		all_requests = sorted(all_requests, key=itemgetter(1))
		for tup in all_requests:
			returnval = self.swap(tup[0])
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

if __name__ == "__main__":
	ThreadedServer().listen()