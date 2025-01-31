#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
from datetime import timedelta

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
    #data.download_data()
    _, _, dates, df_new, _, _, _, df_incid, _ = data.import_data()
    df_new_france = df_new.groupby(["jour"]).sum().reset_index()
    df_incid_france = df_incid.groupby(["jour"]).sum().reset_index()
    
    lastday_df_new = datetime.strptime(df_new_france['jour'].max(), '%Y-%m-%d')
    
    hosp = df_new_france[df_new_france['jour']==lastday_df_new.strftime('%Y-%m-%d')]['incid_hosp'].values[-1]
    date_j7 = (lastday_df_new - timedelta(days=7)).strftime("%Y-%m-%d")
    hosp_j7 = df_new_france[df_new_france['jour'] == date_j7]['incid_hosp'].values[-1]
    
    
    deaths = df_new_france[df_new_france['jour']==lastday_df_new.strftime('%Y-%m-%d')]['incid_dc'].values[-1]
    deaths_j7 = df_new_france[df_new_france['jour'] == date_j7]['incid_dc'].values[-1]
    
    lastday_df_incid = datetime.strptime(df_incid_france['jour'].max(), '%Y-%m-%d')
    tests = df_incid_france[df_incid_france['jour']==lastday_df_incid.strftime('%Y-%m-%d')]['P'].values[-1]
    date_j7_incid = (lastday_df_incid - timedelta(days=7)).strftime("%Y-%m-%d")
    tests_j7 = df_incid_france[df_incid_france['jour'] == date_j7_incid]['P'].values[-1]
    
    date = datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')
    
    hosp_tendance, hosp_sign = "en hausse", "+"
    if hosp_j7>hosp:
        hosp_tendance, hosp_sign = "en baisse", ""
    if hosp_j7==hosp:
        hosp_tendance, hosp_sign = "stable", "+"
        
    deaths_tendance, deaths_sign = "en hausse", "+"
    if deaths_j7>deaths:
        deaths_tendance, deaths_sign = "en baisse", ""
    if deaths_j7==deaths:
        deaths_tendance, deaths_sign = "stable", "+"
        
    tests_tendance, tests_sign = "en hausse", "+"
    if tests_j7>tests:
        tests_tendance, tests_sign = "en baisse", ""
    if tests_j7==tests:
        tests_tendance, tests_sign = "stable", "+"
        
    date_incid = datetime.strptime(sorted(list(dict.fromkeys(list(df_incid_france['jour'].values))))[-1], '%Y-%m-%d').strftime('%d %B')
    tweet ="Chiffres #Covid19 France :\n• {} personnes décédées en milieu hospitalier ({}), {} sur 7 jours ({}{})\n• {} admissions à l'hôpital ({}), {} sur 7 jours ({}{})\n• {} cas positifs ({}), {} sur 7 jours ({}{})\n➡️ Plus d'infos : covidtracker.fr/covidtracker-france".format(deaths, lastday_df_new.strftime('%d/%m'), deaths_tendance, deaths_sign, deaths-deaths_j7, hosp, lastday_df_new.strftime('%d/%m'), hosp_tendance, hosp_sign, hosp-hosp_j7, tests, lastday_df_incid.strftime('%d/%m'), tests_tendance, tests_sign, tests-tests_j7) # toDo 
    
    images_path =["images/charts/france/var_journ_lines_recent.jpeg", "images/charts/france/entrees_sorties_hosp_rea_ROLLING_recent.jpeg", "images/charts/france/dc_new_bar.jpeg", "images/charts/france/reffectif.jpeg"]
    media_ids = []
    
    for filename in images_path:
        res = api.media_upload(filename)
        media_ids.append(res.media_id)

    # to attach the media file 
    api.update_status(status=tweet, media_ids=media_ids)
    #print(tweet)
    
    
def tweet_france_maps():
    _, _, dates, _, _, _, _, df_incid, _ = data.import_data()
    lastday_df_incid = datetime.strptime(df_incid['jour'].max(), '%Y-%m-%d')
    
    ## TWEET2
    df_incid_lastday = df_incid.loc[df_incid['jour']==df_incid['jour'].max(), :]
    nb_dep = len(df_incid_lastday.loc[df_incid_lastday['incidence_color']=='Alerte', :]) + len(df_incid_lastday.loc[df_incid_lastday['incidence_color']=='Alerte Renforcée', :]) + len(df_incid_lastday.loc[df_incid_lastday['incidence_color']=='Alerte Maximale', :])
    
    images_path2 =["images/charts/france/dep-map-incid-cat/latest.jpeg"]
    media_ids2 = []
    
    for filename in images_path2:
        res = api.media_upload(filename)
        media_ids2.append(res.media_id)
        
    tweet2 = "🔴 {} départements devraient être classés rouge, car ils dépassent le niveau d'alerte de 50 cas pour 100 000 habitants en 7 jours (données du {})\n➡️ Plus d'infos : covidtracker.fr/covidtracker-france".format(nb_dep, lastday_df_incid.strftime('%d/%m'))
    api.update_status(status=tweet2, media_ids=media_ids2)
    #print(tweet2)
    
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
    tweet ="Données du #Covid19 dans le monde au {} :\n+ {} cas en 24h, soit {} au total\n+ {} décès en 24h, soit {} au total\n➡️ Plus d'infos : covidtracker.fr/covidtracker-world\n".format(date_str, f"{new_cases:,d}".replace(',', ' '), f"{sum_cases:,d}".replace(',', ' '), f"{new_deaths:,d}".replace(',', ' '), f"{sum_deaths:,d}".replace(',', ' ')) # toDo 
    #image_path ="images/charts/cases_world.jpeg"
    
    images_path =["images/charts/cases_world.jpeg", "images/charts/deaths_world.jpeg"]
    media_ids = []
    
    for filename in images_path:
        res = api.media_upload(filename)
        media_ids.append(res.media_id)

    # to attach the media file 
    api.update_status(status=tweet, media_ids=media_ids)
    #print(tweet)


# In[3]:


#tweet_world()
#tweet_france()
#tweet_france_maps()

