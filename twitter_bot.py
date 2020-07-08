#!/usr/bin/env python
# coding: utf-8

# In[116]:


# Guillaume Rozier - 2020 - MIT License
# This script will automatically tweet new data and graphes on the account @covidtracker_fr

# importing the module 

import france_data_management as data
import math
from datetime import datetime
import locale
import tweepy
import pandas as pd
import secrets as s

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

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
    
def tweet_france():
    _, _, dates, df_new, _, _, _, df_incid = data.import_data()
    df_new_france = df_new.groupby(["jour"]).sum().reset_index()
    df_incid_france = df_incid.groupby(["jour"]).sum().reset_index()

    hosp = df_new_france.iloc[len(df_new_france)-1]['incid_hosp']
    deaths = df_new_france.iloc[len(df_new_france)-1]['incid_dc']
    cases = df_incid_france.iloc[len(df_incid_france)-1]['p']
    date = datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')
    date_incid = datetime.strptime(sorted(list(dict.fromkeys(list(df_incid_france['jour'].values))))[-1], '%Y-%m-%d').strftime('%d %B')
    tweet ="#Covid19 en #France - Données du jour :\n• {} nouveaux cas positifs ({})\n• {} personnes décédées en milieu hosp. ({})\n• {} admissions à l'hôpital ({})\n➡️ Plus d'infos : covidtracker.fr/covidtracker-france".format(cases, date_incid, deaths, date, hosp, date) # toDo 
    image_path ="images/charts/france/var_journ_lines.jpeg"

    # to attach the media file 
    status = api.update_with_media(image_path, tweet)
    #print(tweet)
    
def tweet_world():
    # Import data
    df_confirmed_csse = pd.read_csv('data/total_cases_csse.csv')
    df_deaths_csse = pd.read_csv('data/total_deaths_csse.csv')
    
    df_confirmed = pd.read_csv('data/data_confirmed.csv')
    df_deaths = pd.read_csv('data/data_deaths.csv')
    
    # Compute diff to get daily data
    df_confirmed_diff = df_confirmed.copy()
    df_confirmed_diff.loc[:, df_confirmed.columns != 'date'] = df_confirmed.loc[:, df_confirmed.columns != 'date'] .diff()

    df_deaths_diff = df_deaths.copy()
    df_deaths_diff.loc[:, df_deaths.columns != 'date'] = df_deaths.loc[:, df_deaths.columns != 'date'] .diff()
    
    # Get only last day
    date = max(df_confirmed["date"])
    date_str = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')

    df_confirmed_lastd = df_confirmed[df_confirmed["date"] == date]
    df_confirmed_diff_lastd = df_confirmed_diff[df_confirmed_diff["date"] == date]

    df_deaths_lastd = df_deaths[df_deaths["date"] == date]
    df_deaths_diff_lastd = df_deaths_diff[df_deaths_diff["date"] == date]
    
    # Get results
    sum_cases = math.trunc(df_confirmed_lastd.sum(axis=1).values[0])
    new_cases = math.trunc(df_confirmed_diff_lastd.sum(axis=1).values[0])

    sum_deaths = math.trunc(df_deaths_lastd.sum(axis=1).values[0])
    new_deaths = math.trunc(df_deaths_diff_lastd.sum(axis=1).values[0])
    
    # Write and publish tweet
    tweet ="Données du #Covid19 dans le monde au {} :\n+ {} cas en 24h, soit {} au total\n+ {} décès en 24h, soit {} au total\nPlus d'infos : covidtracker.fr/covidtracker-world\n".format(date_str, f"{new_cases:,d}".replace(',', ' '), f"{sum_cases:,d}".replace(',', ' '), f"{new_deaths:,d}".replace(',', ' '), f"{sum_deaths:,d}".replace(',', ' ')) # toDo 
    image_path ="images/banniere.jpeg"

    # to attach the media file 
    status = api.update_with_media(image_path, tweet)
    #print(tweet)


# In[117]:


#tweet_world()

