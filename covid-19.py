#!/usr/bin/env python
# coding: utf-8

# # COVID-19 Analysis
# Guillaume Rozier, 2020

# In[5]:


#data_rolling

#df_confirmed_csse['France']


# In[6]:


import requests
import random
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

colors = plotly.colors.DEFAULT_PLOTLY_COLORS
random.shuffle(colors)

chart_studio.tools.set_credentials_file(username='worldice', api_key='2iXFe4Ch2oPo1dpaBj8p')
today = datetime.now().strftime("%Y-%m-%d %H:%M")

"build : " + today


# In[7]:


upload = False
show = True
export = True

if len(sys.argv) == 1:
    print("Error.\n Usage: covid-19 arg1 arg2 arg3")
    print("arg1: upload? (True/False)\n arg2: show charts? (True/False)\n arg3: export charts as png?")
    sys.exit()
    
if len(sys.argv) >= 2:
    if (sys.argv[1]).lower() == "true":
        upload = True
    
if len(sys.argv) >= 3:
    if (sys.argv[2]).lower() == "true":
        show = True

if len(sys.argv) >= 4:
    if (sys.argv[3]).lower() == "true":
        export = True
    
"build : " + today


# ##### Functions

# In[8]:


def compute_offset(df, col_of_reference, col_to_align):
        
    diffs = []
    for offset in range(len(df)-15):
        
        a = df[col_of_reference][1:].shift(offset, fill_value=0)/countries[col_of_reference]["pop"]
        b = df[col_to_align][1:]/countries[col_to_align]["pop"]
        
        if len(a) > len(b):
            a = a[:-2]
        m = min(len(a), len(b))
            
        delta = ((a[offset:] - b[offset:])**2)**(1/2)
        #print("offset : {}\t delta : {}".format(offset, delta.sum()))
        diffs.append(abs(delta.sum()))
        xa = [i for i in range(offset, len(a))]
        xb = [i for i in range(offset, len(b))]
        #plt.scatter(x=xa, y=a[offset:])
        #plt.scatter(x=xb, y=b[offset:])
        #plt.title("offset {}".format(offset, round(delta)))
        #plt.savefig("images/offset"+str(offset)+".png")
        #plt.clf()
    #print(diffs)
    #print(min(diffs))
    ret = diffs.index(min(diffs))


    if col_of_reference == col_to_align:
        return 0
    return ret
#r = compute_offset(data_deaths, "Italy", "France")
#print(r)
"build : " + today


# 
# ### DATA

# #### Download data

# In[9]:



url_confirmed = "https://cowid.netlify.com/data/total_cases.csv"
url_deaths = "https://cowid.netlify.com/data/total_deaths.csv"
url_confirmed_csse = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"    
url_deaths_csse = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"    


r_confirmed = requests.get(url_confirmed)
r_deaths = requests.get(url_deaths)
r_confirmed_csse = requests.get(url_confirmed_csse)
r_deaths_csse = requests.get(url_deaths_csse)

with open('data/total_cases_who.csv', 'wb') as f:
    f.write(r_confirmed.content)
    
with open('data/total_deaths_who.csv', 'wb') as f:
    f.write(r_deaths.content)
    
with open('data/total_cases_csse.csv', 'wb') as f:
    f.write(r_confirmed_csse.content)

with open('data/total_deaths_csse.csv', 'wb') as f:
    f.write(r_deaths_csse.content)
    
print("> data downloaded")
"build : " + today


# #### Import data and merge

# In[10]:


# CSSE data
df_confirmed_csse = pd.read_csv('data/total_cases_csse.csv')
df_deaths_csse = pd.read_csv('data/total_deaths_csse.csv')

# WHO data
df_confirmed_who = pd.read_csv('data/total_cases_who.csv')
df_deaths_who = pd.read_csv('data/total_deaths_who.csv')

# Perso data
df_confirmed_perso = pd.read_csv('data/total_cases_perso.csv')
df_deaths_perso = pd.read_csv('data/total_deaths_perso.csv')

