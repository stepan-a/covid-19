#!/usr/bin/env python
# coding: utf-8

# In[4]:


import datetime
import time
import subprocess

def update_repo():
    subprocess.run(["git", "fetch", "--all"])
    subprocess.run(["git", "reset", "--hard", "origin/master"])
    subprocess.run(["sudo", "jupyter", "nbconvert", "--to", "script", "*.ipynb"])
    
def push(type_data):
    subprocess.run(["git", "add", "images/", "date/"])
    subprocess.run(["git", "comit", "-m", "auto data update: {}".format(type_data)])
    
while True:
    x = datetime.datetime.now()
    h = x.strftime("%H")
    m = x.strftime("%M")
    
    if h == '05' & m =='00':
        update_repo()
        subprocess.run(["sudo", "python3", "covid19_world_charts.py"])
        subprocess.run(["sudo", "python3", "covid19_france_charts.py"])
        push("World")
        
    if h == '19' & m == '05':
        update_repo()
        subprocess.run(["sudo", "python3", "covid19_france_charts.py"])
        push("France")
        
    if h == '19' & m == '40':
        update_repo()
        subprocess.run(["sudo", "python3", "covid19_france_charts.py"])  
        push("France")
        
    time.sleep(30)

