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
for_sending = queue.Queue()

IP = "10.1.16.202"
S1_IP = "10.1.21.15"
S2_IP = "10.1.56.110"
PORT = 8001

SENT_CTR = 0

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


		# ### Check if the other two servers are up ###
		# ### Issue: because there is no client handler before this,
		# ### other servers can't respond with UP ###
		# s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s1.settimeout(3)
		# s2.settimeout(3)
		# s1_status = ""
		# s2_status = ""
		# conn_tries = 0
		# while (s1_status != "UP" and s2_status != "UP"):
		# 	# if conn_tries == 2:
		# 	# 	logging.debug("The other two aren't waking up, exiting...")
		# 	# 	exit(0)
		# 	header = "SUP"

		# 	try:
		# 		s1.connect((S1_IP,PORT))
		# 	except socket.timeout:
		# 		logging.debug("S1 not up")
		# 	except OSError as e:
		# 		logging.debug("OS said S1 not up: {}".format(e))
		# 		time.sleep(5)
		# 	else:
		# 		logging.debug("S1 up!")
		# 		# s1.send(header.encode())
		# 		s1_status = "UP"

		# 	try:
		# 		s2.connect((S2_IP,PORT))
		# 	except socket.timeout:
		# 		logging.debug("S2 not up")
		# 	except OSError as e:
		# 		logging.debug("OS said S2 not up: {}".format(e))
		# 		time.sleep(5)
		# 	else:
		# 		logging.debug("S2 up!")
		# 		# s2.send(header.encode())
		# 		s2_status = "UP"

		# 	conn_tries = conn_tries + 1

		# This should start only when all 3 servers are up
		sched = threading.Thread(target = self.run_forever, args = ())
		sched.setName('scheduler')
		sched.start()
		# to check if there are no items in queue
		# queue.get() will run forever if tried on empty list
		
		while True:
			c, addr = self.s.accept()
			c.settimeout(60)
			# start a new thread with the function that handles client
			ch = threading.Thread(target = self.handleClient,args = (c, addr))
			ch.setName('clientHandler')
			ch.start()

	def handleClient(self, c, addr):
		global SENT_CTR
		global request_queue
		global nums
		global for_sending

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
			swap_req = (header, (ij, rn))
			request_queue.append(swap_req)
			logging.debug("Client swap request added to queue.\n")

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

		elif (data == 'SUP'):
			c.send("UP".encode())

		else:
			print("\tNeed data! Closing connection with {}\n".format(addr))

	def sync_mode(self):
		received_queue = list()

		toserver1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		toserver2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		toserver1.settimeout(3)
		toserver2.settimeout(3)

		header = "S1"

		try:
			toserver1.connect((S1_IP,PORT))

		except socket.timeout as e:
			logging.debug("{} connecting to Reuel, check if he's sleeping.\n".format(e))

		else:
			logging.debug("\tConnected to REUEL\n")
			
			# send identifying that i am a server
			toserver1.send(header.encode())

			# receive the requestq
			s1_q_obj = toserver1.recv(1024)
			s1_queue = pickle.loads(s1_q_obj)

			if len(s1_queue) > 0:
				logging.debug("Received {} from Reuel".format(str(s1_queue)))
				received_queue.extend(s1_queue)

			toserver1.close()
			logging.debug("\tClosed connection with REUEL\n")


		header = "S2"

		try:
			toserver2.connect((S2_IP,PORT))

		except socket.timeout as e:
			logging.debug("{} connecting to Aastha, check if she's sleeping.\n".format(e))

		else:
			logging.debug("\tConnected to AASTHA\n")
			
			#send identifying that i am a server
			toserver2.send(header.encode())

			#receive the requestq
			s2_q_obj = toserver2.recv(1024)
			s2_queue = pickle.loads(s2_q_obj)
			if len(s2_queue) > 0:
				logging.debug("Received {} from Aastha".format(str(s2_queue)))
				received_queue.extend(s2_queue)

			toserver2.close()
			logging.debug("\tClosed connection with AASTHA\n")

		if len(received_queue) > 0:
			# logging.debug("\tReceived requests from other servers\n")
			logging.debug("\n\n\tPRINTING RECEIVED QUEUE: {}\n\n".format(str(received_queue)))
		else:
			logging.debug("\tNo request queues from other servers. Business as usual.")

		logging.debug("Sleeping before calling update_nums")
		time.sleep(5)
		self.update_nums(received_queue)
		return

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

	def update_nums(self, received):
		global SENT_CTR
		global nums
		global request_queue
		global for_sending

		local_rq = request_queue[:]
		logging.debug("Inside update_nums. Current local_rq is {}".format(str(local_rq)))


		if len(local_rq) == 0 and len(received) == 0:
			return

		# time.sleep(5)
		for_sending.put(local_rq)
		for_sending.put(local_rq)
		
		local_rq.extend(received)
		
		local_rq = sorted(local_rq, key=itemgetter(1))
		for tup in local_rq:
			returnval = self.swap(tup[0])
		request_queue=[]
	
	def run_forever(self):
		logging.debug("Waking up...")
		schedule.every(11).seconds.do(self.sync_mode)
		logging.debug("Calling schedule")
		while True:
			schedule.run_pending()

if __name__ == "__main__":
	ThreadedServer().listen()