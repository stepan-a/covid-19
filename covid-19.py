#!/usr/bin/env python
# coding: utf-8

# # COVID-19 Analysis
# Guillaume Rozier, 2020

# In[43]:


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
import matplotlib.pyplot as plt

chart_studio.tools.set_credentials_file(username='worldice', api_key='2iXFe4Ch2oPo1dpaBj8p')
today = datetime.now().strftime("%Y-%m-%d %H:%M")

"build : " + today


# In[78]:


upload = False
show = False
export = True

if len(sys.argv) == 1:
    print("Error.\n Usage: covid-19 arg1 arg2 arg3")
    print("arg1: upload? (True/False)\n arg2: show charts? (True/False)\n arg3: export charts as png?")
    sys.exit()
    
if len(sys.argv) >= 2:
    if lower(sys.argv[1]) == "true":
        upload = True
    
if len(sys.argv) >= 3:
    if lower(sys.argv[2]) == "true":
        show = True

if len(sys.argv) >= 4:
    if lower(sys.argv[3]) == "true":
        export = True
    
"build : " + today


# ##### Functions

# In[54]:


def compute_offset(df, col_of_reference, col_to_align):
    diffs = []
    for offset in range(len(df)):
        a = df[col_of_reference][1:].shift(offset).dropna()
        b = df[col_to_align][1:].dropna()
        if len(a) > len(b):
            a = a[:-2]
        m = min(len(a), len(b))
            
        delta = a[ -m : ]**2 - b[-m:]**2
        diffs.append(abs(delta.mean()))
        xa = [i for i in range(len(a))]
        xb = [i for i in range(len(b))]
        #plt.scatter(x=xa, y=a)
        #plt.scatter(x=xb, y=b)
        #plt.savefig("images/offset"+str(offset)+".png")
    ret = diffs.index(min(diffs))
    #print("a", a)
    #print("b", b)
    #print("d", delta)

    if col_of_reference == col_to_align:
        return 0
    return ret

"build : " + today


# 
# ### DATA

# #### Download data

# In[66]:



url_confirmed = "https://cowid.netlify.com/data/total_cases.csv"
url_deaths = "https://cowid.netlify.com/data/total_deaths.csv"
    
r_confirmed = requests.get(url_confirmed)
r_deaths = requests.get(url_deaths)

with open('data/total_cases_who.csv', 'wb') as f:
    f.write(r_confirmed.content)
    
with open('data/total_deaths_who.csv', 'wb') as f:
    f.write(r_deaths.content)
print("> data downloaded")
"build : " + today


# #### Import data and merge

# In[67]:


df_confirmed_who = pd.read_csv('data/total_cases_who.csv')
df_deaths_who = pd.read_csv('data/total_deaths_who.csv')

df_confirmed_perso = pd.read_csv('data/total_cases_perso.csv')
df_deaths_perso = pd.read_csv('data/total_deaths_perso.csv')

#df_confirmed = pd.concat([df_confirmed_who, df_confirmed_perso], keys=['date'])
df_confirmed = pd.merge(df_confirmed_who, df_confirmed_perso, how='outer')
df_deaths = pd.merge(df_deaths_who, df_deaths_perso, how='outer')

print("> data merged")
"build : " + today


# In[68]:


#df_confirmed
#df_deaths['France']


# #### Informations on countries (population, offset)

# In[69]:


# Importing informations on countries
with open('data/info_countries.json', 'r') as f:
    countries = json.load(f)
    
# Computing offset
for c in countries:
    countries[c]['offset_confirmed'] = compute_offset(df_confirmed, 'Italy', c)
    countries[c]['offset_deaths'] = compute_offset(df_deaths, 'Italy', c)

# Exporting informations on countries
with open('data/info_countries.json', 'w') as fp:
    json.dump(countries, fp)
print("> pop data imported")
"build : " + today


# # Graphs

# ### Total cases for 1 million inhabitants

# In[79]:


fig = go.Figure()

last_d = len(df_confirmed)
      
for country in countries:
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
print("> graph 1 built")
print("a")
print("upload: " + upload)
if upload:
<<<<<<< HEAD
    print("a1")
    py.plot(fig, filename = 'cases', auto_open=False)
    
print("b")
if show:
    fig.show()
print("c")
if export:
    fig.write_image("images/cases_per_1m_inhabitant.png", scale=5, width=900, height=500)
    print("> graph 1 exported")
print("d")

# ### Total cases (world)

# In[ ]:


"""
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
    
if export:
    fig.write_image("images/cases.png", scale=8, width=1000, height=600)
print("> graph 2 built")
"""


# ### Total cases for 1 million inhabitants [aligned]

# In[81]:


import plotly.graph_objects as go

fig = go.Figure()

last_d = 30
countries["Luxembourg"]["offset_confirmed"] = 9
countries["Belgium"]["offset_confirmed"] = 8

for c in countries:
    offset = countries[c]['offset_confirmed']
    offset2 = offset
    if offset==0: offset2 = 1
    pop = countries[c]['pop']

    fig.add_trace(go.Scatter(x = df_confirmed['date'][ -last_d - offset : - offset2], y = df_confirmed[c][-last_d:] / pop,
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

print("> graph 3 built")

if upload:
    py.plot(fig, filename = 'cases-aligned', auto_open=False)

if show:
    fig.show()
    
if export:
    fig.write_image("images/cases_per_1m_inhabitant_aligned.png", scale=5, width=900, height=500)
    print("> graph 3 exported")


# ### Total deaths for 1 million inhabitants

# In[82]:


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

print("> graph 4 built")
    
if upload:
    py.plot(fig, filename = 'deaths', auto_open=False)
    
if show:
    fig.show()
    
if export:
    fig.write_image("images/deaths_per_1m_inhabitant.png", scale=5, width=900, height=500)
    print("> graph 4 exported")


# ### Total deaths for 1 million inhabitants [aligned]

# In[77]:


import plotly.graph_objects as go
import plotly

fig = go.Figure()

last_d = 16
upset_ch = 1

for c in countries:
    offset = countries[c]['offset_deaths']
    offset2 = offset
    if offset==0: offset2 = 1
        
    pop = countries[c]['pop']
    offset = countries[c]['offset_deaths']
    if offset==0: offset2=-1
    fig.add_trace(go.Scatter(x = df_deaths['date'][-last_d-offset:], y=df_deaths[c][-last_d:]/pop,
                    mode='lines+markers',
                    name='{} [delayed by {} days]'.format(c, -offset)))
    

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

print("> graph 5 built")
    
if upload:
    py.plot(fig, filename = 'deaths-aligned', auto_open=False)
#plotly.offline.plot(fig, filename = 'deaths_aligned.html', auto_open=False)
#py.iplot(fig, filename='covid_aligned.html')

if show:
    fig.show()

if export:  
    fig.write_image("images/deaths_per_1m_inhabitant_aligned.png", scale=5, width=900, height=500)
    print("> graph 5 exported")


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

