#!/usr/bin/env python
# coding: utf-8

# # COVID-19 Analysis
# Guillaume Rozier, 2020

# In[2]:


import requests
import json
from datetime import date
from datetime import datetime
import numpy as np
import sys
import chart_studio
import pandas as pd
import plotly.graph_objects as go
import plotly
import chart_studio.plotly as py
import sys

chart_studio.tools.set_credentials_file(username='worldice', api_key='2iXFe4Ch2oPo1dpaBj8p')


# In[8]:


upload = False
show = True
print(sys.argv)
if len(sys.argv) == 1:
    print("Error.\n Usage: covid-19 arg1 arg2")
    print("arg1: upload? (True/False)\n arg2: show charts? (True/False)")
    sys.exit()
    
if len(sys.argv) >= 2:
    upload = sys.argv[1]
    
if len(sys.argv) >= 3:
    show = sys.argv[2]
    print(show)


# ##### Functions

# In[3]:


def compute_offset(df, col_of_reference, col_to_align):
    diffs = []
    for offset in range(len(df)):
        delta = df[col_of_reference][:].shift(offset) - df[col_to_align][:]
        diffs.append(abs(delta.mean()))
    ret = diffs.index(min(diffs))
    #print(ret)
    if col_of_reference == col_to_align:
        return 0
    return ret


# 
# ### DATA

# #### Download data

# In[4]:


today = datetime.now().strftime("%Y-%m-%d %H:%M")

url_confirmed = "https://cowid.netlify.com/data/total_cases.csv"
url_deaths = "https://cowid.netlify.com/data/total_deaths.csv"
    
r_confirmed = requests.get(url_confirmed)
r_deaths = requests.get(url_deaths)

with open('data/total_cases_who.csv', 'wb') as f:
    f.write(r_confirmed.content)
    
with open('data/total_deaths_who.csv', 'wb') as f:
    f.write(r_deaths.content)


# #### Import data and merge

# In[5]:


df_confirmed_who = pd.read_csv('data/total_cases_who.csv')
df_deaths_who = pd.read_csv('data/total_deaths_who.csv')

df_confirmed_perso = pd.read_csv('data/total_cases_perso.csv')
df_deaths_perso = pd.read_csv('data/total_deaths_perso.csv')
df_confirmed = df_confirmed_who
df_deaths = df_deaths_who
#df_confirmed = pd.concat([df_confirmed_who, df_confirmed_perso], keys=['date'])
#df_confirmed = pd.merge(df_confirmed_who, df_confirmed_perso, how='outer')
#df_deaths = pd.merge(df_deaths_who, df_deaths_perso, how='outer')


# In[84]:


df_confirmed


# #### Informations on countries (population, offset)

# In[6]:


# Importing informations on countries
with open('data/info_countries.json', 'r') as f:
    countries = json.load(f)
    
# Computing offset
for c in countries:
    countries[c]['offset'] = compute_offset(df_confirmed, 'Italy', c)

# Exporting informations on countries
with open('data/info_countries.json', 'w') as fp:
    json.dump(countries, fp)


# # Graphs

# ### Total cases for 1 million inhabitants

# In[28]:


fig = go.Figure()

last_d = len(df_confirmed)
      
for country in countries:
    print(country)
    fig.add_trace(go.Scatter(x=df_confirmed['date'][-last_d:], y=df_confirmed[country][-last_d:]/countries[country]['pop'],
                    mode='lines+markers',
                    name='{}'.format(country)))

fig.update_layout(
    title="COVID-19 total cases over time for 1 million inhabitants",
    xaxis_title="Time (day)",
    yaxis_title="COVID-19 total confirmed cases / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, df_confirmed['date'].values[-1]))]
)
fig.update_xaxes(nticks = last_d)
#plotly.offline.plot(fig, filename = 'cases.html', auto_open=False)
#fig.write_image('cases.png')
if upload:
    py.plot(fig, filename = 'cases', auto_open=False)
    
if show:
    fig.show()
    
#fig.write_image("images/cases_per_1m_inhabitant.png", scale=8, width=1000, height=600)


# ### Total cases (world)

# In[21]:


fig = go.Figure()

last_d = len(df_confirmed)

for col in df_confirmed.columns[2:]:
    fig.add_trace(go.Scatter(x=df_confirmed['date'][-last_d:], y=df_confirmed[col][-last_d:],
                    mode='lines+markers',
                    name='{}'.format(col)))

fig.update_layout(
    title="COVID-19 total cases over time",
    xaxis_title="Time (day)",
    yaxis_title="COVID-19 total confirmed cases",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, df_confirmed['date'].values[-1]))]
)
fig.update_xaxes(nticks = last_d)
plotly.offline.plot(fig, filename = 'cases.html', auto_open=False)
#fig.write_image('cases.png')
if upload:
    py.plot(fig, filename = 'cases', auto_open=False)
    
if show:
    fig.show()
    
#fig.write_image("images/cases.png", scale=8, width=1000, height=600)


# ### Total cases for 1 million inhabitants [aligned]

# In[24]:


import plotly.graph_objects as go

fig = go.Figure()

last_d = 20
countries["Luxembourg"]["offset"] = 11
countries["Belgium"]["offset"] = 8

for c in countries:
    offset = countries[c]['offset']
    if offset==0: offset2=-1
    pop = countries[c]['pop']
    print(offset)
    fig.add_trace(go.Scatter(x=df_confirmed['date'][ -last_d - offset:], y=df_confirmed[c][-last_d:]/pop,
                    mode='lines+markers',
                    name='{} [delayed by {} days]'.format(c, -offset)))

