#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


from multiprocessing import Pool
import requests
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
from datetime import datetime
from datetime import timedelta
from tqdm import tqdm
import imageio
import json
import locale
import france_data_management as data
import numpy as np
import plotly.figure_factory as ff

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()


# In[ ]:


df_metro = data.import_data_metropoles()


# In[ ]:


metros = list(dict.fromkeys(list(df_metro['Metropole'].values))) 

for (name, data, title, scale_txt, data_example, digits) in [("cas", '', "Taux d'<br>incidence", " cas", " cas", 1)]:
    
    array_incidence=np.array([])
    for idx, metro in enumerate(metros): #deps_tests.drop("975", "976", "977", "978")
        array_incidence += [metros[metros["Metropole"] == metro].values]
        
        
    fig = ff.create_annotated_heatmap(
        z=array_incidence, #df_tests_rolling[data].to_numpy()
        x=dates_heatmap,
        y=[str(x-9) + " à " + str(x)+" ans" if x!=99 else "+ 90 ans" for x in range(9, 109, 10)],
        showscale=True,
        font_colors=["white", "white"],
        coloraxis="coloraxis",
        #text=df_tests_rolling[data],
        annotation_text = array_incidence
        )

    annot = []

    fig.update_xaxes(side="bottom", tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))

    fig.update_layout(
        title={
            'text': "{} du Covid19 en fonction de l\'âge".format(title.replace("<br>", " ")),
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=20),
        coloraxis=dict(
            cmin=0, cmax=300,
            colorscale = [[0, "green"], [0.2, "#ffcc66"], [0.8, "#f50000"], [1, "#b30000"]],
            #color_continuous_scale=["green", "red"],
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=12,
                lenmode="pixels", len=300,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(scale_txt),
                )
        ),
    margin=dict(
                    b=80,
                    t=40,
                    pad=0
                ))

    annotations = annot + [
                    dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        opacity=0.6,
                        font=dict(color="white", size=55),
                        text="Dép. <b>{}</b>".format(dep),
                        showarrow=False
                    ),
                    dict(
                        x=0.5,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=12),
                        text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à gauche) et à une date donnée (à lire en bas).<br>Du orange correspond à un {} élevé.  <i>Date : {} - Source : covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ]

    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 12
        fig.layout.annotations[i].text = "<b>"+fig.layout.annotations[i].text+"</b>"

    for annot in annotations:
        fig.add_annotation(annot)

    name_fig = "heatmaps_metropoles/heatmap_"+"taux"+"_"+dep
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=550)
    fig.write_image("images/charts/france/{}_SD.jpeg".format(name_fig), scale=0.5, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

