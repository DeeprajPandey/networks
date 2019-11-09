import socket as skt

def Main():
	# server socket
	IP = 'localhost'
	PORT = 8001

	server = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
	server.bind((IP, PORT))
	server.listen(128)
	print("Server is listening...\n")

	while True:
		(client, address) = server.accept()
		print("Connected to client " + str(address[0]) + \
			":" + str(address[1]))
		
		data = client.recv(1024).decode()
		send_data = "Course Grade Directory is in works."
		client.send(send_data.encode())
		client.close()
if __name__ == '__main__':
	Main()
