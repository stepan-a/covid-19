#!/usr/bin/env python
# coding: utf-8

# In[4]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

README:s
This file contains script that generate France maps and GIFs. 
Single images are exported to folders in 'charts/image/france'. GIFs are exported to 'charts/image/france'.
I'm currently cleaning this file, please ask me is something is not clear enough!
Requirements: please see the imports below (use pip3 to install them).

"""


# In[5]:


import france_data_management as data
import pandas as pd
from tqdm import tqdm
import json
import plotly.express as px
from datetime import datetime
import imageio
import multiprocessing
import locale
import shutil
import os
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[9]:


# Import data from Santé publique France
_, _, _, _, _, _, _, df_incid, _ = data.import_data()
with open('data/france/dep.geojson') as response:
    depa = json.load(response)


# In[10]:


def build_map(data_df, img_folder, date_str = "date", dep_str = "departement", color_str = 'indic_synthese', legend_title="legend_title", title="title", subtitle=""):
    dates_deconf = list(dict.fromkeys(list(data_df[date_str].values)))
    date = dates_deconf[-1]
    data_df = data_df[data_df[date_str] == date]

    fig = px.choropleth(geojson = depa, 
                        locations = data_df[dep_str], 
                        featureidkey="properties.code",
                        color = data_df[color_str],
                        scope='europe',
                        labels={color_str:"Couleur"},
                        #color_discrete_sequence = ["green", "orange", "red"],
                        #labels={'red':"Couleur", 'orange':'bla', 'green':'lol'},
                        color_discrete_map = {"Vert (<25)":"green", "Orange (25-50)":"orange", "Rouge (>50)":"red"}
                        #category_orders = {"indic_synthese" :["vert", "orange", "rouge"]}
                              )
    date_title = datetime.strptime(dates_deconf[-1], '%Y-%m-%d').strftime('%d %B')
    date_now = datetime.now().strftime('%d %B')
    
    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        title={
            'text': title,
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},

        titlefont = dict(
            size=30),

        annotations = [
            dict(
                x=0.54,
                y=0.03,
                xref='paper',
                yref='paper',
                xanchor = 'center',
                text='Source : Santé publique France. Auteur : @guillaumerozier.',
                showarrow = False
            ),

            dict(
                x=0.55,
                y=0.94,
                xref='paper',
                yref='paper',
                text= "{}<br>{} (données du {})".format(subtitle, date_now, date_title),
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
    #fig.show()
    if date == dates_deconf[-1]:
        fig.write_image((img_folder+"/{}.jpeg").format("latest"), scale=2, width=1200, height=800)
    fig.write_image((img_folder+"/{}.jpeg").format(date), scale=2, width=1200, height=800)


# In[11]:


build_map(df_incid, "images/charts/france/dep-map-incid-cat", date_str = "jour", dep_str = "dep", color_str = 'incidence_color', legend_title="", title="Incidence", subtitle="Nombre de cas hebdomadaires pour 100 000 habitants")

