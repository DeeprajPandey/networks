import pandas as pd
import numpy as np
# to check for NaN
import math
# for password generation
import random,sys
# passwords stored in json file
import json


### Globals ###
# username & password from client
name = 'rathi.kashi_ug20'
entered_pass = 'frittletop'

# store what the last test that the student took
test_label = np.nan
passwords = {}

# all passwords in a dict
with open("passwords.json", 'r') as istream:
	passwords = json.load(istream)

# read the excel file and import data as a dataframe
data = pd.read_excel('scores.xlsx', 'monsoon19', header=0)


### Function to generate an n-word diceware password ###
def get_passphrase(n):
	# wordlist is the EFF diceware long word list
	wordlist = [ln.split()[1] for ln in open('./wordlist')]
	# `n` words joined by -
	pp = '-'.join(random.SystemRandom().choice(wordlist) for i in range(n))
	return pp


### Returns the last valid test score in dfObject ###
# and stores the test label in the global test_label variable
def last_valid(y):
	global test_label
	if y.last_valid_index() is None:
		test_label = np.nan
		return np.nan
	else:
		test_label = y.last_valid_index()
		return y[y.last_valid_index()]


# check if the user entered anything
if math.isnan(name) or math.isnan(entered_pass):
	print "Please enter a valid username and/or password.\n\
	Your username is your Ashoka ID and your password must have\
	been assigned to you on your first login on this system.\
	Please contact your course faculty if you have lost your password."

# str.match() returns an array of true(for matches)/false(if not)
indices = data['Students'].str.match(name)
# dataframe with rows where the student column matches the username
search_results  = data[indices]

# if the name wasn't found in monsoon19 or password list
if search_results.empty or\
name not in passwords.keys:
	print("Invalid username or student not in the course. Try again!")
	# continue listening for usernames until sees 'exit'

# df.shape gives a (row,col) tuple
# if the password is correct and more than one row in results
elif entered_pass == passwords[name] and\
search_results.shape[0] > 1:
	print("There are duplicate records for this username. Contact your faculty.")
	# continue listening for usernames until sees 'exit'

# one match for `username` found
else:
	if passwords[name] == "not set":
		# call pass_generator() and store it in the sheet
		new_pass = pass_generator(5)
		passwords[name] = new_pass
		# print it for the user
		print "Your password is", new_pass
		print "Store it in a secure place. If you forget your password, contact course faculty."
		# we don't need this sticking around anymore
		new_pass = np.nan
	elif entered_pass == passwords[name]:
		# array with row index and value
		latest_score = search_results.apply(last_valid, axis=1)
		print "Your score in", test_label, "is " + str(latest_score[1]) + "."
		print "You are now logged out."
		test_label = np.nan
		entered_pass = np.nan
	else:
		print "Incorrect password. Try again."
		# continue listening for usernames until sees 'exit'

# dump all updates passwords to the json file
with open("passwords.json", 'w') as ostream:
	json.dump(passwords, ostream)