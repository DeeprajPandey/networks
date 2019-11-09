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
print(clientsocket.recv(1024).decode())
clientsocket.close()
