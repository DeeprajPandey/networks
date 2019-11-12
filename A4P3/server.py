##
 # server.py
 # Nov 9, 2019
 #
 # deepraj.pandey_ug20@ashoka.edu.in
 #
 # TCP server (Course Grade Directory) which allows students in a course
 # to fetch their latest test scores. Reads the data from an excel file and sends after authentication.
 # Has a basic (not-secure) authentication procedure for everyone in the course.
 #
 # Students use their Ashoka ID to sign up and are given a diceware passphrase on
 # first access.
 #
 # - reads the test scores from scores.xlsx (in the same directory)
 # - stores all passwords in passwords.json (in the same directory)
 # - P.S: make sure the usernames in 'Students' column in the sheet is exactly same
 # as the keys of the json dictionary. AND that all the passwords are initialised to
 # "not set". The server runs a diceware generator from the EFF long wordlist to generate
 # a passphrase during first login.
 ##

import socket as skt
import pandas as pd
import numpy as np
# for password generation
import secrets
# passwords stored in json file
import json

### Data ###
# store what the last test that the student took
test_label = np.nan
search_results = np.nan
passwords = {}
pass_assgn_flag = 0
# all passwords in a dict
with open("passwords.json", 'r') as istream:
	passwords = json.load(istream)

# read the excel file and import data as a dataframe
all_data = pd.read_excel('scores.xlsx', 'monsoon19', header=0)


### Utilities ###
### Function to generate an n-word diceware password ###
def get_passphrase(n):
	# wordlist is the EFF diceware long word list
	wordlist = [ln.split()[1] for ln in open('./wordlist')]
	# `n` words joined by -
	pp = '-'.join(secrets.choice(wordlist) for i in range(n))
	return pp

### Returns the last valid test score in dfObject ###
# and stores the test label in the global test_label variable
def last_valid_score(y):
	global test_label
	if y.last_valid_index() is None:
		test_label = np.nan
		return np.nan
	else:
		test_label = y.last_valid_index()
		return y[y.last_valid_index()]


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

### Server Utils ###

# Checks if the entered username is in the course
# returns true if username is in score sheet
def is_valid_user(username):
	global search_results
	# TODO: check if username is in the sheet
	# str.match() returns an array of true(for matches)/false(if not)
	indices = all_data['Students'].str.match(username)
	# dataframe with rows where the student column matches the username
	search_results  = all_data[indices]

	# will return false if there are multiple
	# or zero instances of the name in the monsoon19 sheet
	# or if the name isn't in password list
	if search_results.shape[0] != 1 or\
username not in passwords.keys():
		return False
	else:
		return True

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
	prompt = "Send Username."
	c.send(prompt.encode())

# Sends prompt when ready to accept password
# c: client socket
def ask_passw(c):
	prompt = "Send Password."
	c.send(prompt.encode())

# generates a passphrase and assigns it to client with username
def assign_passw(client, username):
	new_pass = get_passphrase(5)
	prompt = "Hello, " + str(username) + "!\n\
You are accessing the service for the first time. \
Your generated password is\n" + str(new_pass) + "\n\
Enter this password when prompted...\n"
	# TODO: add it to passwords dict for corresponding username
	passwords[username] = new_pass
	pass_assgn_flag = 1
	# we don't need this sticking around anymore
	new_pass = np.nan
	client.send(prompt.encode())

# searches for the latest test taken by `username` and returns that
# along with the score in that test
def search_test_scores(username):
	global test_label
	# array with the row index and the test score
	latest_score = search_results.apply(last_valid_score, axis=1)
	latest_test = test_label
	# clear the global variable for further use
	test_label = "None"
	return latest_test, int(latest_score[latest_score.index[0]])

# sends scores to client
# Note: this should be called after proper authentication
def send_scores(client, username):
	# TODO: DEFINE LATEST SCORE MECHANISM
	# TODO: get scores from the sheet and add to prompt
	test, score = search_test_scores(username)
	prompt = "Hello, " + str(username) + "!\n\
Welcome  back to Course Grade Directory.\nYour score in "\
+ str(test) + " is " + str(score) + "\nYou are \
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
				c.send("Next...".encode())
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
					key = c.recv(1024).decode()
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
		# dump all updated passwords to the json file
		with open("passwords.json", 'w') as ostream:
			json.dump(passwords, ostream)
if __name__ == '__main__':
	Main()
