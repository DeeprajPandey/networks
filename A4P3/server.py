import socket as skt

### Utilities ###
### Function to generate an n-word diceware password ###
def get_passphrase(n):
	# wordlist is the EFF diceware long word list
	wordlist = [ln.split()[1] for ln in open('./wordlist')]
	# `n` words joined by -
	pp = '-'.join(random.SystemRandom().choice(wordlist) for i in range(n))
	return pp



welcome = "Welcome to Course Grade Directory!"

spec_string = "\n#### Server Specs ####\nYou can only access this server if you are \
enrolled in this course. If you are accessing it for the first time, \
you will receive a password right after sending your username.\n\
Send that after PASS and you will receive your latest test score.\n\n\
USER: tell server that you will be sending username\n\
PASS: tell server that you will be sending password\n\
HELP: display this help text\n\
END: ask server to end connection\n############\n"

warn = "No data received. Try again."

invalid_usr_p = "\nIncorrect username or password. Try again.\n\n"

inworks = "Course Grade Directory is in works."

# Checks if the entered username is in the course
# returns true if username is in score sheet
def is_valid_user(username):
	# TODO: check if username is in the sheet

	return False

# Sends server specs. Is called when undeterministic behaviour
# is noticed
# c: client socket
def anomaly(c):
	c.send(spec_string.encode())

# Sends help text when incorrect usr or passw is received
# Is called when username or password is invalid
def incorrect_creds(client):
	prompt = invalid_usr_p + spec_string
	client.send(prompt.encode())

# Sends prompt when ready to accept username
# c: client socket
def ask_usr(c):
	prompt = "Send Username.\n"
	c.send(prompt.encode())

# Sends prompt when ready to accept password
# c: client socket
def ask_passw(c):
	prompt = "Send Password.\n"
	c.send(prompt.encode())

# generates a passphrase and assigns it to client with username
def assign_passw(client, username):
	new_pass = get_passphrase(5)
	prompt = "Hello, " + str(username) + "!\n\
You are accessing the service for the first time. \
Your generated password is\n" + str(new_pass) + "\n\
Enter this password when prompted."
	# TODO: add it to passwords dict for corresponding username

	c.send(prompt.encode())

# sends scores to client
# Note: this should be called after proper authentication
def send_scores(client, username):
	# TODO: DEFINE LATEST SCORE MECHANISM
	# TODO: get scores from the sheet and add to prompt

	test = "in works"
	score = "in works"
	# test, score = search_test_scores(username)
	prompt = "Hello, " + str(username) + "!\n\
Welcome  back to Course Grade Directory.\nYour score in "\
+ str(test) + " is " + str(score) + "\nYou are\
now logged out."
	client.send(prompt.encode())

# Authenticates user
# c: client socket
def auth(c):
	end = False
	usr = "None"
	passw = "None"
	c.send(welcome.encode())
	key = c.recv(1024).decode()
	while not end:
		if key == "USER":
			ask_usr(c)
			usr = c.recv(1024).decode()
			if not usr:
				c.send(warn.encode())
				key = "HELP"
			else:
				key = c.recv(1024).decode()

		elif key == "PASS":
			# only for clients logging in for the first time
			# check if we have valid username
			if is_valid_user(usr):
				# check if first time
				if passwords[usr] == "not set":
					# assign a password
					assign_passw(c, usr)
			ask_passw(c)
			passw = c.recv(1024).decode()
			if not passw:
				c.send(warn.encode())
				key = "HELP"
			else:
				if is_valid_user(usr) and passw == passwords[usr]:
					# send latest test scores
					send_scores(c, usr)
					usr = "None"
					passw = "None"
				else:
					incorrect_creds(c)
					key = c.recv(1024).decode()

		elif key == "END":
			c.send("Bye".encode())
			return

		# control comes here when key is either HELP or anything else
		else:
			anomaly(c)
			key = c.recv(1024).decode()

def Main():
	# server socket
	IP = 'localhost'
	PORT = 8001

	server = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
	server.bind((IP, PORT))
	server.listen(128)
	print("Server is listening...\n", flush=True)

	while True:
		(client, address) = server.accept()
		print("Connected to client " + str(address[0]) + \
			":" + str(address[1]), flush=True)

		auth(client)
		client.close()
if __name__ == '__main__':
	Main()
