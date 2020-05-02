#!/usr/bin/env python
# coding: utf-8

# # COVID-19 World Charts
# Guillaume Rozier, 2020

# In[62]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

This file contains scripts that download data from CSSE (John Hopkins) Github Repository and then process it to build many graphes.
I'm currently cleaning the code, please come back soon it will be easier to read and edit it!

The charts are exported to 'charts/images/'.
Data is download to/imported from 'data/'.
"""


# In[63]:


import requests
import random
from tqdm import tqdm
import json
from datetime import date
from datetime import datetime
import numpy as np
import sys
import chart_studio
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
import chart_studio.plotly as py
import sys
import matplotlib.pyplot as plt
from plotly.validators.scatter.marker import SymbolValidator

colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet

#If you want to uplaod charts to your Plotly account (and switch "upload" to True just below):
#chart_studio.tools.set_credentials_file(username='', api_key='')

today = datetime.now().strftime("%Y-%m-%d %H:%M")
"build : " + today


# If you want to display charts here, please change "show" variable to True:

# In[64]:


upload = False
show = False
export = True


# In[65]:



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


# ## Functions

# In[66]:


def compute_offset(df, col_of_reference, col_to_align, countries):
        
    diffs = []
    for offset in range(len(df)-15):
        
        a = df[col_of_reference][1:].shift(offset, fill_value=0)/countries[col_of_reference]["pop"]
        b = df[col_to_align][1:]/countries[col_to_align]["pop"]
        
        if len(a) > len(b):
            a = a[:-2]
        m = min(len(a), len(b))
            
        delta = ((a[offset:] - b[offset:])**2)**(1/2)
        diffs.append(abs(delta.sum()))
        xa = [i for i in range(offset, len(a))]
        xb = [i for i in range(offset, len(b))]

    ret = diffs.index(min(diffs))

    if col_of_reference == col_to_align:
        return 0
    return ret


# 
# ## DATA

# #### Download data

# In[67]:


def download_data():
    #url_confirmed = "https://cowid.netlify.com/data/total_cases.csv"
    #url_deaths = "https://cowid.netlify.com/data/total_deaths.csv"
    url_confirmed_csse = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"    
    url_deaths_csse = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"    
    url_france_data = "https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv"

    #r_confirmed = requests.get(url_confirmed)
    #r_deaths = requests.get(url_deaths)
    r_confirmed_csse = requests.get(url_confirmed_csse)
    r_deaths_csse = requests.get(url_deaths_csse)
    r_france_data = requests.get(url_france_data)

    #with open('data/total_cases_who.csv', 'wb') as f:
        #f.write(r_confirmed.content)

    #with open('data/total_deaths_who.csv', 'wb') as f:
        #f.write(r_deaths.content)

    with open('data/total_cases_csse.csv', 'wb') as f:
            f.write(r_confirmed_csse.content)

    with open('data/total_deaths_csse.csv', 'wb') as f:
        f.write(r_deaths_csse.content)
    
    with open('data/france_data.csv', 'wb') as f:
        f.write(r_france_data.content)

    print("> data downloaded")
    #"build : " + today


# #### Import data and merge

# In[68]:


def import_files(): 
    # CSSE data
    df_confirmed_csse = pd.read_csv('data/total_cases_csse.csv')
    df_deaths_csse = pd.read_csv('data/total_deaths_csse.csv')

    # WHO data
    #df_confirmed_who = pd.read_csv('data/total_cases_who.csv')
    #df_deaths_who = pd.read_csv('data/total_deaths_who.csv')

    # Perso data
    df_confirmed_perso = pd.read_csv('data/total_cases_perso.csv')
    df_deaths_perso = pd.read_csv('data/total_deaths_perso.csv')
    df_france_data = pd.read_csv('data/france_data.csv')

    print("> data imported")
    return df_confirmed_csse, df_deaths_csse, df_confirmed_perso, df_deaths_perso, df_france_data


# In[69]:


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

#"build : " + today


# In[70]:


def data_merge(data_confirmed, df_confirmed_perso, data_deaths, df_deaths_perso, df_france_data):
    """data_confirmed['date'] = data_confirmed['date'].astype('datetime64[ns]') 
    data_deaths['date'] = data_deaths['date'].astype('datetime64[ns]') 

    df_france_data = df_france_data[df_france_data['granularite']=='pays']
    df_france_data_deaths = pd.DataFrame()
    df_france_data_deaths['date'] = df_france_data['date']
    df_france_data_deaths['France'] = df_france_data['deces']
    df_france_data_deaths = df_france_data_deaths.dropna().drop_duplicates(subset=['date'], keep='last').reset_index()
    df_france_data_deaths['date'] = df_france_data_deaths['date'].astype('datetime64[ns]') 
    #data_deaths = pd.merge(df_france_data_deaths, data_deaths, how='outer').drop_duplicates(subset=['date'])
    #data_deaths = pd.merge(data_deaths[['date','France']], df_france_data_deaths, how='left') 
    data_deaths.set_index('date').join(df_france_data_deaths.set_index('date'))
    
    df_france_data_confirmed = pd.DataFrame()
    df_france_data_confirmed['date'] = df_france_data['date']
    df_france_data_confirmed['France'] = df_france_data['cas_confirmes']
    df_france_data_confirmed = df_france_data_confirmed.dropna().drop_duplicates(subset=['date']).reset_index()
    df_france_data_confirmed['date'] = df_france_data_confirmed['date'].astype('datetime64[ns]') 
    data_confirmed = pd.merge(data_confirmed, df_france_data_confirmed, how='outer').drop_duplicates(subset=['date'], keep='last')
    """
    data_confirmed = pd.merge(data_confirmed, df_confirmed_perso, how='outer').drop_duplicates(subset='date')
    data_deaths = pd.merge(data_deaths, df_deaths_perso, how='outer').drop_duplicates(subset='date')

    #######
    #date_int = [i for i in range(len(data_confirmed))]
    #data_confirmed["date_int"] = date_int

    #date_int = [i for i in range(len(data_deaths))]
    #data_deaths["date_int"] = date_int

    "build : " + today
    #data_confirmed['date']
    #df_deaths_perso.iloc[-1]
    
    #for c in countries:
     #    data_deaths[c+"_new"] = data_deaths[c].diff()
    return data_confirmed, data_deaths


# In[71]:


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


def final_data_prep(data_confirmed, data_confirmed_rolling, data_deaths, data_deaths_rolling):
    # Date conversion
    data_confirmed['date'] = data_confirmed['date'].astype('datetime64[ns]') 
    #data_confirmed_rolling['date'] = data_confirmed_rolling['date'].astype('datetime64[ns]') 

    data_deaths['date'] = data_deaths['date'].astype('datetime64[ns]') 
    #data_deaths_rolling['date'] = data_deaths_rolling['date'].astype('datetime64[ns]') 

    date_int = [i for i in range(len(data_confirmed))]
    data_confirmed["date_int"] = date_int

    date_int = [i for i in range(len(data_deaths))]
    data_deaths["date_int"] = date_int
    
    return data_confirmed, data_confirmed_rolling, data_deaths, data_deaths_rolling


# In[72]:


#print(data_confirmed_rolling.tail)


# #### Informations on countries (population, offset)

# In[73]:



def offset_compute_export(data_confirmed, data_deaths):
    # Importing informations on countries

    with open('data/info_countries.json', 'r') as f:
        countries = json.load(f)

    # Computing offset
    i = 0
    for c in tqdm(countries):
        countries[c]['offset_confirmed'] = compute_offset(data_confirmed, 'Italy', c, countries)
        countries[c]['offset_deaths'] = compute_offset(data_deaths, 'Italy', c, countries)
        countries[c]['color'] = i
        i += 1
    # Exporting informations on countries
    with open('data/info_countries.json', 'w') as fp:
        json.dump(countries, fp)

    print("> pop data imported")
    "build : " + today


# In[74]:


def final_df_exports(data_confirmed, data_deaths):
    data_confirmed.to_csv('data/data_confirmed.csv')
    data_deaths.to_csv('data/data_deaths.csv')
    print("> dfs exported")
    
def data_import():
    with open('data/info_countries.json', 'r') as f:
        countries = json.load(f)
    return pd.read_csv('data/data_confirmed.csv'), pd.read_csv('data/data_deaths.csv'), countries


# In[75]:


def update_data():
    # Data update:
    download_data()
    df_confirmed_csse, df_deaths_csse, df_confirmed_perso, df_deaths_perso, df_france_data = import_files()

    df_confirmed_csse = data_prep_csse(df_confirmed_csse)
    df_deaths_csse = data_prep_csse(df_deaths_csse)

    data_confirmed, data_deaths = data_merge(df_confirmed_csse, df_confirmed_perso, df_deaths_csse, df_deaths_perso, df_france_data)

    #data_confirmed_rolling = rolling(data_confirmed)
    #data_deaths_rolling = rolling(data_deaths)

    data_confirmed, data_confirmed_rolling, data_deaths, data_deaths_rolling = final_data_prep(data_confirmed, "data_confirmed_rolling", data_deaths, "data_deaths_rolling")
    
    offset_compute_export(data_confirmed, data_deaths)

    final_df_exports(data_confirmed, data_deaths)


# In[76]:


"""df_confirmed_csse, df_deaths_csse, df_confirmed_perso, df_deaths_perso, df_france_data = import_files()