#date_int = [i for i in range(len(df_confirmed))]
#df_confirmed["date_int"] = date_int

#date_int = [i for i in range(len(df_deaths))]
#df_deaths["date_int"] = date_int

print("> data merged")
"build : " + today


# In[11]:


def data_prep_csse(df0):
    df = df0.drop('Lat', axis=1)
    df = df.drop('Long', axis=1)
    df = df.drop('Province/State', axis=1)
    #df_csse_new2 = df_csse_new.groupby(['Country/Region'])
    df = df.T.reset_index()
    df.columns = df.iloc[0]
    df = df.rename(columns={"Country/Region": "date"})
    df = df.drop(df.index[0])
    dates = df['date'].values
    df = df.groupby(by=df.columns, axis=1).sum(numeric_only=True)
    df['date'] = dates
    return df

df_confirmed_csse = data_prep_csse(df_confirmed_csse)
df_deaths_csse = data_prep_csse(df_deaths_csse)
"build : " + today


# In[12]:


data_confirmed = df_confirmed_csse
data_deaths = df_deaths_csse

data_confirmed = pd.merge(data_confirmed, df_confirmed_perso, how='outer').drop_duplicates(subset='date')
data_deaths = pd.merge(data_deaths, df_deaths_perso, how='outer').drop_duplicates(subset='date')

"build : " + today
#data_confirmed['date']
#df_deaths_perso.iloc[-1]


# In[13]:


def rolling(df):
    df_r = df
    df_r[:len(df_r)-1].fillna(method='pad',inplace=True)
    df_r = df.rolling(5, win_type='gaussian', center=True).mean(std=2)
    df_r['date'] = df['date'].values
    df_r.iloc[len(df_r)-2] = df.iloc[-2]
    df_r.iloc[len(df_r)-1] = df.iloc[-1]

    #moins_2 = ((df.iloc[-3][:-1] + df.iloc[-1][:-1]) / 2).append(pd.Series([df.iloc[-2]["date"]]))
    #moins_1 = ((df.iloc[-3][:-1] + df.iloc[-1][:-1]) / 2).append(pd.Series([df.iloc[-1]["date"]]))

    #df_r.iloc[-2] = moins_2
    #df_r.iloc[-1] = moins_1
    #data_confirmed.loc[:, data_confirmed.columns != "date"]
    #df_r = df_r.drop(len(df_r)-1)
    #df_r = df_r.drop(len(df_r)-1)
    
    df_r.loc[len(df_r)-3, df_r.columns != "date" ] = ((df.iloc[-4][:-1] + df.iloc[-2][:-1])/2 + df.iloc[-3][:-1])/2
    df_r.loc[len(df_r)-3, "date"] = df.iloc[-3]["date"]
    
   # df_r.loc[len(df_r)-2, df_r.columns != "date" ] = ((df.iloc[-3][:-1] + df.iloc[-1][:-1])/2 + df.iloc[-2][:-1])/2
    #df_r.loc[len(df_r)-2, "date"] = df.iloc[-2]["date"]
    
    df_r.loc[len(df_r)-2, df_r.columns != "date" ] = (df.iloc[-3][:-1] + (df.iloc[-3][:-1] - df.iloc[-4][:-1]) / 2 + df.iloc[-2][:-1])/2
    df_r.loc[len(df_r)-2, "date"] = df.iloc[-2]["date"] 
    
    df_r.loc[len(df_r)-1, df_r.columns != "date" ] = (df.iloc[-2][:-1] + (df.iloc[-1][:-1] - df.iloc[-3][:-1]) / 2 + df.iloc[-1][:-1])/2
    df_r.loc[len(df_r)-1, "date"] = df.iloc[-1]["date"] 
    
    return df_r

data_confirmed_rolling = rolling(data_confirmed)
data_deaths_rolling = rolling(data_deaths)

# Date conversion
data_confirmed['date'] = data_confirmed['date'].astype('datetime64[ns]') 
data_confirmed_rolling['date'] = data_confirmed_rolling['date'].astype('datetime64[ns]') 

