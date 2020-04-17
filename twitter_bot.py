#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Guillaume Rozier - 2020 - MIT License
# This script will automatically tweet new data and graphes on the account @covidtracker_fr

# importing the module 
try:
    import tweepy
except ImportError as e:
    get_ipython().system('sudo pip3 install tweepy')

import secrets as s

"""
Secrets :
    consumer_key ="xxxxxxxxxxxxxxxx"
    consumer_secret ="xxxxxxxxxxxxxxxx"
    access_token ="xxxxxxxxxxxxxxxx"
    access_token_secret ="xxxxxxxxxxxxxxxx"
"""

# authentication 
auth = tweepy.OAuthHandler(s.consumer_key, s.consumer_secret) 
auth.set_access_token(s.access_token, s.access_token_secret) 
   
api = tweepy.API(auth) 
tweet ="🔴 #Coronavirus #France\n{} pers. décédées en milieu hosp.\n{} pers. en réanimation\n{} pers. en hosp. (hors réa.)\n{} pers. retournées à domicile\n + d'infos guillaumerozier.fr/covidtracker-france".format(dc, rea, hosp, rad) # toDo 
image_path ="charts/images/france/var_journ.png"
  
# to attach the media file 
status = api.update_with_media(image_path, tweet)  
api.update_status(status = tweet) 

