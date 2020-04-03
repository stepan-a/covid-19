#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip3 install pygal
#!pip3 install pygal_maps_fr
import pygal_maps_fr
import pygal
from p_tqdm import p_map
from multiprocessing import Pool
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
from datetime import datetime
from tqdm import tqdm
import imageio
import json

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

colors = px.colors.qualitative.D3 + px.colors.qualitative.Dark24 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Alphabet


# In[2]:


build_gif_bool = False


# In[3]:


def download_data():
    pbar = tqdm(total=8)
    url_metadata = "https://www.data.gouv.fr/fr/organizations/sante-publique-france/datasets-resources.csv"
    url_geojson = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
    pbar.update(1)
    metadata = requests.get(url_metadata)
    pbar.update(2)
    geojson = requests.get(url_geojson)
    pbar.update(3)
    with open('data/france/metadata.csv', 'wb') as f:
        f.write(metadata.content)
    pbar.update(4)
    with open('data/france/dep.geojson', 'wb') as f:
        f.write(geojson.content)
    pbar.update(5)
    df_metadata = pd.read_csv('data/france/metadata.csv', sep=";")
    url_data = df_metadata[df_metadata['url'].str.contains("/donnees-hospitalieres-covid19")]["url"].values[0]
    pbar.update(6)
    data = requests.get(url_data)
    pbar.update(7)
    with open('data/france/donnes-hospitalieres-covid19.csv', 'wb') as f:
        f.write(data.content)
    pbar.update(8)

download_data()


# In[4]:


def import_data():
    
    pbar = tqdm(total=4)
    pbar.update(1)
    df = pd.read_csv('data/france/donnes-hospitalieres-covid19.csv', sep=";")
    df_regions = pd.read_csv('data/france/departments_regions_france_2016.csv', sep=",")
    df_reg_pop = pd.read_csv('data/france/population_regions.csv', sep=",")
    df_dep_pop = pd.read_csv('data/france/dep-pop.csv', sep=";")
    
    df = df.merge(df_regions, left_on='dep', right_on='departmentCode')
    df = df.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df = df.merge(df_dep_pop, left_on='dep', right_on='dep')
    #df_geojson = pd.read_csv('data/france/dep.geojson)
    df = df[df["sexe"] == 0]
    df['hosp_nonrea'] = df['hosp'] - df['rea']
    pbar.update(2)
    
    df['rea_pop'] = df['rea']/df['regionPopulation']*100000
    df['rea_deppop'] = df['rea']/df['departmentPopulation']*100000
    
    df['rad_pop'] = df['rad']/df['regionPopulation']*100000
    
    df['dc_pop'] = df['dc']/df['regionPopulation']*100000
    df['dc_deppop'] = df['dc']/df['departmentPopulation']*100000
    
    df['hosp_pop'] = df['hosp']/df['regionPopulation']*100000
    df['hosp_nonrea_pop'] = df['hosp_nonrea']/df['regionPopulation']*100000
    pbar.update(3)
    df_confirmed = pd.read_csv('data/data_confirmed.csv')
    pbar.update(4)
    
    deps = list(dict.fromkeys(list(df['departmentCode'].values))) 
    for d in deps:
        for col in ["dc", "rad", "rea", "hosp_nonrea"]:
            vals = df[df["dep"] == d][col].diff()
            df.loc[vals.index,col+"_new"] = vals
            df.loc[vals.index,col+"_new_deppop"] = vals / df.loc[vals.index,"departmentPopulation"]*100000

    return df, df_confirmed

df, df_confirmed = import_data()

df_region = df.groupby(['regionName', 'jour']).sum().reset_index()
#df_region["dc_cumsum"] = df.groupby(by=['regionName','jour']).sum().groupby(level=[0]).cumsum().reset_index()["dc"]
dates = list(dict.fromkeys(list(df['jour'].values))) 
df.dtypes


# In[5]:


