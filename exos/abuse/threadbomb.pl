author=chilowi
text==
Implementation of a nice thread bomb!
==
tester==
from threading import Thread

def run():
	for i in range(0, 2):
		Thread(target=run).start()

run()
==