fig.update_layout(
    title="COVID-19 total cases over time for 1 million inhabitants [aligned for comparison]",
    xaxis_title="Time (day) — delayed for some countries",
    yaxis_title="COVID-19 total confirmed cases / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, df_confirmed['date'].values[-1]))]
)


fig.update_xaxes(nticks = last_d)
plotly.offline.plot(fig, filename = 'cases_aligned.html', auto_open=False)

if upload:
    py.plot(fig, filename = 'cases-aligned', auto_open=False)

if show:
    fig.show()
#py.iplot(fig, filename='covid_aligned.html')
#fig.write_image("images/cases_per_1m_inhabitant_aligned.png", scale=8, width=1000, height=600)


# ### Total deaths for 1 million inhabitants

# In[25]:


import plotly.graph_objects as go
fig = go.Figure()

last_d = len(df_deaths)

for c in countries:
    pop = countries[c]["pop"]
    fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d:], y=df_deaths[c][-last_d:] / pop,
                    mode='lines+markers',
                    name='{}'.format(c)))

fig.update_layout(
    title="COVID-19 deaths over time for 1 million inhabitants",
    xaxis_title="Time (day)",
    yaxis_title="COVID-19 total deaths / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, df_confirmed['date'].values[-1]))]
)
fig.update_xaxes(nticks = last_d)
plotly.offline.plot(fig, filename = 'deaths.html', auto_open=False)

if upload:
    py.plot(fig, filename = 'deaths', auto_open=False)
    
if show:
    fig.show()
#fig.write_image("images/deaths_per_1m_inhabitant.png", scale=8, width=1000, height=600)


# ### Total deaths for 1 million inhabitants [aligned]

# In[26]:


import plotly.graph_objects as go
import plotly

fig = go.Figure()

last_d = 16
offset_france = compute_offset(df_confirmed, 'Italy', 'France')
offset_uk = compute_offset(df_confirmed, 'Italy', 'United Kingdom')
offset_sp = compute_offset(df_confirmed, 'Italy', 'Spain')
offset_ge = compute_offset(df_confirmed, 'Italy', 'Germany')
upset_ch = 1

for c in countries:
    pop = countries[c]['pop']
    offset = countries[c]['offset']
    if offset==0: offset2=-1
    fig.add_trace(go.Scatter(x = df_deaths['date'][-last_d-offset:], y=df_deaths[c][-last_d:]/pop,
                    mode='lines+markers',
                    name='{} [delayed by {} days]'.format(c, -offset)))
    
"""
fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d-offset_france:-offset_france], y=df_deaths['France'][-last_d:]/pop_fr,
                    mode='lines+markers',
                    name='France [delayed by {} days]'.format(-offset_france)))
fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d:], y=df_deaths['Italy'][-last_d:]/pop_it,
                    mode='lines+markers',
                    name='Italy [reference]'))
fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d-offset_uk:-offset_uk], y=df_deaths['United Kingdom'][-last_d:]/pop_uk,
                    mode='lines+markers',
                    name='UK [delayed by {} days]'.format(-offset_uk)))

fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d:], y=df_deaths['China'][upset_ch : upset_ch+last_d]/pop_ch,
                    mode='lines+markers',
                    name='CH [delayed by {} days]'.format(len(df_confirmed)-upset_ch)))
fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d-offset_sp:-offset_sp], y=df_deaths['Spain'][-last_d:]/pop_sp,
                    mode='lines+markers',
                    name='Spain [delayed by {} days]'.format(-offset_sp)))
fig.add_trace(go.Scatter(x=df_deaths['date'][-last_d-offset_ge:-offset_ge], y=df_deaths['Germany'][-last_d:]/pop_ge,
                    mode='lines+markers',
                    name='Germany [delayed by {} days]'.format(-offset_ge)))

"""
fig.update_layout(
    title="COVID-19 deaths over time for 1 million inhabitants [aligned for comparison]",
    xaxis_title="Time (day) — delayed for some countries",
    yaxis_title="COVID-19 total deaths / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, df_confirmed['date'].values[-1]))]
)

fig.update_xaxes(nticks = 30)

if upload:
    py.plot(fig, filename = 'deaths-aligned', auto_open=False)
#plotly.offline.plot(fig, filename = 'deaths_aligned.html', auto_open=False)
#py.iplot(fig, filename='covid_aligned.html')

if show:
    fig.show()
    
#fig.write_image("images/deaths_per_1m_inhabitant_aligned.png", scale=8, width=1000, height=600)


# # Dashboard

# In[66]:


import chart_studio.dashboard_objs as dashboard
import IPython.display
from IPython.display import Image

my_dboard = dashboard.Dashboard()

box_cases = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:12',
    'title': 'scatter-for-dashboard'
}
box_cases_aligned = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:7',
    'title': 'scatter-for-dashboard'
}
box_deaths = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:5',
    'title': 'scatter-for-dashboard'
}
box_deaths_aligned = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:3',
    'title': 'scatter-for-dashboard',
}
text_for_box="ha"
box_text = {
    'type': 'box',
    'boxType': 'text',
    'text': text_for_box,
    'title': 'Markdown Options for Text Box'
}

my_dboard.insert(box_cases, 1)

my_dboard.insert(box_deaths, 'below', 1)
my_dboard.insert(box_cases_aligned, 'below', 1)

my_dboard.insert(box_deaths_aligned, 'below', 3)

my_dboard['layout']['size'] = 2500
my_dboard['settings']['title'] = 'COVID-19 Stats - @guillaumerozier - data: worldometer'

if show:
    my_dboard.get_preview()


# In[68]:


import chart_studio.plotly as py

#py.dashboard_ops.upload(my_dboard, 'COVID-19 Europe Dashboard', auto_open=False)