fig = px.line(x=df_region['jour'], y=df_region['hosp'], color=df_region["regionName"], color_discrete_sequence=colors)
fig.update_layout(
    title={
                'text': "Nombre de <b>patients hospitalisés</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients hospitalisés")

name_fig = "hosp_line"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

#fig.show()


# In[6]:


fig = px.line(x=df_region['jour'], y=df_region['rea'], color=df_region["regionName"], color_discrete_sequence=colors)
fig.update_layout(
    title={
                'text': "Nombre de <b>patients en réanimation</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                    size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients en réanimation")

name_fig = "rea_line"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[7]:


df_rhin = df[df["dep"].isin(["67", "68"])]
fig = px.line(x=df_rhin['jour'], y=df_rhin['rea'], color=df_rhin["dep"], labels={'color':'Département'}, color_discrete_sequence=colors)

fig.update_layout(
    title={
                'text': "Nombre de <b>patients en réa. ou soins intensifs</b> en Ht et Bas Rhin",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                    size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients en réa. ou soins intensifs")

name_fig = "rea_rhin"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[ ]:





# # GIF

# In[8]:


with open('data/france/dep.geojson') as response:
    depa = json.load(response)
    
def map_gif(dates, imgs_folder, df, type_ppl, legend_title, min_scale, max_scale, colorscale, subtitle):
    i=1
    for date in tqdm(dates):
        if max_scale == -1:
            max_scale = df[type_ppl].max()
        df_map = pd.melt(df, id_vars=['jour','dep'], value_vars=[type_ppl])
        df_map = df_map[df_map["jour"] == date]

        data={}
        for dep in df_map["dep"].values:
            data[dep] = df_map[df_map["dep"] == dep]["value"]

        fig = px.choropleth(geojson=depa, 
                            locations=df_map['dep'], 
                            color=df_map['value'],
                            color_continuous_scale = colorscale,
                            range_color=(min_scale, max_scale),
                            featureidkey="properties.code",
                            scope='europe',
                            labels={'color':legend_title}
                                  )
        date_title = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')
        
        fig.update_geos(fitbounds="locations", visible=False)
        
        var_hab = 'pour 100k. hab.'
        pourcent = ''
        
        val_mean = round(df_map['value'].mean(), 1)
        
        n = len(dates)
        progressbar = i * '█' + (n-i) * '░'
        i += 1
        
        if type_ppl == 'surmortalite20':
            var_hab = ''
            pourcent = " %"
            if val_mean < 0:
                val_mean = "– " + str(abs(val_mean))
            else:
                val_mean = "+ " + str(val_mean)
                
        val_mean = str(val_mean).replace(".", ",")
        
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            title={
            'text': "{}".format(date_title),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=30),
            annotations = [
                dict(
                    x=0.54,
                    y=0.08,
                    xref='paper',
                    yref='paper',
                    xanchor = 'center',
                    text='Source : INSEE. Auteur : @guillaumerozier.',
                    showarrow = False
                ),
                dict(
                    x=0.54,
                    y=0.03,
                    xref = 'paper',
                    yref = 'paper',
                    text = progressbar,
                    xanchor = 'center',
                    showarrow = False,
                    font=dict(
                        size=14
                            )
                ),
                dict(
                    x=0.07,
                    y=0.47,
                    xref='paper',
                    yref='paper',
                    xanchor='left',
                    text='Moyenne France',
                    showarrow = False,
                    font=dict(
                        size=14
                            )
                ),
                dict(
                    x=0.07,
                    y=0.50,
                    xref='paper',
                    yref='paper',
                    xanchor='left',
                    text='{}{}'.format(val_mean, pourcent),
                    showarrow = False,
                    font=dict(
                        size=25
                            )
                ),
                
                dict(
                    x=0.07,
                    y=0.45,
                    xref='paper',
                    yref='paper',
                    xanchor='left',
                    text = var_hab,
                    showarrow = False,
                    font=dict(
                        size=14
                            )
                ),
                dict(
                    x=0.55,
                    y=0.9,
                    xref='paper',
                    yref='paper',
                    text=subtitle,
                    showarrow = False,
                    font=dict(
                        size=20
                            )
                )]
             ) 
        
        fig.update_geos(
            #center=dict(lon=-30, lat=-30),
            projection_rotation=dict(lon=12, lat=30, roll=8),
            #lataxis_range=[-50,20], lonaxis_range=[0, 200]
        )
        fig.write_image(imgs_folder.format(date), scale=1, width=900, height=700)
        #fig.show()

        #image = imageio.imread("images/charts/france/dep-map-img/{}.png".format(date))
        #writer.append_data(image)
        #i+=1
        #if i==len(dates):
            #for k in range(4):
               #writer.append_data(image)
    #images.append(imageio.imread("images/charts/france/dep-map_{}.png".format(date)))
    #imageio.mimsave('"images/charts/france/dep-map.gif"', images)

def build_gif(file_gif, imgs_folder, dates):
    i=0
    with imageio.get_writer(file_gif, mode='I', duration=0.3) as writer: 
        for date in tqdm(dates):
            image = imageio.imread(imgs_folder.format(date))
            writer.append_data(image)
            i+=1
            if i==len(dates):
                for k in range(4):
                    writer.append_data(image)


# In[34]:


#build_gif_bool = True
if build_gif_bool:
    imgs_folder = "images/charts/france/dep-map-img/{}.png"
    sub = 'Nombre de <b>personnes en réanimation</b> <br>par habitant de chaque département.'
    map_gif(dates, imgs_folder, df = df, type_ppl = "rea_deppop", legend_title="réan./100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map.gif", imgs_folder = "images/charts/france/dep-map-img/{}.png", dates=dates)


# In[35]:


if build_gif_bool:
    imgs_folder = "images/charts/france/dep-map-img-dc-cum/{}.png"
    sub = 'Nombre de <b>décès cumulés</b> <br>par habitant de chaque département.'
    map_gif(dates[1:], imgs_folder, df = df, type_ppl = "dc_deppop", legend_title="décès/100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map-dc-cum.gif", imgs_folder = "images/charts/france/dep-map-img-dc-cum/{}.png", dates=dates[1:])


# In[36]:


if build_gif_bool:
    imgs_folder = "images/charts/france/dep-map-img-dc-journ/{}.png"
    sub = 'Nombre de <b>décès quotidien</b> <br>par habitant de chaque département.'
    map_gif(dates[1:], imgs_folder, df = df, type_ppl = "dc_new_deppop", legend_title="décès/100k hab", min_scale = 0, max_scale=-1, colorscale ="Reds", subtitle=sub)
    build_gif(file_gif = "images/charts/france/dep-map-dc-journ.gif", imgs_folder = "images/charts/france/dep-map-img-dc-journ/{}.png", dates=dates[1:])


# In[12]:


df_last_d = df[df['jour'] == dates[-1]]
#deps_ordered = df_last_d.sort_values(by=['rea'], ascending=False)["dep"].values
deps_ordered = df_last_d.sort_values(by=['dep'], ascending=True)["dep"].values

fig = go.Figure()
for dep in deps_ordered:
    fig.add_trace(go.Scatter(x=df['jour'], y=df[df["dep"] == dep]["rea"],
                    mode='lines+markers',
                    name=dep,
                    line=dict(width=1.5)
                            ))
#fig = px.line(x=df['jour'], y=df['rea'], color=df["dep"], labels={'color':'Région (des dép.)'}, color_discrete_sequence=colors)
#fig.update_layout(
 #   title_text=''
#)
fig.update_layout(
    title={
                'text': "Nb. de <b>patients en réanimation</b> par département",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients en réa. ou soins intensifs")

name_fig = "rea_dep"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[13]:


df_region_last_d = df_region[df_region['jour'] == dates[-1]]
reg_ordered = df_region_last_d.sort_values(by=['rea'], ascending=False)["regionName"].values

fig = go.Figure()
for reg in tqdm(reg_ordered):
    showld = True
    for dep in deps_ordered:
        fig.add_trace(go.Scatter(x=df['jour'], y=df[ (df["regionName"] == reg) & (df["dep"] == dep) ]["rea"],
                        mode='lines+markers',
                        legendgroup = reg,
                        name = dep,
                        marker = dict(color = colors[list(reg_ordered).index(reg)]),
                        line=dict(width=1.5),
                        showlegend = showld))
        showld = False

fig.update_layout(
    title={
                'text': "Nb. de <b>patients en réanimation</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients en réanimation")

name_fig = "rea_reg"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[14]:



df_rean = df.groupby('jour').sum().reset_index()
df_rean["lim_rea"] = [14000 for i in range(len(dates))]
df_rean = pd.melt(df_rean, id_vars=['jour'], value_vars=['rea', 'lim_rea'])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'rea']['value'],
                    mode='lines+markers',
                    name='Nb. patients réa.'))

fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'lim_rea']['value'],
                    mode='lines',
                    name='Nombre de lits réa.'))

