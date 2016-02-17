author=chilowi
text==
Emission of lots of requests towards the localhost website
==
tester==

URL = "http://localhost/"

from urllib.request import urlopen
from threading import Thread

def run():
	with urlopen(URL) as f:
		value = f.read()
		
while True:
	Thread(target=run).start()
==
