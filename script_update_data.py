#!/usr/bin/env python
# coding: utf-8

# In[4]:


import datetime
import time
import subprocess
import requests

url_metadata = "https://www.data.gouv.fr/fr/organizations/sante-publique-france/datasets-resources.csv"

def update_repo():
    subprocess.run(["sudo", "git", "fetch", "--all"])
    subprocess.run(["sudo", "git", "reset", "--hard", "origin/master"])
    subprocess.run(["sudo", "jupyter", "nbconvert", "--to", "script", "*.ipynb"])
    
def push(type_data):
    subprocess.run(["sudo", "git", "add", "images/", "data/"])
    subprocess.run(["sudo", "git", "commit", "-m", "[auto] data update: {}".format(type_data)])
    subprocess.run(["git", "push"])
    print("pushed")
    
while True:
    x = datetime.datetime.now()
    h = x.strftime("%H")
    m = x.strftime("%M")
    
    if (h == '05') & (m =='00'):
        update_repo()
        subprocess.run(["sudo", "python3", "covid19_world_charts.py"])
        push("World")
        print("update World" + str(h) + " " + str(m))
        
        subprocess.run(["sudo", "python3", "covid19_france_charts.py"])
        push("France")
        print("update France" + str(h) + " " + str(m))
        time.sleep(30)
    
    if ((h == '18') & (m =='59')):
        data_today = False
        update_repo()
            
        while not data_today:
            metadata = requests.get(url_metadata)

            if "donnees-hospitalieres-covid19-2020-{}-{}".format(x.strftime("%m"), x.strftime("%d")) in str(metadata.content):
                data_today = True
                
                subprocess.run(["sudo", "python3", "covid19_france_charts.py"])
                push("France")
                print("update France" + str(h) + " " + str(m))

                subprocess.run(["sudo", "python3", "covid19_france_maps.py"])
                push("France GIF")
                print("update France GIF" + str(h) + " " + str(m))

            time.sleep(20)
            
    time.sleep(30)

