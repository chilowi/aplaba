author=chilowi
text==
Creation of lots of empty files and directories
==
tester==

import os

def run():
	i = 0
	while True:
		os.mkdir("dir{}".format(i))
		with open("file{}".format(i), "wb"):
			pass
		i += 1
==
