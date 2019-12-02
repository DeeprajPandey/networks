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

request_queue = []
nums = list([3, 9, 6, 1, 10, 5, 2, 7, 4, 8])

IP = "10.1.16.202"
S1_IP = "10.1.21.15"
S2_IP = "10.1.17.123"
PORT = 8000

SENT_CTR = 0

class ThreadedServer():
	def __init__(self):
		self.host = IP
		self.port = 8000
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #the SO_REUSEADDR flag tells the kernel to
		self.s.bind((self.host, self.port))

	def listen(self):
		self.s.listen(7)
		logging.debug('Server is listening...\n\n')
		for_sending = queue.Queue()

		sched = threading.Thread(target = self.run_forever, args = (for_sending,))
		sched.setName('scheduler')
		sched.start()
		# to check if there are no items in queue
		# queue.get() will run forever if tried on empty list
		
		while True:
			c, addr = self.s.accept()
			c.settimeout(60)
			# start a new thread with the function that handles client
			ch = threading.Thread(target = self.handleClient,args = (c, addr, for_sending))
			ch.setName('clientHandler')
			ch.start()

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

	def update_nums(self, received, for_sending):
		global SENT_CTR
		global nums
		global request_queue

		if len(request_queue)==0 and len(received)==0:
			return
		
		for_sending.put(request_queue)
		for_sending.put(request_queue)

		request_queue.extend(received)
		
		request_queue = sorted(request_queue, key=itemgetter(1))
		for tup in request_queue:
			returnval = self.swap(tup[0])
		request_queue=[]


	def handleClient(self, c, addr, for_sending):
		global SENT_CTR
		global request_queue
		global nums

		block_size = 1024
		# thread_id = threading.current_thread().ident() # get id assigned by kernel
		logging.debug('Connected to {}'.format(addr))

		# this is either of {'CLIENT', 'S1', 'S2'}
		data = c.recv(block_size).decode()

		if (data == 'CLIENT'):
			current_nums = " ".join(str(num) for num in nums)
			c.send(current_nums.encode())

			ij = c.recv(block_size).decode()
			ij = ij.split(" ")
			rn = datetime.now().timestamp()

			# tuple of ([i, j], timestamp) representing when server received
			# request to swap ith and jth indices
			swap_req = (ij, rn)
			request_queue.append(swap_req)
			logging.debug("Client swap request added to queue.\n")
			# concurrent_req_queue.put(swap_req_item)
			# logging.debug('Added {} to concurrent request queue'.format(swap_req_item))
			# concurrent_req_queue.task_done()
		elif ('S' in data):
			if not for_sending.empty():
				logging.debug("Q before popping: {}".format(for_sending.qsize()))
				temp=for_sending.get()
				logging.debug("Q after popping: {}".format(for_sending.qsize()))
				ret_obj = pickle.dumps(temp)
				logging.debug("sending list {}  to {}".format(str(temp), data))
				#send to S1 or S2 depending
				c.send(ret_obj)
				for_sending.task_done()
			else:
				logging.debug("QUEUE IS EMPTY\n\n\n")
				c.send(pickle.dumps([]))
		else:
			print("\tNeed data! Closing connection with {}\n".format(addr))

	def sync_mode(self, for_sending):
		# print("Starting thread {}".format(threading.current_thread().name))
		toserver1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		received_queue = list()

		header="S1"
		toserver1.connect((S1_IP,PORT))
		logging.debug("\tConnected to REUEL\n")
		#send identifying that i am a server
		toserver1.send(header.encode())
		# print("Request sent to REUEL")



		#receive the requestq
		rec1 = toserver1.recv(1024)
		data1 = pickle.loads(rec1)
		if len(data1) > 0:
			logging.debug("Received from Reuel {}".format(str(data1)))
			received_queue.extend(data1)

		toserver1.close()
		print("Closed connection with REUEL")


		toserver2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		header="S2"
		toserver2.connect((S2_IP,PORT))
		logging.debug("\tConnected to AASTHA")
		#send identifying that i am a server
		toserver2.send(header.encode())
		# print("Request sent to AASTHA")

		#receive the requestq
		rec2 = toserver2.recv(1024)
		data2 = pickle.loads(rec2)
		if len(data2) > 0:
			logging.debug("Received from Aastha {}".format(str(data2)))
			received_queue.extend(data2)

		toserver2.close()

		if len(received_queue) > 0:
			logging.debug("\tReceived requests from other servers.\nUpdating local list with all requests")
			logging.debug("\n\n\tPRINTING RECEIVE QUEUE: ", received_queue,"\n\n")
		else:
			logging.debug("\tNo request queues from other servers. Business as usual.")
		time.sleep(2)
		self.update_nums(received_queue, for_sending)
		return

	def run_forever(self, for_sending):
		print("Sleeping")
		time.sleep(2)
		schedule.every(10).seconds.do(self.sync_mode, for_sending)
		print("Calling schedule")
		while True:
			schedule.run_pending()

if __name__ == "__main__":
	ThreadedServer().listen()