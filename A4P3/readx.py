import pandas as pd
import numpy as np
# to check for NaN
import math

# store what the last test that the student took
test_label = np.nan

# returns the last valid test score
# and stores the test label in the global test_label variable
def last_valid(y):
	global test_label
	if y.last_valid_index() is None:
		test_label = np.nan
		return np.nan
	else:
		test_label = y.last_valid_index()
		return y[y.last_valid_index()]

# username & password from client
name = 'rathi.kashi_ug20'
entered_pass = 'frittletop'

# check if the user entered anything
if math.isnan(name) or math.isnan(entered_pass):
	print "Please enter a valid username and/or password.\n\
	Your username is your Ashoka ID and your password must have\
	been assigned to you on your first login on this system.\
	Please contact your course faculty if you have lost your password."

data = pd.read_excel('scores.xlsx', 'monsoon19', header=0)
# usernames are indices in this data frame
passwords = pd.read_excel('scores.xlsx', 'passwords', header=0, index_col=0)

# returns an array of true(for matches)/false(if not)
indices = data['Students'].str.match(name)
# dataframe with rows where the student column matches the username
search_results  = data[indices]

# if the name wasn't found in monsoon19
if search_results.empty:
	print("Invalid username or student not in the course. Try again!")
	# continue listening for usernames until sees 'exit'

# df.shape gives a (row,col) tuple
# if the password is correct and more than one row in results
elif search_results.shape[0] > 1 and\
	 entered_pass == passwords.loc[name]['stored']:
	print("There are duplicate records for this username. Contact your faculty.")
	# continue listening for usernames until sees 'exit'

# one match found
else:
	if passwords.loc[name]['stored'] == 'not set':
		# call pass_generator() and store it in the sheet
		# print it to the user
	elif entered_pass == passwords.loc[name]['stored']:
		# array with row index and value
		latest_score = search_results.apply(last_valid, axis=1)
		print "Your score in", test_label, "is " + str(latest_score[1]) + "."
		print "You are now logged out."
		test_label = np.nan
		entered_pass = np.nan
	else:
		print "Incorrect password. Try again."
		# continue listening for usernames until sees 'exit'
