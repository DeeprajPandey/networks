import pandas as pd
import numpy as np

# store what the last test that the student took
test_label = np.nan

def last_valid(y):
	global test_label
	if y.last_valid_index() is None:
		test_label = np.nan
		return np.nan
	else:
		test_label = y.last_valid_index()
		return y[y.last_valid_index()]

df = pd.read_excel('scores.xlsx', 'monsoon19', header=0)
# username from client
name = 'rathi.kashi_ug20'

# returns an array of true(for matches)/false(if not)
indices = df['Students'].str.match(name)
# dataframe with rows where the student column matches the username
search_results  = df[indices]

# if the name wasn't found
if search_results.empty:
	print("Student is not in the course. Try again!")
	# continue listening for usernames until sees 'exit'

# df.shape gives a (row,col) tuple
elif search_results.shape[0] > 1:
	print("There are duplicate records for this username. Contact your faculty.")
	# continue listening for usernames until sees 'exit'
# one match found
else:
	# array with row index and value
	latest_score = search_results.apply(last_valid, axis=1)
	print "Your score in", test_label, "is " + str(latest_score[1]) + "."