df_confirmed_csse = data_prep_csse(df_confirmed_csse)
df_deaths_csse = data_prep_csse(df_deaths_csse)
df_confirmed_csse['date'] = df_confirmed_csse['date'].astype('datetime64[ns]') 

df_france_data = df_france_data[df_france_data['granularite']=='pays']



df_france_data_deaths = pd.DataFrame()
df_france_data_deaths['date'] = df_france_data['date']
df_france_data_deaths['France'] = df_france_data['deces']
df_france_data_deaths = df_france_data_deaths.dropna().drop_duplicates(subset=['date']).reset_index()
#df_france_data_deaths['date'] = df_france_data_deaths['date'].astype('datetime64[ns]') 
data_confirmed = pd.merge(data_deaths_csse, df_france_data_deaths, how='outer')



df_france_data_confirmed = pd.DataFrame()
df_france_data_confirmed['date'] = df_france_data['date']
df_france_data_confirmed['France'] = df_france_data['cas_confirmes']
df_france_data_confirmed = df_france_data_confirmed.dropna().drop_duplicates(subset=['date']).reset_index()
df_france_data_confirmed['date'] = df_france_data_confirmed['date'].astype('datetime64[ns]') 
data_confirmed = pd.merge(df_confirmed_csse, df_france_data_confirmed, how='outer')"""


# In[77]:


"""download_data()
df_confirmed_csse, df_deaths_csse, df_confirmed_perso, df_deaths_perso, df_france_data = import_files()

