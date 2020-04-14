#!/usr/bin/env python
# coding: utf-8

# # COVID-19 Analysis
# Guillaume Rozier, 2020

# In[87]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

"""


# In[88]:


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
import chart_studio.plotly as py
import sys
import matplotlib.pyplot as plt
from plotly.validators.scatter.marker import SymbolValidator

colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet

#random.shuffle(colors)

chart_studio.tools.set_credentials_file(username='worldice', api_key='2iXFe4Ch2oPo1dpaBj8p')
today = datetime.now().strftime("%Y-%m-%d %H:%M")

"build : " + today


# In[89]:


upload = False
show = False
export = True


# In[90]:



"""if len(sys.argv) == 1:
    print("Error.\n Usage: covid-19 arg1 arg2 arg3")
    print("arg1: upload? (True/False)\n arg2: show charts? (True/False)\n arg3: export charts as png?")
    sys.exit()
"""
    
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

# In[91]:


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
# ### DATA

# #### Download data

# In[92]:


def download_data():
    #url_confirmed = "https://cowid.netlify.com/data/total_cases.csv"
    #url_deaths = "https://cowid.netlify.com/data/total_deaths.csv"
    url_confirmed_csse = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"    
    url_deaths_csse = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"    


    #r_confirmed = requests.get(url_confirmed)
    #r_deaths = requests.get(url_deaths)
    r_confirmed_csse = requests.get(url_confirmed_csse)
    r_deaths_csse = requests.get(url_deaths_csse)

    #with open('data/total_cases_who.csv', 'wb') as f:
        #f.write(r_confirmed.content)

    #with open('data/total_deaths_who.csv', 'wb') as f:
        #f.write(r_deaths.content)

    with open('data/total_cases_csse.csv', 'wb') as f:
            f.write(r_confirmed_csse.content)

    with open('data/total_deaths_csse.csv', 'wb') as f:
        f.write(r_deaths_csse.content)

    print("> data downloaded")
    #"build : " + today


# #### Import data and merge

# In[93]:


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

    print("> data imported")
    return df_confirmed_csse, df_deaths_csse, df_confirmed_perso, df_deaths_perso


# In[94]:


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


# In[95]:


def data_merge(data_confirmed, df_confirmed_perso, data_deaths, df_deaths_perso):
    data_confirmed = pd.merge(data_confirmed, df_confirmed_perso, how='outer').drop_duplicates(subset='date')
    data_deaths = pd.merge(data_deaths, df_deaths_perso, how='outer').drop_duplicates(subset='date')

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


# In[96]:


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
    data_confirmed_rolling['date'] = data_confirmed_rolling['date'].astype('datetime64[ns]') 

    data_deaths['date'] = data_deaths['date'].astype('datetime64[ns]') 
    data_deaths_rolling['date'] = data_deaths_rolling['date'].astype('datetime64[ns]') 

    date_int = [i for i in range(len(data_confirmed))]
    data_confirmed["date_int"] = date_int

    date_int = [i for i in range(len(data_deaths))]
    data_deaths["date_int"] = date_int
    
    #for c in countries:
     #    data_deaths[c+"_new"] = data_deaths[c].diff()
        #data_deaths.loc[vals.index, c+"_new"] = vals
    return data_confirmed, data_confirmed_rolling, data_deaths, data_deaths_rolling


# In[97]:


#print(data_confirmed_rolling.tail)


# #### Informations on countries (population, offset)

# In[98]:



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


# In[99]:


def final_df_exports(data_confirmed, data_deaths):
    data_confirmed.to_csv('data/data_confirmed.csv')
    data_deaths.to_csv('data/data_deaths.csv')
    print("> dfs exported")
    
def data_import():
    with open('data/info_countries.json', 'r') as f:
        countries = json.load(f)
    return pd.read_csv('data/data_confirmed.csv'), pd.read_csv('data/data_deaths.csv'), countries


# In[100]:


def update_data():
    # Data update:
    download_data()
    df_confirmed_csse, df_deaths_csse, df_confirmed_perso, df_deaths_perso = import_files()

    df_confirmed_csse = data_prep_csse(df_confirmed_csse)
    df_deaths_csse = data_prep_csse(df_deaths_csse)

    data_confirmed, data_deaths = data_merge(df_confirmed_csse, df_confirmed_perso, df_deaths_csse, df_deaths_perso)

    data_confirmed_rolling = rolling(data_confirmed)
    data_deaths_rolling = rolling(data_deaths)

    data_confirmed, data_confirmed_rolling, data_deaths, data_deaths_rolling = final_data_prep(data_confirmed, data_confirmed_rolling, data_deaths, data_deaths_rolling)

    offset_compute_export(data_confirmed, data_deaths)

    final_df_exports(data_confirmed, data_deaths)


# 
# 
# 
# 
# 
# 

# # Graphs

# In[ ]:





# ## Function

# In[101]:


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


# ## Function calls

# In[102]:


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
    


# In[103]:


data_deaths


# In[104]:


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


# In[105]:


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


# In[106]:


results = seir_model_with_soc_dist(init_vals, params, t)


# # Dashboard

# In[107]:


"""import chart_studio.dashboard_objs as dashboard
import IPython.display
from IPython.display import Image

my_dboard = dashboard.Dashboard()

box_cases = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:12',
    'title': 'scatter-for-dashboard'
}
box_cases_million = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:326',
    'title': 'scatter-for-dashboard'
}
box_cases_aligned = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:328',
    'title': 'scatter-for-dashboard'
}
box_cases_since = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:330',
    'title': 'scatter-for-dashboard'
}


box_deaths = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:5',
    'title': 'scatter-for-dashboard'
}
box_deaths_million = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:333',
    'title': 'scatter-for-dashboard'
}
box_deaths_aligned = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:335',
    'title': 'scatter-for-dashboard'
}
box_deaths_since = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': 'worldice:337',
    'title': 'scatter-for-dashboard'
}


text_for_box="ha"
box_text = {
    'type': 'box',
    'boxType': 'text',
    'text': text_for_box,
    'title': 'Markdown Options for Text Box'
}

my_dboard.insert(box_cases, 1)
my_dboard.insert(box_cases_million, 'below', 1)
my_dboard.insert(box_cases_aligned, 'below', 2)
my_dboard.insert(box_cases_since, 'below', 3)

my_dboard.insert(box_deaths, 'below', 4)
my_dboard.insert(box_deaths_million, 'below', 5)
my_dboard.insert(box_deaths_aligned, 'below', 6)
my_dboard.insert(box_deaths_since, 'below', 7)

my_dboard['layout']['size'] = 10000
my_dboard['settings']['title'] = 'COVID-19 Stats - @guillaumerozier - data: worldometer'

if show:
    my_dboard.get_preview()
print("done")"""


# In[108]:


"""import chart_studio.plotly as py

py.dashboard_ops.upload(my_dboard, 'COVID-19 Europe Dashboard', auto_open=False)"""


# ### Total cases (world)

# In[109]:


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


# In[110]:


"""
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
"""

