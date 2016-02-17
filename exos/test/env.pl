title=Environnement
author=chilowi
grader==
import os, json
import student

def get_useful_data():
	data = {}
	data.update(globals={ str(k): str(v) for (k, v) in globals().items() })
	data.update(environ=dict(os.environ))
	return data
	
print(json.dumps(get_useful_data()))

==