data_deaths['date'] = data_deaths['date'].astype('datetime64[ns]') 
data_deaths_rolling['date'] = data_deaths_rolling['date'].astype('datetime64[ns]') 

"build : " + today


# In[14]:


print(data_confirmed_rolling.tail)


# #### Informations on countries (population, offset)

# In[15]:


from tqdm import tqdm

# Importing informations on countries
with open('data/info_countries.json', 'r') as f:
    countries = json.load(f)
    
# Computing offset
for c in tqdm(countries):
    
    countries[c]['offset_confirmed'] = compute_offset(data_confirmed, 'Italy', c)
    countries[c]['offset_deaths'] = compute_offset(data_deaths, 'Italy', c)

# Exporting informations on countries
with open('data/info_countries.json', 'w') as fp:
    json.dump(countries, fp)
    
print("> pop data imported")
"build : " + today


# In[ ]:





# In[16]:


#data_confirmed['date']


# # Graphs

# ### Total cases for 1 million inhabitants

# In[17]:


fig = go.Figure()

last_d = round(len(data_confirmed)/2)
#data_confirmed_rolling = data_confirmed
from sklearn.svm import SVC

i=0
for country in countries:
    #model = SVC(kernel='poly')
    #model.fit(df_confirmed['date_int'][-last_d:].values.reshape(-1, 1), df_confirmed[country][-last_d:].fillna(0).values.reshape(-1, 1))
    #Y = model.predict(df_confirmed['date_int'][-last_d:].values.reshape(-1, 1))
    
    fig.add_trace(go.Scatter(x = data_confirmed['date'][-last_d:], y = data_confirmed[country][-last_d:]/countries[country]['pop'],
                    mode='markers',
                    marker_color=colors[i],
                    legendgroup=c,
                    marker_symbol="cross",
                    marker_size=4,
                    marker_line_color=colors[i],
                    #marker_line_width=2,
                    opacity=1,
                    showlegend=False,
                    name='{}'.format(country)))
    
    fig.add_trace(go.Scatter(x = data_confirmed_rolling['date'][-last_d:], y = data_confirmed_rolling[country][-last_d:]/countries[country]['pop'],
                    mode='lines',
                    marker_color=colors[i],
                    legendgroup=c,
                    showlegend=True,
                    name='{}'.format(country)
                    ))
    i+=1
    if i>=10:
        i=0
    #fig.add_trace(go.Scatter(x=df_confirmed['date'][-last_d:], y=Y/countries[country]['pop'],
     #               mode='lines',
     #               name='{}'.format(country)))
    
fig.update_layout(
    title="COVID-19 total cases over time for 1 million inhabitants",
    xaxis_title="Time (day)",
    yaxis_title="COVID-19 total confirmed cases / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, str(data_confirmed['date'].values[-1])[:10]))]
)
fig.update_xaxes(nticks = last_d)
print("> graph 1 built")
if upload:
    py.plot(fig, filename = 'cases', auto_open=False)
    
if show:
    fig.show()

if export:
    fig.write_image("images/cases_per_1m_inhabitant.png", scale=5, width=900, height=500)
    print("> graph 1 exported")


# ### Total cases for 1 million inhabitants [aligned]

# In[18]:


import plotly.graph_objects as go

fig = go.Figure()

last_d = 20
#countries["Luxembourg"]["offset_confirmed"] = 9
#countries["Belgium"]["offset_confirmed"] = 8
i=0
for c in countries:
    if c != "Belgium":
        offset = countries[c]['offset_confirmed']
        offset2 = offset
        
        if offset==0: offset2 = 1
        pop = countries[c]['pop']

        fig.add_trace(go.Scatter(x = data_confirmed['date'][ -last_d - offset : - offset2], y = data_confirmed[c][-last_d:] / pop,
                        mode='markers',
                        marker_color=colors[i],
                        legendgroup=c,
                        marker_symbol="cross",
                        marker_size=4,
                        marker_line_color=colors[i],
                        #marker_line_width=2,
                        opacity=1,
                        showlegend=False,
                        name='{} [delayed by {} days]'.format(c, -offset)))

        fig.add_trace(go.Scatter(x = data_confirmed_rolling['date'][ -last_d - offset : - offset2], y = data_confirmed_rolling[c][-last_d:] / pop,
                        mode='lines',
                        marker_color=colors[i],
                        opacity=1,
                        legendgroup=c,
                        showlegend=True,
                        name='{} [delayed by {} days]'.format(c, -offset)))
        i+=1
        if i >= 10:
            i=0

