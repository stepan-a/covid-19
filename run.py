import time
from datetime import datetime
import subprocess

k=0

while True is True:
    subprocess.run(["git", "pull"])

    if k%4 == 0: # do upload to plotly
        subprocess.run(["python3", "covid-19.py", "True", "False"])

    else: #do not upload to plotly
        subprocess.run(["python3", "covid-19.py", "False", "False"])

    subprocess.run(["git", "add", "images/*"])
    subprocess.run(["git", "commit", "-m", "Charts updated (image folder)"])
    subprocess.run(["git", "push"])

    print(">>>>> " + str(datetime.now()))
    print("---- Iteration " + k)
    k += 1
    time.sleep(3600)
