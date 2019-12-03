import socket
import pickle

# create an INET, STREAMing socket


port = 8001
ip_database = {
        "1":"10.1.16.202",
        "2":"10.1.21.15",
        "3":"10.1.56.110"
} 
# clientsocket.connect(("10.1.17.123", 8728))


while True:
	# print(clientsocket.recv(1024).decode())
	print(ip_database)
	print("Enter which server you want to connect to (1, 2, 3, or 4 for exit)\n")
	choice = input("Enter choice: ")
	if(choice=="4"):
		print("\nExiting\n")
		break

	ip = ip_database.get(choice, "none")

	clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	clientsocket.settimeout(3)

	try:
		clientsocket.connect((ip, port))
	except ConnectionRefusedError:
		print("Server down, try again later.\n\n")
	except socket.timeout:
		print("Server down, try again later.\n\n")
	except Exception as e:
		print(e)
	else:
		tosend = ("C", "0 0")
		clientsocket.send(pickle.dumps(tosend))

		print("Current list:\n", clientsocket.recv(1024).decode())
		i = input("Enter i: ")
		j = input("Enter j: ")
		clientsocket.send((str(i)+" "+str(j)).encode())
		clientsocket.close()
		print("Closed connection with server!\n\n")