fig.update_layout(
    title="COVID-19 total cases over time for 1 million inhabitants [aligned for comparison]",
    xaxis_title="Time (day) — delayed for some countries",
    yaxis_title="COVID-19 total confirmed cases / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, data_confirmed['date'].values[-1]))]
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
    
    #print(data_confirmed.info())


# ### Total deaths for 1 million inhabitants

# In[19]:


import plotly.graph_objects as go
fig = go.Figure()
#data_deaths_rolling = data_deaths
last_d = round(len(data_deaths)/2)
i=0
for c in countries:
    pop = countries[c]["pop"]
    
    fig.add_trace(go.Scatter(x = data_deaths['date'][-last_d:], y = data_deaths[c][-last_d:] / pop,
                    mode='markers',
                    marker_color=colors[i],
                    legendgroup=c,
                    marker_symbol="cross",
                    marker_size=4,
                    marker_line_color=colors[i],
                    #marker_line_width=2,
                    opacity=1,
                    showlegend=False,
                    name='{}'.format(c)))
    
    fig.add_trace(go.Scatter(x = data_deaths_rolling['date'][-last_d:], y = data_deaths_rolling[c][-last_d:] / pop,
                    mode='lines',
                    marker_color=colors[i],
                    legendgroup=c,
                    showlegend=True,
                    name='{}'.format(c)))
    i+=1
    if i >= 10:
        i=0

fig.update_layout(
    title="COVID-19 deaths over time for 1 million inhabitants",
    xaxis_title="Time (day)",
    yaxis_title="COVID-19 total deaths / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, data_confirmed['date'].values[-1]))]
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

# In[20]:


import plotly.graph_objects as go
import plotly

fig = go.Figure()

last_d = 30
upset_ch = 1
i=0

for c in countries:
    offset = countries[c]['offset_deaths']
    offset2 = offset
    if offset==0: offset2 = 1
        
    pop = countries[c]['pop']
    offset = countries[c]['offset_deaths']
    if offset==0: offset2=-1
    fig.add_trace(go.Scatter(x = data_deaths['date'][-last_d-offset:], y=data_deaths[c][-last_d:]/pop,
                    mode='markers',
                    marker_color=colors[i],
                    legendgroup=c,
                    marker_symbol="cross",
                    marker_size=6,
                    marker_line_color=colors[i],
                    #marker_line_width=2,
                    opacity=1,
                    showlegend=False,
                    name='{} [delayed by {} days]'.format(c, -offset)))
    
    fig.add_trace(go.Scatter(x = data_deaths_rolling['date'][-last_d-offset:], y=data_deaths_rolling[c][-last_d:]/pop,
                    mode='lines',
                    marker_color=colors[i],
                    legendgroup=c,
                    showlegend=True,
                    name='{} [delayed by {} days]'.format(c, -offset)))
    i+=1
    if i >= 10:
        i=0
    
fig.update_layout(
    title="COVID-19 deaths over time for 1 million inhabitants [aligned for comparison]",
    xaxis_title="Time (day) — delayed for some countries",
    yaxis_title="COVID-19 total deaths / nb of inhabitants (million)",
    annotations = [dict(xref='paper',
        yref='paper',
        x=0, y=1.1,
        showarrow=False,
        text ='Last update: {} ; Last data: {}'.format(today, data_confirmed['date'].values[-1]))]
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

# In[21]:


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


# In[22]:


import chart_studio.plotly as py

#py.dashboard_ops.upload(my_dboard, 'COVID-19 Europe Dashboard', auto_open=False)


# ### Total cases (world)

# In[23]:


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

