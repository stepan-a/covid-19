import time
from datetime import datetime
import subprocess

k=0

while True is True:
        subprocess.run(["git", "pull"])
	subprocess.run(["python3", "covid-19.py"])
	print(">>>>> " + datetime.now())	
	print("---- Iteration " + k)
	k += 1
	time.sleep(14400)
