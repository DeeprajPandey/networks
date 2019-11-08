import pandas as pd

df = pd.read_excel('scores.xlsx', 'monsoon19', header=0)
# username from client
name = 'rathi.kashi_ug20'

# returns an array of true(for matches)/false(if not)
indices = df['students'].str.match(name)
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
	print search_results
