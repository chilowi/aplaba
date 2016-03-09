author=chilowi
text==
Creation of an gigantic file!
==
answer==
with open("myfile", "w"):
	while True:
		f.write("a" * 100000)
==