fig.update_layout(
    title={
                'text': "Nb. de <b>patients en réanimation</b> et de lits disponibles",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
            size=20),
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "capacite_rea"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[15]:



fig = px.line(x=df_region['jour'], y=df_region['hosp_pop'], labels={'color':'Région'}, color=df_region["regionName"], color_discrete_sequence=colors)
fig.update_layout(
    title={
                'text': "Nb. de <b>patients hospitalisés</b> <b>par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients hospitalisés/100k hab. (de ch. région)")

name_fig = "hosp_hab"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[16]:


fig = px.line(x=df_region['jour'], y=df_region['dc'], color=df_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors)
fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
    
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès cumulés")

name_fig = "dc_cum_line"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[17]:


fig = px.line(x=df_region['jour'], y = df_region['dc']/df_region['regionPopulation']*100000, labels={'color':'Région'}, color=df_region["regionName"], color_discrete_sequence=colors)

fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> par <b>habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. décès cumulés / 100k hab. de chaq. région")

name_fig = "dc_cum_hab_line"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[18]:


fig = px.bar(x=df_region['jour'], y = df_region['dc'], color=df_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors, opacity=0.9)

fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
    
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de décès cumulés")
#fig.show()

name_fig = "dc_cum_region"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=500)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[19]:



#df_region4 = df_region.groupby("regionName", "jour").sum().reset_index()
df_region_sans = df_region.drop( df_region[ df_region["regionName"].isin(["Martinique", "Guadeloupe", "Guyane", "La Réunion"]) ].index)
fig = go.Figure()


fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-4]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-4]]['dc'],
    name = datetime.strptime(dates[-4], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred',
    opacity=0.3
)).update_xaxes(categoryorder="total ascending")

fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-3]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-3]]['dc'],
    name = datetime.strptime(dates[-3], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred',
    opacity=0.4
))

fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-2]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-2]]['dc'],
    name = datetime.strptime(dates[-2], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred',
    opacity=0.5
))

fig.add_trace(go.Bar(
    x = df_region_sans[df_region_sans["jour"] == dates[-1]]['regionName'],
    y = df_region_sans[df_region_sans["jour"] == dates[-1]]['dc'],
    name = datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B'),
    marker_color='indianred'
)).update_xaxes(categoryorder="total ascending")


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='group', xaxis_tickangle=-45,
    
    title={
                'text': "<b>Décès cumulés</b> par région",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis_title="",
    yaxis_title="Nb. de décès cumulés",
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "dc_cum_region_comp"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1300, height=600)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[20]:


df_region3 = df_region[df_region["jour"]==dates[-1]].groupby("regionName").sum().reset_index()
fig = px.bar(x=df_region3['regionName'], y = df_region3['dc'], color_discrete_sequence=colors).update_xaxes(categoryorder="total descending")
fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b> ({})".format(dates[-1]),
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
        size=20),
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 
)
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de décès cumulés")

name_fig = "dc_cum"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=500)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()

#####


# In[21]:


df_region3 = df_region[df_region["jour"] == dates[-1]].groupby("regionName").sum().reset_index()
fig = px.bar(x=df_region3['regionName'], y = df_region3['dc_pop'], color_discrete_sequence=colors).update_xaxes(categoryorder="total descending")
fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
)
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de décès cumulés / 100k habitants de chaq. rég.")

name_fig = "dc_cum_hab"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=550)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[22]:


fig = go.Figure()
df_region3 = df_region[df_region["jour"] == dates[-1]].groupby("regionName").sum().reset_index()
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(
    x=df_region3['regionName'], 
    y = df_region3['dc'],
    name = "Nombre décès cumulés",
    width=0.3,
    marker_color='indianred'
),
             secondary_y = False).update_xaxes(categoryorder="total descending")

fig.add_trace(go.Bar(
    x=df_region3['regionName'], 
    y = df_region3['dc_pop'],
    name = "Nb. décès cum./100k hab.",
    marker_color='indianred',
    opacity=0.6,
    width=0.3,
    offset=0.15
    
),
             secondary_y = True)

fig.update_layout(
    barmode='group', 
    xaxis_tickangle=-45,
    
    title={
                'text': "Comparaison des <b>décès cumulés</b> et <b>décès cumulés par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis_title="",
        annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_yaxes(title_text="Nb. décès cumulés", secondary_y=False)
fig.update_yaxes(title_text="Nb. décès cumulés/100k hab.", secondary_y=True)

name_fig = "dc_cum_hab_nonhab_comp"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[23]:


df_region_sumj = df_region.groupby('jour').sum().reset_index()
df_region_sumj = pd.melt(df_region_sumj, id_vars=['jour'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['jour'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)
df_bar = df_region_sumj
data = df_bar[df_bar["variable"] == "dc"]
fig = go.Figure(go.Bar(x=data['jour'], y=data['value'], text=data['value'], textposition='auto', name='Décès', marker_color='#000000', opacity=0.8))

data = df_bar[df_bar["variable"] == "rea"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], text=data['value'], textposition='auto', name='Réanimation', marker_color='#FF0000', opacity=0.8))

data = df_bar[df_bar["variable"] == "hosp_nonrea"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], text= data['value'], textposition='auto', name='Autre hospitalisation', marker_color='#FFA200', opacity=0.8))

