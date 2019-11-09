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
print("Server closed connection. Closing socket.")
clientsocket.close()
