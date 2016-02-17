import os
for (dirpath, dirs, files) in os.walk("."):
	for filepath in files:
		with open(os.path.join(dirpath, filepath), "r", errors="ignore") as f:
			print(os.path.join(dirpath, filepath) + "\n" + f.read() + "\n\n")