if len(df_confirmed[df_confirmed["date"].isin([dates[-1]])]) > 0:
    data = df_confirmed[df_confirmed["date"].isin(dates)].reset_index()
    sum_df = df_bar[df_bar["variable"] == "dc"]['value'].reset_index() + df_bar[df_bar["variable"] == "rea"]['value'].reset_index() +  df_bar[df_bar["variable"] == "hosp_nonrea"]['value'].reset_index() + df_bar[df_bar["variable"] == "rad"]['value'].reset_index()
    fig.add_trace(go.Bar(x=data['date'], y=data['France'] - sum_df['value'], text = data['France'] - sum_df['value'], textposition='auto', name='Non hospitalisés', marker_color='grey', opacity=0.8))

data = df_bar[df_bar["variable"] == "rad"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], text= data['value'], textposition='auto', name='Retour à domicile', marker_color='green', opacity=0.8))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            barmode='stack',
            title={
                'text': "Évolution de la <b>situation des malades</b> du Covid-19",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = dict(
                size=20),
            xaxis=dict(
                title='',
                tickformat='%d/%m',
                nticks=len(dates)+5
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)

name_fig = "situation_cas"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[24]:


#df_region_sumj = df_region.groupby('regionName').sum().reset_index()
df_region_sumj = df_region[df_region['jour'] == dates[-1]]

df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[25]:


data = df_region_sumj[df_region_sumj["variable"] == "dc"]
fig = go.Figure(go.Bar(x=data['regionName'], y=data['value'], text=data['value'], textposition='auto', name='Décès', marker_color='#000000', opacity=0.8))

data = df_region_sumj[df_region_sumj["variable"] == "rea"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text=data['value'], textposition='auto', name='Réanimation', marker_color='#FF0000', opacity=0.8))

data = df_region_sumj[df_region_sumj["variable"] == "hosp_nonrea"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text= data['value'], textposition='auto', name='Autre hospitalisation', marker_color='#FFA200', opacity=0.8))

data = df_region_sumj[df_region_sumj["variable"] == "rad"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text= data['value'], textposition='auto', name='Retour à domicile', marker_color='green', opacity=0.8))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            barmode='stack',
            title={
                'text': "<b>Situation des malades hospitalisés</b> du Covid-19",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = dict(
                size=20),
            xaxis=dict(
                title='',
                tickformat='%d/%m',
                nticks=len(dates)+5
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    
                    showarrow = False
                )]
)
fig.update_xaxes(categoryorder="total descending")     

name_fig = "situation_cas_region"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[26]:


df_region_sumj = df_region[df_region['jour'] == dates[-1]]
df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad_pop', 'rea_pop', 'dc_pop', 'hosp_nonrea_pop'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[27]:


data = df_region_sumj[df_region_sumj["variable"] == "dc_pop"]
fig = go.Figure(go.Bar(x=data['regionName'], y=data['value'], text=round(data['value']), textposition='auto', name='Décès/100k hab.', marker_color='black', opacity=0.7))

data = df_region_sumj[df_region_sumj["variable"] == "rea_pop"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text=round(data['value']), textposition='auto', name='Réanimation/100k hab.', marker_color='red', opacity=0.7))

data = df_region_sumj[df_region_sumj["variable"] == "hosp_nonrea_pop"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text= round(data['value']), textposition='auto', name='Autre hospitalisation/100k hab.', marker_color='#FFA200', opacity=0.7))