df_confirmed_csse = data_prep_csse(df_confirmed_csse)
df_deaths_csse = data_prep_csse(df_deaths_csse)

#data_confirmed['date'] = data_confirmed['date'].astype('datetime64[ns]') 
data_deaths['date'] = data_deaths['date'].astype('datetime64[ns]') 


df_france_data_confirmed = pd.DataFrame()
df_france_data_confirmed['date'] = df_france_data['date']
df_france_data_confirmed['France_corr'] = df_france_data['cas_confirmes']
df_france_data_confirmed = df_france_data_confirmed.dropna().drop_duplicates(subset=['date']).reset_index()
#df_france_data_confirmed['date'] = df_france_data_confirmed['date'].astype('datetime64[ns]') 
data_confirmed = pd.merge(data_confirmed, df_france_data_confirmed, how='outer').drop_duplicates(subset=['date'], keep='last')
data_confirmed.join(df_france_data_confirmed.set_index('date'), lsuffix='_caller', rsuffix='_other', on="date")"""


# 
# 
# 
# 
# 
# 

# # Graphs

# ## Function
# This fonction builds and export graphs.

# In[78]:


def chart(data, data_rolling, countries, by_million_inh = False, align_curves = False, last_d = 15, offset_name = 'offset_confirmed', type_ppl = "confirmed cases", name_fig="", since=False, min_rate=0, log=False, new=""):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    ### Symbols
    symbols = []
    for i in range(35):
        symbols.append(SymbolValidator().values[i])
    random.shuffle(symbols)
    ###
    
    fig = go.Figure()

    i = 0
    j = 0
    x_an=np.array([])
    y_an=np.array([])
    
    countries_last_val = []
    countries_array = []
    for c in countries:
        if by_million_inh:
             val = data[c][len(data) - 1]/countries[c]['pop']
        else:
            val = data[c][len(data) - 1]
            
        countries_last_val.append(val)
        countries_array.append(c)
        
    ind = np.argsort(countries_last_val)
    countries_array = np.array(countries_array)
    countries_array = countries_array[ind][::-1]
        
    for c in countries_array:

        if align_curves:
            offset = countries[c][offset_name]
            offset2 = -offset
        else:
            offset = 0

        if offset==0: offset2 = None

        if by_million_inh:
            pop = countries[c]['pop']
        else:
            pop = 1
        
        date = 'date'
        offset3=0
        since_str = ""
        since_str_leg = ""
        
        if since:
            date = 'date_int'
            res = list(map(lambda i: i> min_rate, data[c+new].values / pop))
            offset2 = 0
            if True in res:
                ind = res.index(True) 
                offset2 = -ind
                since_str_leg = " [since {} days]".format(len(data) - ind)

            offset3 = offset2
            last_d = 0
            offset = 0
            since_str = " [since {}]".format(min_rate) #, type_ppl
            
            if by_million_inh:
                since_str = since_str[:-1] + "/1M inh.]"
                

        x = data[date][ -last_d - offset: offset2]
        y = data[c+new][-last_d - offset3:] / pop
        
        if offset != 0:
            name_legend = '{} [delayed by {} days]'.format(c, -offset)
        else:
            name_legend = '{} {}'.format(c, since_str_leg)
        txt=["" for i in range(len(data_rolling[c][-last_d - offset3:]))]
        txt[-1] = c
        fig.add_trace(go.Scatter(x = x, y = y,
                        mode='markers',
                        marker_color = colors[countries[c]['color']],
                        legendgroup = c,
                        marker_symbol = countries[c]['color'],
                        marker_size=9,
                        #marker_line_width=2,
                        opacity=1,
                        showlegend=True,
                        name = name_legend))
        
        fig.add_trace(go.Scatter(x = data_rolling[date][ -last_d - offset : offset2], y = data_rolling[c+new][-last_d - offset3:] / pop,
                        mode='lines',
                        marker_color = colors[countries[c]['color']],
                        opacity = 1,
                        legendgroup=c,
                        showlegend=False,
                        line=dict(width=2),
                        name = name_legend))
        i += 1
        j += 1
        
        if i >= len(colors):
            i = 0
            
        if j >= 40:
            j = 0
        
        if log and since and c=="Italy":
            date_start = data_rolling['date_int'].values[ -last_d - offset]
            
            x = data_rolling["date_int"][ -last_d - offset : offset2]
            
            max_values = 15
            for (rate, rate_str) in [(2**(1/10), "x2 every 10 days"), (2**(1/7), "x2 every 7 days"), (2**(1/3), "x2 every 3 days"), (2**(1/2), "x2 every 2 days"), (2**(1/5), "x2 every 5 days")]:
                
                y = rate ** (data_rolling["date_int"][ -last_d - offset : offset2].values - date_start) * min_rate
                
                fig.add_trace(go.Scatter(x = x[:max_values+1], y = y[:max_values+1],
                                mode='lines+text',
                                marker_color="grey",
                                opacity=1,
                                #text = rate_str,
                                textposition = "bottom right",
                                legendgroup="Tendance",
                                showlegend=False,
                                line=dict(
                                    width=1,
                                    dash='dot'
                                ),
                                name = "Tendance"))

                fig.add_trace(go.Scatter(x = [data_rolling["date_int"][ -last_d - offset : offset2].values[max_values]], y = [(rate ** (data_rolling["date_int"][ -last_d - offset : offset2].values - date_start) * min_rate)[max_values]],
                                mode='text',
                                marker_color="grey",
                                opacity=1,
                                text = rate_str,
                                textposition = "bottom right",
                                legendgroup="Tendance",
                                showlegend=False,
                                name = "Tendance"))
            
    ### END LOOP ###
    
    align_str = ""
    if align_curves:
        align_str = " [aligned]"
        
    million_str = ""
    million_str_ax = ""
    if by_million_inh:
        million_str = " for 1M inhabitants"
        million_str_ax = "/ nb of inhabitants (million)"
        
    delayed=""
    if align_curves:
        delayed="— delayed for some countries"
    if since:
        delayed ="— since {} {} {}".format(min_rate, type_ppl, million_str)
    
    fig.update_annotations(dict(
            xref="x",
            yref="y",
            showarrow=True,
            arrowhead=7
    ))
    log_str="linear"
    
    if log:
        log_str = "log"
    
    fig.update_layout(
        showlegend=True,
        title={
            'text': "COVID-19 <b>{}{}</b>{}{}".format(type_ppl, million_str, align_str, since_str),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="Day {} {}".format(delayed, ''),
        yaxis_type=log_str,
        yaxis_title="Total {} {}".format(type_ppl, million_str),
        titlefont = dict(
            size=28),
        annotations = [dict(xref='paper',
            yref='paper',
            x=0, y=1.05,
            showarrow=False,
            text ='Last update: {} ; Last data: {} ; Data: CSSE ; Author: @guillaumerozier'.format(today, str(data['date'].values[-1])[:10]))]
    )

    fig.update_xaxes(nticks = last_d)

    print("> graph built")

    if upload:
        py.plot(fig, filename = name_fig, auto_open=False)
        print("> graph uploaded")

    if show:
        fig.show()
        print("> graph showed")

    if export:
        path_log = ""
        if log:
            path_log = "log_yaxis/"
        fig.write_image("images/charts/{}{}.png".format(path_log, name_fig), scale=3, width=1100, height=700)
        fig.write_image("images/charts_sd/{}{}.png".format(path_log, name_fig), scale=0.5)
        plotly.offline.plot(fig, filename = 'images/html_exports/{}{}.html'.format(path_log, name_fig), auto_open=False)
        print("> graph exported\n")
    return fig


# In[79]:


update_data()
data_confirmed, data_deaths, countries = data_import()
data_confirmed_t = data_confirmed.T
data_confirmed_t.columns = data_confirmed_t.iloc[len(data_confirmed_t)-2]
data_confirmed_t = data_confirmed_t.drop(data_confirmed_t.index[-1])
data_confirmed_t = data_confirmed_t.drop(data_confirmed_t.index[-1])
data_confirmed_t = data_confirmed_t.drop(data_confirmed_t.index[0])

data_deaths_t = data_deaths.T
data_deaths_t.columns = data_deaths_t.iloc[len(data_deaths_t)-2]
data_deaths_t = data_deaths_t.drop(data_deaths_t.index[-1])
data_deaths_t = data_deaths_t.drop(data_deaths_t.index[-1])
data_deaths_t = data_deaths_t.drop(data_deaths_t.index[0])


# In[ ]:





# In[ ]:





# In[80]:


for (data, name_var) in [(data_deaths_t, "deaths"), (data_confirmed_t, "confirmed")]: 
    name_suffix="confirmed"
    type_ppl = "cas positifs"
    
    if "death" in name_var:
        name_suffix="deaths"
        type_ppl = "décès"
        
    ni, nj = 3, 5
    i, j = 1, 1

    dates = data.columns.values

    data = data.sort_values(by=[dates[-1]], ascending=False)
    data = data.diff(axis=1).rolling(axis=1, window=4).mean()

    countries_ordered = list(data.index.values[:15])
    #countries_ordered[:11] + [""] + countries_ordered[11:14] + [""] + countries_ordered[14:]
    max_value = 0

    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles = ["<b>" + c + "</b>" for c in countries_ordered], vertical_spacing = 0.06, horizontal_spacing = 0.01)

    sub = "<sub>par ordre décroissant du cumul total, moyenne mobile sur 4 jours  •  guillaumerozier.fr</sub>"

    max_value_diff = 0

    for country in countries_ordered:

        data_c = data.loc[country].rolling(window=7).mean()
        fig.add_trace(go.Bar(x = data.loc[country].index, y = data_c,
                            marker=dict(color = data_c.diff(), coloraxis="coloraxis"), ),
                      i, j)
        max_value = max(max_value, data_c.max())
        max_value_diff = max(max_value_diff, data_c.diff().max())

        rangemin = "2020-02-02"

        fig.update_xaxes(title_text="", range=[rangemin, "2020-05-05"], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=i, col=j)
        fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=1, linecolor='white', row=i, col=j)

        j+=1
        if j == nj+1 : #or ((i >= 3) & (j == nj))
            i+=1
            j=1


    for i in fig['layout']['annotations']:
        i['font'] = dict(size=20)

    #for annotation in fig['layout']['annotations']: 
            #annotation ['x'] = 0.5
    by_million_title = ""
    by_million_legend = ""

    fig.update_layout(
        barmode="overlay",
        margin=dict(
            l=0,
            r=25,
            b=0,
            t=160,
            pad=0
        ),
        bargap=0,
        paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
        plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5 
        coloraxis=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-max_value_diff/4, cmax=max_value_diff/4), 
                    coloraxis_colorbar=dict(
                        title="Nombre<br>quotidien<br>de {}<br>&#8205;<br>&#8205; ".format(type_ppl),
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=600,
                        yanchor="middle", y=0.5, xanchor="left", x=1.02,
                        ticks="outside", tickprefix="  ", ticksuffix="",
                        nticks=15,
                        tickfont=dict(size=15),
                        titlefont=dict(size=18)),

                    showlegend=False,

                     title={
                        'text': ("COVID19 : <b>nombre de {} quotidiens</b><br>"+sub).format(type_ppl),
                        'y':0.97,
                        'x':0.5,
                        'xref':"paper",
                         'yref':"container",
                        'xanchor': 'center',
                        'yanchor': 'middle'},
                        titlefont = dict(
                        size=40,
                        )
    )

    fig["layout"]["annotations"] += ( dict(
                            x=0.9,
                            y=0.015,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='Source :<br>Santé Publique France',
                            showarrow = False,
                            font=dict(size=12), 
                            opacity=0.5
                        ),)
    

    name_fig = "subplots_" + name_suffix
    fig.write_image("images/charts/{}.png".format(name_fig), scale=2, width=3000, height=1650)

    fig["layout"]["annotations"] += (
                    dict(
                        x=0.5,
                        y=1,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                        showarrow = False
                        ),
                        )
    plotly.offline.plot(fig, filename = 'images/html_exports/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)


    #fig.show()


# In[ ]:





# ## Function calls
# This block contains calls to above function for every chart.

# In[81]:


update_data()
data_confirmed, data_deaths, countries = data_import()

for log in False, True:
    # Confirmed cases
    name = "cases"
    print(name)
    chart(countries=countries,
          data = data_confirmed, 
          data_rolling = data_confirmed, 
          by_million_inh = False, 
          last_d = round(len(data_confirmed)/2),
          name_fig = name,
          log=log
         )

    name = "cases_per_1m_inhabitant"
    print(name)
    chart(countries=countries,
          data = data_confirmed, 
          data_rolling = data_confirmed, 
          by_million_inh = True, 
          last_d = round(len(data_confirmed)/2),
          name_fig = name,
          log=log
         )

    name = "cases_per_1m_inhabitant_aligned"
    print(name)
    chart(countries=countries,
          data = data_confirmed, 
          data_rolling = data_confirmed, 
          by_million_inh = True, 
          last_d = 40, 
          align_curves = True,
          offset_name = 'offset_confirmed',
          name_fig = name,
          log=log
         )

    name = "cases_per_1m_inhabitant_since"
    print(name)
    chart(countries=countries,
          data = data_confirmed, 
          data_rolling = data_confirmed, 
          by_million_inh = True, 
          align_curves = False,
          since=True,
          name_fig = name,
          min_rate=20,
          log=log
         )

    
    name = "cases_since"
    print(name)
    chart(countries=countries,
          data = data_confirmed, 
          data_rolling = data_confirmed, 
          by_million_inh = False, 
          align_curves = False,
          since=True,
          name_fig = name,
          min_rate=1000,
          log=log
         )
    

    # Deaths
    name = "deaths"
    print(name)
    chart(countries=countries,
          data = data_deaths, 
          data_rolling = data_deaths, 
          by_million_inh = False, 
          last_d = round(len(data_deaths)/2),
          type_ppl = "deaths",
          name_fig = name,
          log=log
         )
    
    """name = "deaths_new_since"
    print(name)
    chart(countries = countries,
          new = "_new",
          data = data_deaths,
          data_rolling = data_deaths, 
          by_million_inh = False, 
          last_d = round(len(data_deaths)/2),
          type_ppl = "deaths",
          name_fig = name,
          since=True,
          min_rate=10,
          log=log
         )"""

    name = "deaths_per_1m_inhabitant"
    print(name)
    chart(countries=countries,
          data = data_deaths, 
          data_rolling = data_deaths, 
          by_million_inh = True, 
          last_d = round(len(data_deaths)/2),
          type_ppl = "deaths",
          name_fig = name,
          log=log
         )

    name = "deaths_per_1m_inhabitant_aligned"
    print(name)
    chart(countries=countries,
          data = data_deaths, 
          data_rolling = data_deaths, 
          by_million_inh = True, 
          last_d = 35, 
          align_curves = True,
          offset_name = 'offset_deaths',
          type_ppl = "deaths",
          name_fig = name,
          log=log
         )

    name = "deaths_per_1m_inhabitant_since"
    print(name)
    chart(countries=countries,
          data = data_deaths, 
          data_rolling = data_deaths, 
          by_million_inh = True, 
          align_curves = False,
          type_ppl = "deaths",
          since=True,
          name_fig = name,
          min_rate=3,
          log=log
         )
    
    name = "deaths_since"
    print(name)
    chart(countries=countries,
          data = data_deaths, 
          data_rolling = data_deaths, 
          by_million_inh = False, 
          last_d = 20, 
          align_curves = False,
          type_ppl = "deaths",
          since=True,
          name_fig = name,
          min_rate=100,
          log=log
         )
    


# # EXPERIMENTATIONS (SEIR model)
# Currently not working.

# In[82]:


# Define parameters
t_max = 100
dt = .1
t = np.linspace(0, t_max, int(t_max/dt) + 1)
N = 10000
init_vals = 1 - 1/N, 1/N, 0, 0
alpha = 0.2
beta = 1.75
gamma = 0.5
rho = 0.5
params = alpha, beta, gamma, rho
# Run simulation


# In[83]:


def seir_model_with_soc_dist(init_vals, params, t):
    S_0, E_0, I_0, R_0 = init_vals
    S, E, I, R = [S_0], [E_0], [I_0], [R_0]
    alpha, beta, gamma, rho = params
    dt = t[1] - t[0]
    for _ in t[1:]:
        next_S = S[-1] - (rho*beta*S[-1]*I[-1])*dt
        next_E = E[-1] + (rho*beta*S[-1]*I[-1] - alpha*E[-1])*dt
        next_I = I[-1] + (alpha*E[-1] - gamma*I[-1])*dt
        next_R = R[-1] + (gamma*I[-1])*dt
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)
        R.append(next_R)
    return np.stack([S, E, I, R]).T


# In[84]:


results = seir_model_with_soc_dist(init_vals, params, t)

