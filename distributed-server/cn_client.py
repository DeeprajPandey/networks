import socket
import string 
import random 

# create an INET, STREAMing socket
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


port = 8000
ip_database = {
        "1":"10.1.16.202",
        "2":"10.1.21.15",
        "3":"54321"
} 
# clientsocket.connect(("10.1.17.123", 8728))


while True:
	# print(clientsocket.recv(1024).decode())
	print("Enter which server you want to connect to (1, 2, 3, or 4 for exit)\n")
	choice = input("Enter choice:")
	if(choice=="4"):
		print("\nExiting\n")
		# clientsocket.send(choice.encode())
		break
	ip = ip_database.get(choice, "none")
	clientsocket.connect((ip, port))
	clientsocket.send("CLIENT".encode())
	print("Current list:\n", clientsocket.recv(1024).decode())
	# print("Enter tuple\n")
	# i, j = raw_input().split()
	# i = str(i)
	# j = str(j)
	ij = input("Enter tuple\n")
	print("ij:",ij)
	print(type(ij))
	clientsocket.send(ij.encode())
	# clientsocket.send(j.encode())
	# clientsocket.send("closing connection".encode())
	clientsocket.close()
	# clientsocket.send(choice.encode())
	# choice = int(choice)
	# if(choice==1):
	# 	email = input("Enter email: ")
	# 	clientsocket.send(email.encode())
	# 	ack = clientsocket.recv(1024).decode()
	# 	if(ack=="yes"):
	# 		print("\nEMAIL ADDED TO DATABASE IF NOT PRESENT ALREADY\n")
	# 		continue
	# 	else:
	# 		print("\nNOT IN CLASS - CANNOT CREATE ACCOUNT\n")
	# 		continue
	# if(choice==2):
	# 	email = input("Enter email: ")
	# 	clientsocket.send(email.encode())
	# 	ack = clientsocket.recv(1024).decode()
	# 	if(ack=="yes"):
	# 		password = input("Enter password: ")
	# 		clientsocket.send(password.encode())
	# 		print(clientsocket.recv(1024).decode())
	# 		continue
	# 	else:
	# 		print("\nEMAIL NOT IN DATABASE\n")
	# 		continue

# clientsocket.close()
# close the connection with the server

