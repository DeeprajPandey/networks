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

clientsocket.send("Hello from the other side.".encode())
while True:
	from_server = clientsocket.recv(1024).decode()
	print(from_server, flush=True)
	if from_server == "Bye":
		break
	data = input()
	clientsocket.send(data.encode())
print("Server closed connection. Closing socket.")
clientsocket.close()
