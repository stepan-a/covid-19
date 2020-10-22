#!/usr/bin/env python
# coding: utf-8

# In[20]:


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


# In[21]:


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


# In[22]:


# Import data from Santé publique France
_, _, _, _, _, _, _, df_incid, _ = data.import_data()
df_incid = df_incid[df_incid["cl_age90"] == 0]

with open('data/france/dep.geojson') as response:
    depa = json.load(response)


# In[23]:


def build_map(data_df, img_folder, date_val, date_str = "date", dep_str = "departement", color_str = 'indic_synthese', legend_title="legend_title", title="title", subtitle="", subsubtitle="{}<br>{} (données du {})", color_descrete_map={"Risque Faible":"#DAF7A6", "Alerte":"#b8002a", "Alerte Renforcée":"#7c0030", "Alerte Maximale":"#460d37"}):
    for date in date_val:
        data_df_temp = data_df[data_df[date_str] == date]
        
        if len(data_df_temp) > 0:
            fig = px.choropleth(geojson = depa, 
                                locations = data_df_temp[dep_str], 
                                featureidkey="properties.code",
                                color = data_df_temp[color_str],
                                scope='europe',
                                #labels={color_str:"Couleur"},
                                #color_discrete_sequence = ["green", "orange", "red"],
                                #labels={'red':"Couleur", 'orange':'bla', 'green':'lol'},
                                color_discrete_map = color_descrete_map
                                #color_discrete_map = ,
                                #category_orders = {color_str :["Risque Faible", "Alerte", "Alerte Renforcée", "Alerte Maximale"]}
                                      )
            date_title = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')
            date_now = datetime.now().strftime('%d %B')

            fig.update_geos(fitbounds="locations", visible=False)

            fig.update_layout(
                legend_title_text = "Couleur",
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
                        text= subsubtitle.format(subtitle, date_now, date_title),
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
                fig.write_image((img_folder+"/{}.jpeg").format("latest"), scale=2, width=960, height=640)
            fig.write_image((img_folder+"/{}.jpeg").format(date), scale=2, width=960, height=640)
        else:
            print("no data")


# In[24]:


def build_gif(file_gif, imgs_folder, dates):
    i=0
    with imageio.get_writer(file_gif, mode='I', duration=0.3) as writer: 
        for date in tqdm(dates):
            try:
                print((imgs_folder+"/{}.jpeg").format(date))
                image = imageio.imread((imgs_folder+"/{}.jpeg").format(date))
                writer.append_data(image)
                i+=1
                if (i==len(dates)-1) or (i==0):
                    for k in range(8):
                        writer.append_data(image)
            except:
                print("no image for "+str(date))


# In[25]:


dates_deconf = list(dict.fromkeys(list(df_incid["jour"].values)))

date = dates_deconf[-30:]
build_map(df_incid.sort_values(by=['incidence']), "images/charts/france/dep-map-incid-cat", date_val=date, date_str = "jour", dep_str = "dep", color_str = 'incidence_color', legend_title="", title="Incidence", subtitle="Nombre de cas hebdomadaires pour 100 000 habitants")


# In[26]:


df_incid #df_incid.loc[:,"color_couvre_feu"] = 
deps_couvre_feu = ["01", "05", "06", "07", "08", "09", "10", "12", "13", "14", "67", "2A", "2B", "21", "26", "30", "31", "34", "35", "37", "38", "39", "42", "43", "45", "48", "49", "51", "54", "59", "60","62", "63", "64", "65", "66","67", "69", "71", "73","74", "75", "76", "77", "78", "81", "82", "83", "84", "87", "91", "92", "93", "94", "95"]
df_incid.loc[:,"color_couvre_feu"] = ['Couvre-feu' if dep in deps_couvre_feu else 'Pas de couvre-feu' for dep in df_incid['dep']]

dates_deconf = list(dict.fromkeys(list(df_incid["jour"].values)))
date = [dates_deconf[-1]]
build_map(df_incid.sort_values(by=['incidence']), "images/charts/france/dep-map-couvre-feu", date_val=date, date_str = "jour", dep_str = "dep", color_str = 'color_couvre_feu', legend_title="", title="Départements possiblement en couvre feu samedi", subsubtitle="", color_descrete_map={"Pas de couvre-feu":"#a4bda8", "Couvre-feu":"#bd2828"})


# In[27]:


deps_strings=[]
for dep in deps_couvre_feu:
    deps_strings += [df_incid[df_incid["dep"] == dep]["departmentName"].values[0]]


# In[28]:


to_disp=""
for val in deps_strings:
    to_disp += val+", "
to_disp


# In[29]:


#df_incid.loc[df_incid["dep"] == "75"]["P"].rolling(window=7).sum()/df_incid.loc[df_incid["dep"] == "75"]["pop"]*100000


# In[30]:


build_gif("images/charts/france/incid-cat.gif", "images/charts/france/dep-map-incid-cat", dates_deconf[-30:])