data = df_region_sumj[df_region_sumj["variable"] == "rad_pop"]
fig.add_trace(go.Bar(x=data['regionName'], y=data['value'], text=round(data['value']), textposition='auto', name='Retour à dom./100k hab', marker_color='green', opacity=0.7))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            barmode='stack',
            title={
                'text': "<b>Situation des malades hospitalisés</b> du Covid-19 <b>par habitant</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont = dict(
                size=20),
            xaxis=dict(
                title='',
                tickformat='%d/%m',
                nticks=len(dates)+5
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.update_xaxes(categoryorder="total descending")        

name_fig = "situation_cas_region_hab"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[28]:



df_46 = pd.melt(df, id_vars=['jour'], value_vars=['dc_new', 'rad_new'])
df_46 = df.groupby(["jour"]).sum().reset_index()

fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_46["jour"],
    y = df_46["dc_new"],
    name = "Nouveaux décès",
    marker_color='black',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_46["jour"],
    y = df_46["rea_new"],
    name = "Admissions réanimation",
    marker_color='red',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_46["jour"],
    y = df_46["hosp_nonrea_new"],
    name = "Admi. autre hospitalisation",
    marker_color='grey',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_46["jour"],
    y = df_46["rad_new"],
    name = "Nouv. retours à domicile",
    marker_color='green',
    opacity=0.6
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='group',
    title={
                'text': "<b>COVID-19 : évolution quotidienne en France</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                size=20),
    xaxis=dict(
        title='',
        tickformat='%d/%m',
        nticks=100),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : @guillaumerozier (Twitter).'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "evol_journ"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1400, height=650)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# In[29]:


last_day = df['jour'].max()
df_bar = pd.melt(df, id_vars=['jour','regionName'], value_vars=['rea_pop', 'hosp_nonrea_pop'])
df_bar = df_bar[df_bar['jour']==last_day]
df_bar = df_bar.groupby(['regionName', 'variable']).sum().reset_index()

fig = px.bar(df_bar, x='regionName', y='value', color="variable").update_xaxes(categoryorder="total descending")

fig.update_layout(
    title_text='Nb. de <b>patients hospitalisés</b> et en <b>réanimation</b> par <b>habitant</b> ({})'.format(dates[-1]),
    title={
    'y':0.95,
    'x':0.5,
    'xanchor': 'center',
    'yanchor': 'top'}
),
titlefont = dict(
            size=40),
fig.data[-1].name = 'Réanimation'
fig.data[-2].name = 'Hospitalisation'
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients / 100k hab. de chaq. région")

name_fig = "hosp_rea_hab"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='Cliquez sur des éléments de légende pour les ajouter/supprimer',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
#fig.show()


# ## INSEE sur-mortalité

# In[30]:


dict_insee = pd.read_excel('data/france/deces_quotidiens_departement.xlsx', header=[3], index_col=None, sheet_name=None, usecols='A:H', nrows=31)
dict_insee.pop('France')
dict_insee.pop('Documentation')

for key in dict_insee:
    dict_insee[key]["dep"] = [key for i in range(len(dict_insee[key]))]


# In[31]:


df_insee = pd.concat(dict_insee)
df_insee = df_insee.rename(columns={"Total des décès (2)": "dc20", "Total des décès (2).1": "dc19", "Total des décès (2).2": "dc18", "Date d'événement": "jour"})
df_insee = df_insee.drop(columns=['Remontées dématérialisées (1) (*)', 'Remontées dématérialisées (1) (**)', 'Remontées dématérialisées (1) (*)', 'Remontées dématérialisées (1)', 'Taux de dématérialisation   (1)/(2)'])
df_insee["moy1819"] = (df_insee["dc19"] + df_insee["dc20"])/2
df_insee["surmortalite20"] = (df_insee["dc20"] - df_insee["moy1819"])/df_insee["moy1819"]*100
df_insee['jour'] = pd.to_datetime(df_insee['jour'])
df_insee['jour'] = df_insee['jour'].dt.strftime('%Y-%m-%d')


# In[32]:


df_insee["surmortalite20"]


# In[33]:


dates_insee = list(dict.fromkeys(list(df_insee.dropna()['jour'].values))) 

if build_gif_bool:
    imgs_folder = "images/charts/france/dep-map-surmortalite-img/{}.png"
    ppl = "surmortalite20"
    sub = 'Comparaison de la <b>mortalité journalière</b> entre 2020 <br>et les deux années précédentes.'
    map_gif(dates_insee, imgs_folder, df = df_insee.dropna(), type_ppl = ppl, legend_title="Sur-mortalité (%)", min_scale=-80, max_scale=80, colorscale = ["green", "white", "red"], subtitle = sub)
    build_gif(file_gif = "images/charts/france/dep-map-surmortalite.gif", imgs_folder = imgs_folder, dates=dates_insee)


# In[ ]:




