##
 # client.py
 # Nov 9, 2019
 #
 # deepraj.pandey_ug20@ashoka.edu.in
 #
 # The client program for the Course Grade Directory server. Communication alternates
 # between client and server.
 #
 # Note: Type "HELP" at first prompt to read the server spec-sheet.
 ##

import socket as skt

try:
	clientsocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
	print("Client socket created successfully.\n")
except skt.error as err:
	print("Socket creation failed with error %s" % (err))

host_ip = 'localhost'
port = 8001

# connect to the server
clientsocket.connect((host_ip, port))

while True:
	from_server = clientsocket.recv(1024).decode()
	print("CGD:", from_server, flush=True)
	if from_server == "Bye":
		break
	data = input("Us: ")
	clientsocket.send(data.encode())
print("\nServer closed connection. Closing socket.")
clientsocket.close()
