#!/usr/bin/env python
# coding: utf-8

# # COVID-19 French Charts
# Guillaume Rozier, 2020

# In[1]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.covidtracker.fr
Mail : guillaume.rozier@telecomnancy.net

README:
This file contains scripts that download data from data.gouv.fr and then process it to build many graphes.
I'm currently cleaning the code, please ask me if something is not clear enough.

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
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

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet
show_charts = False
now = datetime.now()


# # Data download and import

# In[3]:


data.download_data()


# ## Data transformations

# In[4]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()

df_incid_france = df_incid.groupby("jour").sum().reset_index()

df_sursaud_france = df_sursaud.groupby(['date_de_passage']).sum().reset_index()
df_sursaud_france["taux_covid"] = df_sursaud_france["nbre_pass_corona"] / df_sursaud_france["nbre_pass_tot"]
df_sursaud_france["taux_covid_acte"] = df_sursaud_france["nbre_acte_corona"] / df_sursaud_france["nbre_acte_tot"]
dates_sursaud = list(dict.fromkeys(list(df_sursaud['date_de_passage'].values))) 

dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
departements = list(dict.fromkeys(list(df_incid['dep'].values))) 

last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")

df_region = df.groupby(['regionName', 'jour', 'regionPopulation']).sum().reset_index()
df_region["hosp_regpop"] = df_region["hosp"] / df_region["regionPopulation"]*1000000 
df_region["rea_regpop"] = df_region["rea"] / df_region["regionPopulation"]*1000000 

df_tests_tot = df_tests.groupby(['jour']).sum().reset_index()

df_new_region = df_new.groupby(['regionName', 'jour']).sum().reset_index()
df_france = df.groupby('jour').sum().reset_index()

regions = list(dict.fromkeys(list(df['regionName'].values))) 


# In[5]:


#Calcul sorties de réa
# Dataframe intermédiaire (décalée d'une ligne pour le calcul)
df_new_tot = df_new.groupby(["jour"]).sum().reset_index()
last_row = df_new_tot.iloc[-1]
df_new_tot = df_new_tot.shift()
df_new_tot = df_new_tot.append(last_row, ignore_index=True)

# Nouvelle dataframe contenant le résultat
df_new_tot["incid_dep_rea"] = df_france["rea"] - df_france["rea"].shift() - df_new_tot["incid_rea"]
df_new_tot["incid_dep_hosp_nonrea"] = df_france["hosp_nonrea"] - df_france["hosp_nonrea"].shift() - df_new_tot["incid_hosp_nonrea"]

# On ne garde que les 19 derniers jours (rien d'intéressant avant)
df_new_tot_last15 = df_new_tot[ df_new_tot["jour"].isin(dates[:]) ]
df_france_last15 = df_france[ df_france["jour"].isin(dates[-19:]) ]
df_tests_tot_last15 = df_tests_tot[ df_tests_tot["jour"].isin(dates[-19:]) ]


# # Graphes: bar charts

# ## Variation journée

# In[6]:


fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["dc_new"],
    name = "Nouveaux décès hosp.",
    marker_color='black',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["rea_new"],
    name = "<b>Variation</b> des réanimations",
    marker_color='red',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["hosp_nonrea_new"],
    name = "<b>Variation</b> des hosp. (hors réa.)",
    marker_color='grey',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_france_last15["jour"],
    y = df_france_last15["rad_new"],
    name = "Nouv. retours à domicile",
    marker_color='green',
    opacity=0.6
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(

    barmode='group',
    title={
                'text': "<b>COVID-19 : variation quotidienne en France</b>",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "var_journ"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1400, height=800)

fig.update_layout(

    legend_orientation="h",
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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Var jour lines

# In[7]:



for (range_x, name_fig) in [(["2020-03-22", last_day_plot], "var_journ_lines"), (["2020-06-10", last_day_plot], "var_journ_lines_recent")]:
    #fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    dc_new_rolling = df_france["dc_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=4,
        opacity=0.8
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["dc_new"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.3,
        showlegend=False
    ))

    ###
    rea_new_rolling = df_france["rea_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = rea_new_rolling,
        name = "<b>Variation</b> des réanimations",
        marker_color='red',
        line_width=4,
        opacity=0.8
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [rea_new_rolling.values[-1]],
        name = "<b>Variation</b> des réanimations",
        marker_color='red',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    #

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["rea_new"],
        name = "<b>Variation</b> des réanimations",
        mode="markers",
        marker_color='red',
        line_width=3,
        opacity=0.3,
        showlegend=False
    ))

    ##
    hosp_non_rea_rolling = df_france["hosp_nonrea_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = hosp_non_rea_rolling,
        name = "<b>Variation</b> des hosp. (hors réa.)",
        marker_color='grey',
        fillcolor='rgba(219, 219, 219, 0.5)',
        line_width=4,
        opacity=0.8,
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [hosp_non_rea_rolling.values[-1]],
        name = "<b>Variation</b> des ",
        marker_color='grey',
        fillcolor='rgba(219, 219, 219, 0.5)',
        marker_size=15,
        mode="markers",
        opacity=1,
        showlegend=False
    ))


    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["hosp_nonrea_new"],
        name = "<b>Variation</b> des tests positifs",
        mode="markers",
        marker_color='grey',
        opacity=0.3,
        showlegend=False
    ))
    
    ###
    incid_rolling = df_incid_france['P'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_incid_france["jour"],
        y = incid_rolling,
        name = "<b>Variation</b> des tests positifs",
        marker_color='blue',
        line_width=4,
        opacity=0.8
    ), secondary_y=True)
    
    fig.add_trace(go.Scatter(
        x = [df_incid_france['jour'].max()],
        y = [incid_rolling.values[-1]],
        name = "<b>Variation</b> des tests positifs",
        marker_color='blue',
        fillcolor='rgba(219, 219, 219, 0.5)',
        marker_size=15,
        mode="markers",
        opacity=1,
        showlegend=False
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x = df_incid_france['jour'],
        y = df_incid_france['P'],
        name = "<b>Variation</b> des tests positifs",
        mode="markers",
        marker_color='blue',
        opacity=0.3,
        showlegend=False
    ), secondary_y=True)

    ###
    rad_new_rolling=df_france["rad_new"].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = rad_new_rolling,
        name = "Nouv. retours à domicile",
        marker_color='green',
        fillcolor='rgba(114, 171, 108, 0.3)',
        line_width=4,
        opacity=0.8,
    ))

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [rad_new_rolling.values[-1]],
        name = "Nouv. retours à domicile",
        marker_color='green',
        fillcolor='rgba(114, 171, 108, 0.3)',
        marker_size=15,
        mode="markers",
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["rad_new"],
        name = "Nouv. retours à domicile",
        mode="markers",
        marker_color='green',
        line_width=2,
        opacity=0.3,
        showlegend=False
    ))

    fig.update_yaxes(zeroline=True, range=[df_france["hosp_nonrea_new"].min(), df_france['rad_new'].max()], zerolinewidth=2, zerolinecolor='Grey', secondary_y=False)
    fig.update_yaxes(zeroline=True, range=[df_france["hosp_nonrea_new"].min(), df_incid_france['P'].max()], zerolinewidth=2, zerolinecolor='Grey', secondary_y=True)
    fig.update_xaxes(range=range_x, nticks=30, ticks='inside', tickangle=0)

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=20,
                r=190,
                b=100,
                t=100,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': "<b>COVID-19 : variation quotidienne en France</b>, moyenne mobile centrée de 7 jours",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
            title='',
            tickformat='%d/%m'),
        yaxis_title="Nb. de personnes",

        annotations = [
                    dict(
                        x=0,
                        y=1.05,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )
    for (data_temp, type_ppl, col, ys, ay, date, yref) in [(dc_new_rolling, "décès", "black", 3, -10, dates[-1], 'y1'), (incid_rolling, "tests positifs", "blue", 8, -25, df_incid_france['jour'].max(), 'y2'), (rea_new_rolling, "réanimations", "red", -3, 10, dates[-1], 'y1'), (hosp_non_rea_rolling, "hospitalisations<br> &#8205; (hors réa.)", "grey", -10, 30, dates[-1], 'y1'), (rad_new_rolling, "retours à<br> &#8205; domicile", "green", 10, -30, dates[-1], 'y1')]:
        fig['layout']['annotations'] += (dict(
                x=date, y = data_temp.values[-1], # annotation point
                xref='x1', 
                yref=yref,
                text=" <b>{}</b> {}".format('%+d' % math.trunc(round(data_temp.values[-1], 2)), type_ppl),
                xshift=15,
                yshift=ys,
                xanchor="left",
                align='left',
                font=dict(
                    color=col,
                    size=15
                    ),
                opacity=0.8,
                ax=30,
                ay=ay,
            arrowcolor=col,
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=4,
                showarrow=True
            ),)

    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1300, height=850)

    fig.update_layout(

        legend_orientation="h"
                     )
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# ## Evolution jorunée

# In[8]:


#EVOL JOURN
fig = make_subplots(specs=[[{"secondary_y": True}]])
#fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dc"],
    name = "Nouveaux décès hosp.",
    marker_color='black',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rea"],
    name = "<b>Admissions</b> réanimations",
    marker_color='red',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_hosp_nonrea"],
    name = "<b>Admissions</b> autres hospit.",
    marker_color='grey',
    opacity=0.6
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rad"],
    name = "Nouv. retours à domicile",
    marker_color='green',
    opacity=0.6
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    legend_orientation="h",
    margin=dict(
            l=0,
            r=0,
            b=0,
            t=80,
            pad=0
        ),
    #paper_bgcolor='#fffbed',#fcf8ed #faf9ed
    #plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "evol_journ"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=1600, height=800)

fig.update_layout(
    legend_orientation="h",
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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Tests Covid

# In[9]:


# TESTS

fig = make_subplots(specs=[[{"secondary_y": True}]])
#fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_tests_tot["jour"],
    y = df_tests_tot["nb_pos"].rolling(window=4, center=True).mean(),
    name = "Tests positifs",
    marker_color='red',
    opacity=0.6
), secondary_y=False)

fig.add_trace(go.Bar(
    x = df_tests_tot["jour"],
    y = df_tests_tot["nb_test"].rolling(window=4, center=True).mean(),
    name = "Tests négatifs",
    marker_color='green',
    opacity=0.6
), secondary_y=False)


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='stack',
    #paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    #plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
    title={
                'text': "<b>COVID-19 : tests en laboratoire de ville</b>",
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
    yaxis_title="Nb. de personnes testées",
    
    annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "tests_journ"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1400, height=800)

fig.update_layout(
    legend_orientation="h",
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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Entrées/Sortires hosp et réa

# In[10]:


fig = go.Figure()
#fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rea"],
    name = "Admissions réanimation",
    marker_color='red',
    opacity=0.8
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_hosp_nonrea"],
    name = "Admissions hospitalisation (hors réa.)",
    marker_color='red',
    opacity=0.5
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dep_rea"],
    name = "Sorties réanimation",
    marker_color='green',
    opacity=0.8
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dep_hosp_nonrea"],
    name = "Sorties hospitalisation (hors réa.)",
    marker_color='green',
    opacity=0.5
))

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = df_france["rea_new"],
    name = "Solde quotidien réanimation",
    marker_color='black',
    mode="lines+markers",
    opacity=0.8
))

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = df_france["hosp_nonrea_new"],
    name = "Solde quotidien hosp. (hors réa.)",
    marker_color='black',
    mode="lines+markers",
    opacity=0.4
))


# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    legend_orientation="v",
    barmode='relative',
    title={
                'text': "<b>COVID-19 : entrées et sorties en hospitalisation</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),
        
    xaxis=dict(
        range=["2020-03-20", (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")  ], # Adding one day
        title='',
        tickformat='%d/%m'),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0.6,
                    y=1.08,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='',
                    font=dict(size=17),
                    showarrow = False),
            
                dict(
                    x=0,
                    y=1.04,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),           
                    showarrow = False)
                ]
                )

name_fig = "entrees_sorties_hosp_rea"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1200, height=800)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Entrées/Sorties hosp et réa - rolling mean (7 days)
# La moyenne glissante sur 4 jours permet de lisser les effets liés aux week-ends (moins de saisies de données, donc il y a un trou) et d'évaluer la tendance.

# In[11]:


for (rge_x, rge_y, suffix) in [(["2020-03-21", last_day_plot], [-2500, 3700], ""), (["2020-06-10", last_day_plot], [-1000, 1000], "_recent")]:
    fig = go.Figure()
    #fig = make_subplots(specs=[[{"secondary_y": True}]])
    incid_rea = df_new_tot_last15["incid_rea"].rolling(window=7, center=True).mean()
    fig.add_trace(go.Bar(
        x = df_new_tot_last15["jour"],
        y = incid_rea,
        name = "Admissions réanimation",
        marker_color='red',
        opacity=0.8
    ))
    incid_hosp_nonrea = df_new_tot_last15["incid_hosp_nonrea"].rolling(window=7, center=True).mean()
    fig.add_trace(go.Bar(
        x = df_new_tot_last15["jour"],
        y = incid_hosp_nonrea,
        name = "Admissions hospitalisation (hors réa.)",
        marker_color='red',
        opacity=0.5
    ))

    incid_dep_rea = -df_new_tot_last15["incid_dep_rea"].rolling(window=7, center=True).mean().abs()
    fig.add_trace(go.Bar(
        x = df_new_tot_last15["jour"],
        y = incid_dep_rea,
        name = "Sorties réanimation",
        marker_color='green',
        opacity=0.8
    ))

    incid_dep_hosp_nonrea = -df_new_tot_last15["incid_dep_hosp_nonrea"].rolling(window=7, center=True).mean().abs()
    fig.add_trace(go.Bar(
        x = df_new_tot_last15["jour"],
        y = incid_dep_hosp_nonrea,
        name = "Sorties hospitalisation (hors réa.)",
        marker_color='green',
        opacity=0.5
    ))

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["rea_new"].rolling(window=7, center=True).mean(),
        name = "Solde réanimation",
        marker_color='black',
        mode="lines+markers",
        opacity=0.8
    ))

    fig.add_trace(go.Scatter(
        x = df_france["jour"],
        y = df_france["hosp_nonrea_new"].rolling(window=7, center=True).mean(),
        name = "Solde hosp. (hors réa.)",
        marker_color='black',
        mode="lines+markers",
        opacity=0.4
    ))

    fig.update_layout(
        legend_orientation="h",
        margin=dict(
                l=20,
                r=200,
                b=100,
                t=100,
                pad=0
            ),
        barmode='relative',
        title={
                    'text': "<b>COVID-19 : entrées et sorties en hospitalisation</b>",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'middle'},
                    titlefont = dict(
                    size=20),

        xaxis=dict(
            range=rge_x, # Adding one day
            title='',
            tickformat='%d/%m'),
        yaxis=dict(title="Nb. de personnes",
                   range=rge_y
                  ),

        annotations = [
                    dict(
                        x=0.6,
                        y=1.08,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        text='moyenne mobile centrée sur 7 jours',
                        font=dict(size=17),
                        showarrow = False),

                    dict(
                        x=0,
                        y=1.04,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France et CSSE. Auteur : GRZ - covidtracker.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),           
                        showarrow = False)
                    ]
                    )

    fig['layout']['annotations'] += (dict(
                x=dates[-4], y = incid_rea.values[-4], # annotation point
                xref='x1', 
                yref='y1',
                text=" <b> {}</b> {}".format(math.trunc(round(incid_rea.values[-4], 1)), "admissions en<br> &#8205;  réanimation"),
                xshift=10,
                xanchor="left",
                align='left',
                font=dict(
                    color="rgba(255,0,0,1)",
                    size=14
                    ),
                opacity=1,
                ax=70,
                ay=-20,
                arrowcolor="rgba(255,0,0,1)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=4,
                showarrow=True
            ),)
    fig['layout']['annotations'] += (dict(
                x=dates[-4], y = incid_hosp_nonrea.values[-4], # annotation point
                xref='x1', 
                yref='y1',
                text=" <b> {}</b> {}".format(math.trunc(round(incid_hosp_nonrea.values[-4], 1)), "admissions en<br> &#8205; autre hospitalisation"),
                xshift=10,
                xanchor="left",
                align='left',
                font=dict(
                    color="rgba(255,0,0,0.6)",
                    size=14
                    ),
                ax=70,
                ay=-50,
                arrowcolor="rgba(255,0,0,0.6)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=4,
                showarrow=True
            ),)
    fig['layout']['annotations'] += (dict(
                x=dates[-4], y = incid_dep_rea.values[-4], # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{}</b> {}".format(math.trunc(round(incid_dep_rea.values[-4], 1)), "sorties en<br> &#8205;  réanimation"),
                xshift=10,
                xanchor="left",
                align='left',
                font=dict(
                    color="green",
                    size=14
                    ),
                opacity=1,
                ax=70,
                ay=20,
                arrowcolor="green",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=4,
                showarrow=True
            ),)
    fig['layout']['annotations'] += (dict(
                x=dates[-4], y = incid_dep_hosp_nonrea.values[-4], # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{}</b> {}".format(math.trunc(round(incid_dep_hosp_nonrea.values[-4], 1)), "sorties en<br> &#8205; autre hospitalisation"),
                xshift=10,
                xanchor="left",
                align='left',
                font=dict(
                    color="rgba(0,128,0,0.6)",
                    size=14
                    ),
                ax=70,
                ay=50,
                arrowcolor="rgba(0,128,0,0.6)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=4,
                showarrow=True
            ),)

    name_fig = "entrees_sorties_hosp_rea_ROLLING{}".format(suffix)
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1200, height=800)

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
    print("> " + name_fig)
    if show_charts:
        fig.show()


# ## Hospitalisations (bar chart)

# In[12]:


"""fig = go.Figure()

fig = px.bar(df_france, x='jour', y='hosp',
             color='hosp_new',
             labels={'hosp_new':'Solde hospitalisations'}, color_continuous_scale=["green", "#ffc832", "#cf0000"], range_color=(-2500, 2500))



# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    barmode='group',
    bargap=0,
    yaxis=dict(
        range=[0, 45000]),
    title={
                'text': "COVID19 : <b>nombre de personnes hospitalisées</b>",
                'y':0.97,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                titlefont = dict(
                    family="Roboto",
                    size=30),
    xaxis=dict(
        range=["2020-03-15", "2020-04-25"],
        title='',
        tickformat='%d/%m',
        nticks=50
    ),
    yaxis_title="Nb. de personnes",
    
    annotations = [
                dict(
                    x=0.01,
                    y=0.99,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "hosp_bar"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1400, height=800)

fig.update_layout(
    legend_orientation="h",
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
print("> " + name_fig)

if show_charts:
    fig.show()"""


# ## Hospitalisations et réanimations (bar charts subplot)

# In[13]:


fig = make_subplots(rows=2, cols=1, shared_yaxes=True, subplot_titles=["Nombre de personnes<b> hospitalisées</b>", "Nombre de personnes en <b>réanimation</b>"], vertical_spacing = 0.15, horizontal_spacing = 0.1)

fig1 = px.bar(x=df_france['jour'], y=df_france['hosp'],
             color=df_france['hosp_new'], color_continuous_scale=["green", "#ffc832", "#cf0000"], range_color=(df_france['hosp_new'].min(), df_france['hosp_new'].max())
            )
fig2 = px.bar(x=df_france['jour'], y=df_france['rea'],
             color=df_france['rea_new'], color_continuous_scale=["green", "#ffc832", "#cf0000"], range_color=(-2500, 2500)
            )
trace1 = fig1['data'][0]
trace2 = fig2['data'][0]

"""fig.add_trace(trace1, row=1, col=1)
fig.add_trace(trace2, row=2, col=1)"""

fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['hosp'],
                    marker=dict(color =df_france['hosp_new'], coloraxis="coloraxis1"), ),
              1, 1)
fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['rea'],
                    marker=dict(color =df_france['rea_new'], coloraxis="coloraxis2"), ),
              2, 1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=1, col=1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=2, col=1)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=25)

fig.update_layout(
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    bargap=0,
    coloraxis1=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['hosp_new'].max(), cmax=df_france['hosp_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. hospitalisées<br> &#8205; ",
                        thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.79, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))),
    coloraxis2=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['rea_new'].max(), cmax=df_france['rea_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. en réanimation<br> &#8205; ",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.22, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))), 


                showlegend=False,

)

fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='covidtracker.fr - {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

name_fig = "hosp_rea_bar"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=1200)

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
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# ## Indicateur 1 - France

# In[14]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

df_sursaud_france['taux_covid_rolling'] = df_sursaud_france['taux_covid'].rolling(window=7, center=True).mean()
df_sursaud_france['taux_covid_acte_rolling'] = df_sursaud_france['taux_covid_acte'].rolling(window=7, center=True).mean()

fig = make_subplots(rows=2, cols=1, shared_yaxes=True, subplot_titles=["Circulation du Coronavirus<br><sub><b>Taux d'admission aux urgences pour Covid19</b></sub>", "<sub><b>Taux d'actes SOS Médecin pour Covid19</b></sub>"], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}], [{"secondary_y": True}]])

fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_pass_corona'], opacity=0.2, marker_color='red', name = "nombre d'admissions aux urgences • d'actes SOS Médecin <b>pour Covid</b>"),
              1, 1, secondary_y=True)

fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_pass_tot']-df_sursaud_france['nbre_pass_corona'], opacity=0.3, marker_color='grey', name = "<b>nombre total</b> d'admissions aux urgences • d'actes SOS Médecin "),
              1, 1, secondary_y=True)

fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid_rolling'], marker_color='red', line_width=5, name = "<b>taux</b> d'admissions aux urgences • d'actes SOS Médecin <b>pour Covid</b>"),
              1, 1)
fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid'], mode="markers", marker_color='red', marker_size=4, line_width=5, showlegend=False),
              1, 1)
fig.add_trace(go.Scatter(x = [dates_sursaud[-4]], y = 100*df_sursaud_france.loc[df_sursaud_france["date_de_passage"] == dates_sursaud[-4], 'taux_covid_rolling'], marker_color='red', name = "taux d'actes SOS Médecin pour Covid", mode="markers", marker_size=20,showlegend=False),
              1, 1)

##
fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_acte_corona'], opacity=0.2, marker_color='red', name = "", showlegend=False),
              2, 1, secondary_y=True)

fig.add_trace(go.Bar(x = df_sursaud_france['date_de_passage'], y = df_sursaud_france['nbre_acte_tot']-df_sursaud_france['nbre_acte_corona'], opacity=0.3, marker_color='grey', name = "", showlegend=False),
              2, 1, secondary_y=True)

fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid_acte_rolling'], marker_color='red', line_width=5, name = "taux d'actes SOS Médecin pour Covid", showlegend=False),
              2, 1)
fig.add_trace(go.Scatter(x = df_sursaud_france['date_de_passage'], y = 100*df_sursaud_france['taux_covid_acte'], mode="markers", marker_color='red', marker_size=4, line_width=5, showlegend=False),
              2, 1)
fig.add_trace(go.Scatter(x = [dates_sursaud[-4]], y = 100*df_sursaud_france.loc[df_sursaud_france["date_de_passage"] == dates_sursaud[-4], 'taux_covid_acte_rolling'], marker_color='red', name = "taux d'actes SOS Médecin pour Covid", mode="markers", marker_size=20,showlegend=False),
              2, 1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', range=[0, 28], linewidth=1, linecolor='white', row=1, col=1, secondary_y=False)
fig.update_yaxes(range=[0, 6], row=1, col=1, secondary_y=True, type="log")

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
fig.update_yaxes(title_text="", gridcolor='white', range=[0, 30], linewidth=1, linecolor='white', row=2, col=1, secondary_y=False)
fig.update_yaxes(range=[0, 5], row=2, col=1, secondary_y=True, type="log")

for i in fig['layout']['annotations']:
    i['font'] = dict(size=30)
    
y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','taux_covid_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = y_val, # annotation point
        xref='x1', 
        yref='y1',
        text="   {} % des admissions au urgences<br>   ont concerné le Covid19 le 28 mars".format(round(y_val, 1)),
        xshift=5,
        yshift=5,
        xanchor="left",
        align='left',
        font=dict(
            color="red",
            size=14,
            ),
        ax=0,
        ay=-60,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']==dates_sursaud[-4],'taux_covid_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x=dates_sursaud[-4], y = y_val, # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{}</b> %".format(round(y_val, 1)),
        xshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16,
            ),
        ax=0,
        ay=-25,
        arrowcolor="red",
        opacity=0.8,
        arrowsize=0.3,
        arrowwidth=0.1,
        arrowhead=0
    ),)

y_val = df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','nbre_pass_tot'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = math.log10(y_val), # annotation point
        xref='x1', 
        yref='y2',
        text="   Il y a eu {} admissions aux urgences<br>   le {} ".format('{:n}'.format(math.trunc(round(y_val, 1))).replace(',', ' '), '28 mars'),
        xshift=0,
        xanchor="left",
        align='left',
        font=dict(
            color="grey",
            size=14
            ),
        ax=250,
        ay=-30,
        arrowcolor="grey",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

###
y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','taux_covid_acte_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = y_val, # annotation point
        xref='x2', 
        yref='y3',
        text="   {} % des actes SOS Médecin<br>   ont concerné le Covid19 le 28 mars".format(round(y_val, 1)),
        xshift=10,
        yshift=10,
        align='left',
        xanchor="left",
        font=dict(
            color="red",
            size=14
            ),
        ax=80,
        ay=-50,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

y_val = 100*df_sursaud_france.loc[df_sursaud_france['date_de_passage']==dates_sursaud[-4],'taux_covid_acte_rolling'].values[0]
fig['layout']['annotations'] += (dict(
        x=dates_sursaud[-4], y = (y_val), # annotation point
        xref='x2', 
        yref='y3',
        text="<b>{}</b> %".format(round(y_val, 1)),
        xshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16
            ),
        opacity=0.8,
        ax=0,
        ay=-25,
        arrowcolor="red",
        arrowsize=0.3,
        arrowwidth=0.1,
        arrowhead=0
    ),)

y_val = df_sursaud_france.loc[df_sursaud_france['date_de_passage']=='2020-03-28','nbre_acte_tot'].values[0]
fig['layout']['annotations'] += (dict(
        x='2020-03-28', y = math.log10(y_val), # annotation point
        xref='x2', 
        yref='y4',
        text="   Il y a eu {} actes SOS Médecin <br>   le {} ".format('{:n}'.format(math.trunc(round(y_val, 1))).replace(',', ' '), '28 mars'),
        xshift=0,
        align='left',
        xanchor="left",
        font=dict(
            color="grey",
            size=14
            ),
        ax = 100,
        ay = -10,
        arrowcolor="grey",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

fig.update_layout(
    barmode='stack',
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=90,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)
commentaire = "Les points rouges représentent les données brutes quotidiennes. Les lignes rouges sont obtenues en effectuant la moyenne mobile<br>centrée, sur 7 jours. Source : Santé publique France. Auteur : GRZ - <i>covidtracker.fr - {}</i>".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y'))
fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=-0.05,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text="",
                        #text='guillaumerozier.fr - {}'.format(datetime.strptime(max(dates_sursaud), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.01,
                        y=-0.05,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        align="left",
                        text=commentaire,
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

fig.add_layout_image(
        dict(
            source="data/covidtracker_logo.jpeg",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=20, sizey=20,
            xanchor="right", yanchor="bottom"
            )
)

name_fig = "indic1_france"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=1400)

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


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

#locale.setlocale(locale.LC_ALL, '')
#fig.show()


# In[15]:


"""
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

incid_rolling = (df_incid_france['p']).rolling(window=7, center=True).mean()
tests_tot_rolling = (df_incid_france['t']).rolling(window=7, center=True).mean()

#fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = incid_rolling, marker_color='red', line_width=5, name = "Nombre de tests positifs", showlegend=True), secondary_y=True
             )

fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = df_incid_france['p'], mode="markers", marker_color='red', marker_size=4, line_width=5, showlegend=False), secondary_y=True
              )
fig.add_trace(go.Scatter(x = [dates_incid[-4]], y = [incid_rolling.values[-4]], marker_color='red', name = "", mode="markers", marker_size=20, showlegend=False), secondary_y=True
             )
fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = tests_tot_rolling, name = "Nombre de tests réalisés", showlegend=True, marker_opacity=0, marker_color='grey', fill='tonexty', fillcolor='rgba(186, 186, 186, 0.4)'), secondary_y=False
             )

fig.update_xaxes(title_text="", gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white')
fig.update_yaxes(title_text="Nombre de tests positifs", range = [0, 1000], gridcolor='white', linewidth=1, linecolor='white', secondary_y=True)
fig.update_yaxes(title_text="Nombre de tests réalisés", range = [0, 40000], linewidth=0, showgrid=False, secondary_y=False)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=30)

fig['layout']['annotations'] += (dict(
        x=dates_incid[-4], y = incid_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y2',
        text="<b>{} personnes sont positives</b> chaque jour<br>en moyenne du {} au {}".format(math.trunc(round(incid_rolling.values[-4], 0)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=20,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16,
            ),
        ax=0,
        ay=-50,
        arrowcolor="red",
        opacity=0.7,
        arrowsize=2,
        arrowwidth=1,
        arrowhead=4
    ),
        dict(
        x=dates_incid[-4], y = tests_tot_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} tests</b> sont réalisés chaque jour<br>en moyenne du {} au {}".format(math.trunc(round(tests_tot_rolling.values[-4], 0)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="black",
            size=16,
            ),
        ax=0,
        ay=-50,
        arrowcolor="black",
        opacity=0.7,
        arrowsize=2,
        arrowwidth=1,
        arrowhead=6
    ))


fig.update_layout(
    title={
                'text': "Covid-19 : <b>nombre de tests positifs au Covid19</b></b><br><sub>par jour ; tests virologiques uniquement ; moyenne mobile sur 7 j. ; données Santé publique France</sub>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    
    
    margin=dict(
        l=0,
        r=40,
        b=150,
        t=90,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)
commentaire = "Les points rouges représentent les données brutes quotidiennes. Les lignes rouges sont obtenues en effectuant la moyenne mobile<br>centrée, sur 7 jours. <i>Guillaume Rozier pour covidtracker.fr - {}</i>".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y'))
fig["layout"]["annotations"] += (
                    dict(
                        x=0,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        align="left",
                        text=commentaire,
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

fig.add_layout_image(
        dict(
            source="data/covidtracker_logo.jpeg",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=20, sizey=20,
            xanchor="right", yanchor="bottom"
            )
) 

name_fig = "incidence_france"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=900)

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


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

locale.setlocale(locale.LC_ALL, '')
#fig.show()"""


# ## Tests France

# In[16]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

incid_rolling = (df_incid_france['P']).rolling(window=7, center=False).mean()
tests_tot_rolling = (df_incid_france['T']).rolling(window=7, center=False).mean()
taux = (df_incid_france['P']/df_incid_france['T']*100).rolling(window=7, center=False).mean()

if taux.dropna().values[-1] > 5:
    clr = "red"
elif taux.dropna().values[-1] > 1:
    clr = "darkorange"
else:
    clr = "green"

#fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Bar(x = df_incid_france["jour"], y = incid_rolling, marker_color='rgba(252, 19, 3, 0.5)', showlegend = False),
                  secondary_y=False)
fig.add_trace(go.Bar(x = df_incid_france['jour'], y = tests_tot_rolling-incid_rolling, name = "Nombre de tests réalisés", showlegend = False, marker_color ='rgba(186, 186, 186, 0.5)'),
              secondary_y=False)
fig.add_trace(go.Scatter(x = df_incid_france['jour'], y = taux, name = "Taux de tests positifs", showlegend = False, marker_opacity=0, line_width = 10, marker_color=clr),
              secondary_y=True)
fig.add_trace(go.Scatter(x = [df_incid_france['jour'].values[-1]], y = [taux.values[-1]], name = "Taux de tests positifs", mode='markers', marker_size=25, showlegend = False, marker_color=clr),
              secondary_y=True)

#fig.add_trace(go.Scatter(x = [data_dep["jour"].values[-2]], y = [data_dep[data_dep["jour"] == data_dep["jour"].values[-2]]["incid_rolling"].values[-1]], line_color=clr, mode="markers", marker_size=15, marker_color=clr),
             # i, j, secondary_y=False)

date_plus_1 = (datetime.strptime(dates_incid[-1], '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d')

fig.update_xaxes(title_text="", range=["2020-05-18", date_plus_1],gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=30), tickangle=0, linewidth=0, linecolor='white')
#fig.update_yaxes(title_text="", range=[0, 5], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j, secondary_y=True)
fig.update_yaxes(title_text="", titlefont=dict(size=30),gridcolor='white', linewidth=0, ticksuffix=" tests", linecolor='white', tickfont=dict(size=30), nticks=8, secondary_y=False) #, type="log"
fig.update_yaxes(title_text="", titlefont=dict(size=30, color="blue"), ticksuffix=" %", range=[0, taux.max()*1.5], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=30, color=clr), nticks=8,  secondary_y=True)

for i in fig['layout']['annotations']:
    i['font'] = dict(size=30)

fig['layout']['annotations'] += (dict(
        x=dates_incid[-1], y = incid_rolling.values[-1], # annotation point math.log10(
        xref='x1', 
        yref='y1',
        text="<b>{} tests positifs</b><br>chaque jour<br>".format(math.trunc(round(incid_rolling.values[-1], 1)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=30,
            ),
        ax=-250,
        ay=-150,
        arrowcolor="red",
        opacity=0.8,
        arrowsize=1,
        arrowwidth=3,
        arrowhead=0
    ),
    dict(
        x=dates_incid[-1], y = taux.values[-1], # annotation point
        xref='x1', 
        yref='y2',
        text="<b>{} %</b> des tests<br>sont <b>positifs</b>".format(str(round(taux.values[-1],2)).replace(".", ","), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=15,
        xanchor="center",
        align='center',
        font=dict(
            color=clr,
            size=30,
            ),
        ax=-300,
        ay=-160,
        arrowcolor=clr,
        opacity=1,
        arrowsize=1,
        arrowwidth=4,
        arrowhead=4
    ),
        dict(
        x=dates_incid[-1], y = tests_tot_rolling.values[-1], # annotation point math.log10(
        xref='x1', 
        yref='y1',
        text="<b>{} tests</b> sont réalisés<br>chaque jour<br>".format(math.trunc(round(tests_tot_rolling.values[-1], 0)), datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=0,
        xanchor="center",
        align='center',
        font=dict(
            color="black",
            size=30,
            ),
        ax=-170,
        ay=-90,
        arrowcolor="black",
        opacity=0.7,
        arrowsize=1,
        arrowwidth=3,
        arrowhead=0
    ))


fig.update_layout(
    barmode="stack",
    paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
    title={
                'text': "",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    
    
    margin=dict(
        l=30,
        r=0,
        b=1000,
        t=32,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)
commentaire = "Mis à jour : {}.<br><br>Les barres rouges représentent le nombre de tests virologiques positifs et les barres<br>grises le nombre de tests négatifs (axe de gauche). Les données sont moyennées sur<br>7 jours afin de lisser les irrégularités. La ligne représente le taux de tests<br>positifs (axe de droite).<br>La couleur du trait de positivité dépend de sa valeur (vert si < 1%, rouge si > 5%).<br>Les données proviennent de Santé publique France.<br><br>Plus de graphiques sur covidtracker.fr. Auteur : Guillaume Rozier.".format(now.strftime('%d %B %Y'))
fig["layout"]["annotations"] += (
                    dict(
                        x=-0.08,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        align="left",
                        text = commentaire,
                        showarrow = False,
                        font=dict(size=40), 
                        opacity=0.8
                    ),)


name_fig = "incidence_taux_france"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1700, height=2300)

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


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)

locale.setlocale(locale.LC_ALL, '')
#fig.show()


# In[17]:


tests_tot_rolling.max()


# ## Titre composition tests

# In[18]:


fig = go.Figure()

fig.update_xaxes(title_text="", visible=False)
fig.update_yaxes(title_text="", visible=False)

fig.update_layout(
    paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    plot_bgcolor='#fffdf5',#f5f0e4 fcf8ed f0e8d5
)

commentaire = "Les points rouges représentent les données brutes quotidiennes. Les lignes rouges sont obtenues en effectuant la moyenne mobile<br>centrée, sur 7 jours. <i>Guillaume Rozier pour covidtracker.fr - {}</i>".format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y'))
fig["layout"]["annotations"] += (
                    dict(
                        x=0.5,
                        y=1.5,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<b>Analyse des tests du COVID-19 en France</b>",
                        showarrow = False,
                        font=dict(size=80), 
                        opacity=0.8
                    ),dict(
                        x=0.25,
                        y=0.2,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<b>À l'échelle nationale</b>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.25,
                        y=-0.4,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<sub>Échelle de gauche : nombre de tests</sub>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.75,
                        y=0.1,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<b>Dans chaque département</b>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ),
                    dict(
                        x=0.75,
                        y=-0.4,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        align="left",
                        text = "<sub>Échelle de gauche : nombre de tests pour 100k habitants de chaque département</sub>",
                        showarrow = False,
                        font=dict(size=60), 
                        opacity=0.8
                    ))


name_fig = "title_incidence"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=3400, height=300)
#fig.show()


# ## R_effectif

# In[19]:


#### Calcul du R_effectif

# Paramètres R_effectif
std_gauss= 5
wind = 7
delai = 7

df_sursaud_dep = df_sursaud.groupby(["date_de_passage"]).sum().reset_index()
df_sursaud_dep = df_sursaud_dep.sort_values(by="date_de_passage")
nbre_pass = df_sursaud_dep["nbre_pass_corona"]

# Calcul suivant deux méthodes
df_sursaud_dep['reffectif_urgences'] = (nbre_pass.rolling(window= wind).sum() / nbre_pass.rolling(window = wind).sum().shift(delai) ).rolling(window=7).mean()
df_incid_france['reffectif_tests'] = (df_incid_france['P'].rolling(window= wind).sum() / df_incid_france['P'].rolling(window = wind).sum().shift(delai) ).rolling(window=7).mean()

# Calcul de la moyenne des deux
df_reffectif = pd.merge(df_sursaud_dep, df_incid_france, left_on="date_de_passage", right_on="jour", how="outer")
df_reffectif['reffectif_mean'] = df_reffectif[['reffectif_urgences', 'reffectif_tests']].mean(axis=1, skipna=False)
df_reffectif['reffectif_var'] = df_reffectif[['reffectif_urgences', 'reffectif_tests']].var(axis=1, skipna=False)

# Résultats
y_data = df_reffectif['reffectif_urgences']
y_data_tests = df_reffectif['reffectif_tests']

#### Construction du graphique
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Ajout R_effectif estimé via les urgences au graph
fig.add_trace(go.Scatter(x = df_reffectif["date_de_passage"], y = y_data.values,
                    mode='lines',
                    line=dict(width=2, color="rgba(96, 178, 219, 0.9)"),
                    name="À partir des données des admissions aux urgences",
                    marker_size=4,
                    showlegend=True
                       ))

# Ajout R_effectif estimé via les tests au graph
fig.add_trace(go.Scatter(x = df_reffectif["date_de_passage"], y = y_data_tests.shift(0).values,
                    mode='lines',
                    line=dict(width=2, color="rgba(108, 212, 141, 0.9)"),
                    name="À partir des données des tests PCR",
                    marker_size=5,
                    showlegend=True
                         ))

# Ajout R_effectif moyen au graph
fig.add_trace(go.Scatter(x = df_reffectif["date_de_passage"], y = df_reffectif['reffectif_mean'],
                    mode='lines',
                    line=dict(width=4, color="rgba(0,51,153,1)"),
                    name="R_effectif moyen",
                    marker_size=4,
                    showlegend=True
                         ))

# Calcul écart-type
y_std = (nbre_pass.rolling(window= wind, win_type="gaussian").sum(std= std_gauss) / nbre_pass.rolling(window = wind, win_type="gaussian").sum(std = std_gauss).shift(delai) ).rolling(window=7).std()
y_std_tests = (df_incid_france['T'].rolling(window= wind, win_type="gaussian").sum(std= std_gauss) / df_incid_france['T'].rolling(window = wind, win_type="gaussian").sum(std = std_gauss).shift(delai) ).rolling(window=7).std()

# Ajout du collier écart-type
fig.add_trace(go.Scatter(x = df_reffectif["jour"], y = df_reffectif['reffectif_tests'],
                    mode='lines',
                    line=dict(width=0),
                    name="",
                    marker_size=8,
                    showlegend=False
                            ))

fig.add_trace(go.Scatter(x = df_reffectif["jour"].values[101:], y = df_reffectif['reffectif_urgences'].values[101:],
                    mode='lines',
                    line=dict(width=0),
                    name="",
                    marker_size=100,
                    showlegend=False,
                    fill = 'tonexty', fillcolor='rgba(0,51,153,0.1)'
                            ))
# Mis en valeur de la dernière valeur du R_effectif
reffectif_now = df_reffectif[df_reffectif["date_de_passage"] == df_reffectif["jour"].dropna().max()]["reffectif_mean"].values[-1]
fig.add_trace(go.Scatter(x = [df_reffectif["jour"].dropna().max()], y = [reffectif_now],
                    mode='markers',
                    name="",
                    line=dict(width=4, color="rgba(0,51,153,1)"),
                    marker_color='rgba(0,51,153,1)',
                    marker_size=12,
                    showlegend=False
                            ))
# Modification du layout
fig.update_layout(
    margin=dict(
            l=0,
            r=0,
            b=0,
            t=80,
            pad=0
        ),
    legend_orientation="h",
    title={
                'text': "Estimation du <b>taux de reproduction R<sub>effectif</sub></b><br><sub>Différence entre le nb de suspicion Covid19 aux urgences à 7 jours d'intervalle (moyenne mobile de 7j)".format(),
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0.5,
                    y=-0.12,
                    xref='paper',
                    yref='paper',
                    opacity=0.8,
                    text='Date : {}. Source : Santé publique France. Auteur : Guillaume Rozier - covidtracker.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="", range=["2020-03-17", last_day_plot])
fig.update_yaxes(title="", range=[0, 3], secondary_y=False)

# Ajout de zones de couleur
fig.add_shape(
        # filled Rectangle
            type="rect",
            x0="2020-03-15",
            y0=1,
            x1=last_day_plot,
            y1=1,
            line=dict(
                color="orange",
                width=1,
                dash="dot"
            ),
            opacity=0.8
        )

fig.add_shape(
        # filled Rectangle
            type="rect",
            x0="2020-03-15",
            y0=1.5,
            x1=last_day_plot,
            y1=1.5,
            line=dict(
                color="red",
                width=1,
                dash="dot"
            ),
            opacity=0.8
        )

if reffectif_now < 1:
    comm_epid = "donc l'épidémie régresse"
else:
    comm_epid = "donc l'épidémie s'aggrave"
    

fig['layout']['annotations'] += (dict(
        x= df_reffectif["jour"].dropna().max(), y = reffectif_now, # annotation point
        xref='x1', 
        yref='y1',
        text="<b>Un malade contamine {}<br>autres personnes</b> en moyenne,<br>{}".format(str(round(reffectif_now, 2)).replace('.', ','), comm_epid),
        xshift=-5,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgba(0,51,153,1)",
            size=15
            ),
        opacity=1,
        ax=-170,
        ay=-150,
        arrowcolor="rgba(0,51,153,1)",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),)

name_fig = "reffectif"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# In[20]:


df_tests_viros_france = df_tests_viros.groupby(['jour', 'cl_age90']).sum().reset_index()
df_tests_viros_france = df_tests_viros_france[df_tests_viros_france['cl_age90'] != 0]


#df_essai = df_tests_viros_france.groupby(['cl_age90', 'jour']).sum().rolling(window=20).mean()
df_tests_rolling = pd.DataFrame()
array_positif= []
array_taux= []
array_incidence=[]
for age in list(dict.fromkeys(list(df_tests_viros_france['cl_age90'].values))):
    df_temp = pd.DataFrame()
    df_tests_viros_france_temp = df_tests_viros_france[df_tests_viros_france['cl_age90'] == age]
    df_temp['jour'] = df_tests_viros_france_temp['jour']
    df_temp['cl_age90'] = df_tests_viros_france_temp['cl_age90']
    df_temp['P'] = (df_tests_viros_france_temp['P']).rolling(window=7).mean()
    df_temp['T'] = (df_tests_viros_france_temp['T']).rolling(window=7).mean()
    df_temp['P_taux'] = (df_temp['P']/df_temp['T']*100)
    df_tests_rolling = pd.concat([df_tests_rolling, df_temp])
    df_tests_rolling.index = pd.to_datetime(df_tests_rolling["jour"])
    #tranche = df_tests_rolling[df_tests_rolling["cl_age90"]==age]
    tranche = df_tests_viros_france[df_tests_viros_france["cl_age90"]==age]
    tranche.index = pd.to_datetime(tranche["jour"])
    tranche = tranche[tranche.index.max() - timedelta(days=7*18-1):].resample('7D').sum()
    array_positif += [tranche["P"].astype(int)]
    array_taux += [np.round(tranche["P"]/tranche["T"]*100, 1)]
    array_incidence += [np.round(tranche["P"]/tranche["pop"]*7*100000,0).astype(int)]
    
    dates_heatmap = list(tranche.index.astype(str).values)
df_tests_rolling = df_tests_rolling[df_tests_rolling['jour'] > "2020-05-18"]
df_tests_rolling['cl_age90'] = df_tests_rolling['cl_age90'].replace(90,99)

dates_heatmap_firstday = tranche.index.values
dates_heatmap_lastday = tranche.index + timedelta(days=6)
dates_heatmap = [str(dates_heatmap_firstday[i])[8:10] + "/" + str(dates_heatmap_firstday[i])[5:7] + "<br>" + str(dates_heatmap_lastday[i])[8:10] + "/" + str(dates_heatmap_lastday[i])[5:7] for i, val in enumerate(dates_heatmap_firstday)]


# In[21]:


temp = df_tests_viros_france.groupby(["jour"]).sum().reset_index()


# In[22]:


for (val, valname) in [('P', 'positifs'), ('T', '')]:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==9][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[0]),
        stackgroup='one',
        groupnorm='percent', # sets the normalization for the sum of the stackgroup,
        name="0 à 9 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==19][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[1]),
        stackgroup='one',
        name="10 à 19 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==29][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[2]),
        stackgroup='one',
        name="20 à 29 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==39][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[3]),
        stackgroup='one',
        name="30 à 39 ans"
    ))

    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==49][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[4]),
        stackgroup='one',
        name="40 à 49 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==59][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[5]),
        stackgroup='one',
        name="50 à 59 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==69][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[6]),
        stackgroup='one',
        name="60 à 69 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==79][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[7]),
        stackgroup='one',
        name="70 à 79 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==89][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[8]),
        stackgroup='one',
        name = "80 à 89 ans"
    ))
    fig.add_trace(go.Scatter(
        x=df_tests_rolling["jour"], y=df_tests_rolling[df_tests_rolling["cl_age90"]==99][val],
        mode='lines',
        line=dict(width=0.5, color=px.colors.qualitative.Plotly[9]),
        stackgroup='one',
        name="90+ ans"
    ))

    fig.update_layout(
        annotations = [
                    dict(
                        x=0,
                        y=1.05,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    )],
        margin=dict(
                    l=20,
                    r=100,
                    b=20,
                    t=65,
                    pad=0
                ),
        showlegend=True,
         title={
                'text': "Répartition des tests{} réalisés en fonction de l'âge".format(" "+valname),
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        titlefont = dict(
                size=20),
        xaxis=dict(
            tickformat='%d/%m',
            nticks=25),
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'))

    #fig.show()
    name_fig = "repartition_age_tests{}".format(valname)
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[23]:


import plotly.figure_factory as ff

for (name, array, title, scale_txt, data_example, digits) in [("cas", array_positif, "Nombre de <b>tests positifs</b>", "", "", 0), ("taux", array_taux, "Taux de <b>positivité</b>", "%", "%", 1), ("incidence", array_incidence, "Taux d'<b>incidence</b>", " cas", " cas", 1)]: #
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    fig = ff.create_annotated_heatmap(
            z=array, #df_tests_rolling[data].to_numpy()
            x=dates_heatmap,
            y=[str(x-9) + " à " + str(x)+" ans" if x!=99 else "+ 90 ans" for x in range(9, 109, 10)],
            showscale=True,
            coloraxis="coloraxis",
            #text=df_tests_rolling[data],
            annotation_text = array
            )
    
    annot = []

    #fig.update_xaxes(title_text="", tickformat='%d/%m', nticks=20, ticks='inside', tickcolor='white')
    fig.update_xaxes(side="bottom", tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))
    #fig.update_yaxes(title_text="Tranche d'âge", ticksuffix=" ans", ticktext=["< 10", "10 - 20", "20 - 30", "30 - 40", "40 - 50", "50 - 60", "60 - 70", "70 - 80", "80 - 90", "> 90"], tickmode='array', tickvals=[9, 19, 29, 39, 49, 59, 69, 79, 89, 99], tickcolor="white")
    annots = annot + [
                    dict(
                        x=0.5,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=10),
                        text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à gauche) et à une date donnée (à lire en bas).<br>Du orange correspond à un {} élevé.  <i>Date : {} - Source : covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ]
    
        
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 7
        
    for annot in annots:
        fig.add_annotation(annot)
    
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
            #cmin=0, cmax=100,
            #colorscale='Inferno',
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=8,
                lenmode="pixels", len=200,
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

    name_fig = "heatmap_"+name
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[24]:


"""#OLD HEATMAP
for (name, data, title, scale_txt, data_example, digits) in [("cas", 'P', "Nombre de<br>tests positifs", "", "", 0), ("taux", 'P_taux', "Taux de<br>positivité", "%", "%", 1)]:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    fig = go.Figure(data=go.Heatmap(
            z=df_tests_rolling[data],
            x=df_tests_rolling['jour'],
            y=df_tests_rolling['cl_age90'],
            coloraxis="coloraxis"
            ))

    #fig['layout']['annotations'] += (,)
    
    annot = []
    
        
    for cl_age in range(9, 109, 10):
        val = round(df_tests_rolling.loc[(df_tests_rolling["cl_age90"]==cl_age) & (df_tests_rolling["jour"]==df_tests_rolling["jour"].max()), data].values[0], digits)
    
        if digits == 0:
            val = math.trunc(val)
        
        annot += [dict(
                    x=df_tests_rolling['jour'].max(), y = cl_age, # annotation point
                    xref='x1', 
                    yref='y1',
                    text="{}{}".format(str(val).replace(".", ","), data_example),
                    xshift=0,
                    xanchor="center",
                    align='left',
                    font=dict(
                        color="black",
                        size=10
                        ),
                    opacity=0.6,
                    ax=20,
                    ay=0,
                    arrowcolor="black",
                    arrowsize=0.7,
                    arrowwidth=0.6,
                    arrowhead=4,
                    showarrow=True
                )]

    fig.update_xaxes(title_text="", tickformat='%d/%m', nticks=20, ticks='inside', tickcolor='white')
    fig.update_yaxes(title_text="Tranche d'âge", ticksuffix=" ans", ticktext=["< 10", "10 - 20", "20 - 30", "30 - 40", "40 - 50", "50 - 60", "60 - 70", "70 - 80", "80 - 90", "> 90"], tickmode='array', tickvals=[9, 19, 29, 39, 49, 59, 69, 79, 89, 99], tickcolor="white")
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
            #cmin=0, cmax=100,
            colorscale='Inferno',
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=12,
                lenmode="pixels", len=300,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(scale_txt),
                )
        ),
        annotations = annot + [
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
                ],
    margin=dict(
                    b=80,
                    t=40,
                    pad=0
                ))

    name_fig = "heatmap_"+name
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=900, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)"""


# In[25]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

y_vals = df_france['rea']/df_france['LITS']*100
clrs_dep = []

for val in y_vals.values:
    if val < 60:
        clrs_dep += ["green"]
    elif val < 80:
        clrs_dep += ["orange"]
    else:
        clrs_dep += ["red"]
    
fig = go.Figure()

fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=100,
            x1="2030-01-01",
            y1=100,
            opacity=1,
            fillcolor="orange",
            line=dict(
                color="red",
                width=1,
            )
        )
"""fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=100,
            x1="2030-01-01",
            y1=100,
            opacity=1,
            fillcolor="red",
            line=dict(
                color="red",
                width=1,
            )
        )
fig.add_shape(
            type="line",
            x0="2000-01-01",
            y0=80,
            x1="2030-01-01",
            y1=80,
            opacity=1,
            fillcolor="red",
            line=dict(
                color="red",
                width=1,
                dash="dot",
            )
        )"""

fig.add_trace(go.Bar(x = df_france['jour'], y = y_vals, opacity=0.8, marker_color=clrs_dep, name = "<b>nombre total</b> d'admissions aux urgences • d'actes SOS Médecin ", showlegend=False),)

fig.update_xaxes(title_text="", range=["2020-03-17", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white')
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white')
    
fig['layout']['annotations'] += (dict(
        x= dates[-1], y = y_vals.values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{}</b> % des lits de réa.<br>sont occupés par des<br>patients Covid19".format(math.trunc(round(y_vals.values[-1], 0) )),
        yshift=8,
        xanchor="center",
        align='center',
        font=dict(
            color=clrs_dep[-1],
            size=15
            ),
        opacity=1,
        ax=-50,
        ay=-100,
        arrowcolor=clrs_dep[-1],
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),
        dict(
        x= "2020-04-08", y = y_vals.values[21], # annotation point
        xref='x1', 
        yref='y1',
        text="&#8205; <br><b>{}</b> % des lits de réa. étaient occupés<br>par des patients Covid19 le 8 avril".format(math.trunc(round(y_vals.values[21], 0)) ),
        yshift=8,
        xanchor="center",
        align='center',
        font=dict(
            color="red",
            size=16
            ),
        opacity=1,
        ax=0,
        ay=-60,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ),
    dict(
        x=0.48,
        y=1.09,
        xref='paper',
        yref='paper',
        xanchor='center',
        text='par rapport au nombre de lits de réa. en France fin 2018 (DREES)',
        font=dict(size=15),
        showarrow = False)
                                
                                )

fig.update_layout(
    title={
                'text': "<b>Saturation des services de réanimation</b> par les patients Covid19",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),
    margin=dict(
        l=0,
        r=25,
        b=0,
        t=100,
        pad=0
    ),
    bargap=0,
    legend_orientation="h",
    showlegend=True,

)

fig["layout"]["annotations"] += (
                dict(
                    x=0,
                    y=1.03,
                    xref='paper',
                    yref='paper',
                    font=dict(size=9),
                    text='Date : {}. Source : Santé publique France et DREES. Auteur : covidtracker.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),)
            

name_fig = "indic2_france"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

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

print("> " + name_fig)


locale.setlocale(locale.LC_ALL, '')
#fig.show()


# In[26]:



fig = make_subplots(rows=2, cols=1, shared_yaxes=True, subplot_titles=["Nombre de personnes<b> hospitalisées</b><br>(moyenne mobile 7 jours)", "Nombre de personnes en <b>réanimation</b><br> (moyenne mobile 7 jours)"], vertical_spacing = 0.15, horizontal_spacing = 0.1)

##
fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['hosp'].rolling(window=7, center=True).mean(),
                    marker=dict(color =df_france['hosp_new'].rolling(window=7, center=True).mean(), coloraxis="coloraxis1"), ),
              1, 1)
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['hosp'],
                    mode="markers",
                    marker_size=8,
                    marker_symbol="x-thin",
                    marker_line_color="Black", marker_line_width=0.7, opacity=0.5),
              1, 1)
##
fig.add_trace(go.Bar(x=df_france['jour'], y=df_france['rea'].rolling(window=7, center=True).mean(),
                    marker=dict(color =df_france['rea_new'].rolling(window=7, center=True).mean(), coloraxis="coloraxis2"), ),
              2, 1)
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['rea'],
                    mode="markers",
                    marker_size=8,
                    marker_symbol="x-thin",
                    marker_line_color="Black", marker_line_width=0.7, opacity=0.5),
              2, 1)
##
fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=1, col=1)

fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=2, col=1)


for i in fig['layout']['annotations']:
    i['font'] = dict(size=25)

fig.update_layout(
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    bargap=0,
    coloraxis1=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['hosp_new'].max(), cmax=df_france['hosp_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. hospitalisées<br> &#8205; ",
                        thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.79, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))),
    coloraxis2=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['rea_new'].max(), cmax=df_france['rea_new'].max(),
                   colorbar=dict(
                        title="Solde quotidien de<br>pers. en réanimation<br> &#8205; ",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="middle", y=0.22, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15))), 


                showlegend=False,

)
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=0.52,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='Source : Santé publique France - covidtracker.fr - {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

name_fig = "hosp_rea_bar_ROLLING"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=1200)

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
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# In[27]:


locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
data= pd.DataFrame()
data["dc_new_r"] = df_france['dc_new'][1:].rolling(window=7, center=True).mean()
data["jour"] = df_france["jour"]

fig = go.Figure()
fig.add_trace(go.Bar(x=df_france.iloc[data.index]['jour'], y=data["dc_new_r"],
                    marker=dict(color = data["dc_new_r"].diff().fillna(method='backfill'), coloraxis="coloraxis"), ))
fig.add_trace(go.Scatter(x=df_france.iloc[data.index]['jour'], y=df_france['dc_new'][1:],
                    mode="markers",
                    marker_size=6,
                    marker_symbol="x-thin",
                    marker_line_color="Black", marker_line_width=0.6, opacity=0.5))

fig.update_xaxes(title_text="", range=["2020-03-24", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white')
fig.update_yaxes(title_text="", range=[0, 700], gridcolor='white', linewidth=1, linecolor='white')

fig.update_layout(
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    title={
                'text': "<b>Nombre de décès quotidiens hospitaliers dus au Covid-19</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),
    bargap=0,
    coloraxis=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-df_france['dc_new'].rolling(window=7, center=True).mean().diff().max(), cmax=df_france['dc_new'].rolling(window=7, center=True).mean().diff().max(),
                   colorbar=dict(
                        title="Variation quotidienne<br>du nombre de<br>nouveaux décès<br> &#8205; ",
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=300,
                        yanchor="middle", y=0.5, xanchor="left", x=1.05,
                        ticks="outside", tickprefix="  ", ticksuffix=" pers.",
                        nticks=15,
                        tickfont=dict(size=8),
                        titlefont=dict(size=10))), 


                showlegend=False,

)


fig["layout"]["annotations"] += ( dict(
                        x=0.5,
                        y=0.5,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='guillaumerozier.fr - {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0
                    ),
                                dict(
                        x=0.56,
                        y=1.08,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        text='moyenne mobile centrée sur 7 jours pour lisser les week-ends - Données Santé publique France - covidtracker.fr',
                        font=dict(size=15),
                        showarrow = False),)

fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/covidtracker_logo_text.jpeg",
            xref="paper", yref="paper",
            x=1.15, y=1.1,
            sizex=0.15, sizey=0.15,
            xanchor="right", yanchor="top", opacity=0.8
            )
) 
data_au_max = data[data["jour"] == "2020-04-05"]["dc_new_r"].values
fig['layout']['annotations'] += (dict(
        x= dates[-4], y = data["dc_new_r"].values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} décès</b> quotidiens<br>en moyenne sur 7 jours<br>(du {} au {})".format(math.trunc(round(data["dc_new_r"].values[-4], 0) ), datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=1,
        xanchor="center",
        align='center',
        font=dict(
            color = "black",
            size=15
            ),
        opacity=0.7,
        ax=-200,
        ay=-300,
        arrowcolor = "black",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=0
    ),
        dict(
        x= "2020-04-05", y = data_au_max[0], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} décès</b> quotidiens<br>en moyenne sur 7 jours<br>(du 2 au 8 avril)".format(math.trunc(round(data_au_max[0], 0) )),
        yshift=-10,
        xanchor="center",
        align='center',
        font=dict(
            color = "black",
            size=15
            ),
        opacity=0.7,
        ax=0,
        ay=-100,
        arrowcolor = "black",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=0
    ),
        dict(
        x= dates[-1], y = df_france['dc_new'][1:].values[-1], # annotation point
        xref='x1', 
        yref='y1',
        text="<b>{} décès</b><br>le {}".format(math.trunc(round(df_france['dc_new'][1:].values[-1], 0) ), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B')),
        yshift=5,
        xanchor="center",
        align='center',
        font=dict(
            color = "grey",
            size=15
            ),
        opacity=0.9,
        ax=-25,
        ay=-150,
        arrowcolor = "grey",
        arrowsize=1,
        arrowwidth=1.5,
        arrowhead=4
    ))

name_fig = "dc_new_bar"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

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
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# In[28]:




fig = go.Figure()

y = [df_new.sum()["incid_rea"]]
fig.add_trace(go.Bar(x=["Hospitalisations cumulées"], y=y, marker_color="Red", text=str(y[0])+"<br>Réanimations cumulées")).update_xaxes(categoryorder="total descending")

y = [df_new.sum()["incid_dc"]]
fig.add_trace(go.Bar(x=["Décès hosp. cumulés"], y=y, marker_color="Black", text=y)).update_xaxes(categoryorder="total descending")

y = [df_new.sum()["incid_hosp"]-df_new.sum()["incid_rea"]]
fig.add_trace(go.Bar(x=["Hospitalisations cumulées"], y= y, marker_color="Orange", text=str(y[0])+"<br>Autres hospitalisations cumulées")).update_xaxes(categoryorder="total descending")

y = [df_new.sum()["incid_rad"]]
fig.add_trace(go.Bar(x=["Retours à domicile cumulés"], y=y, marker_color="Green", text=y)).update_xaxes(categoryorder="total descending")

fig.update_traces(textposition='auto')

fig.update_layout(
    barmode="stack",
    margin=dict(
        l=0,
        r=150,
        b=0,
        t=90,
        pad=0
    ),
    title={
                'text': "<b>Nombre cumulé de personnes hospitalisées, décédées et guéries du Covid-19</b>",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'middle'},
                titlefont = dict(
                size=20),


                showlegend=False,

)

fig["layout"]["annotations"] += (
                                dict(
                        x=0.56,
                        y=1.08,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        text='Données : Santé publique France  -  guillaumerozier.fr  -  {}'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                        font=dict(size=15),
                        showarrow = False),)

name_fig = "sum"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

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
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)


#fig.show()


# ## Situation cas (bar chart)
# Où en sont les personnes atteintes du Covid (retour à domicile, décédées, en réa, hosp ou autre)

# In[29]:



df_region_sumj = df_region.groupby('jour').sum().reset_index()
df_region_sumj = pd.melt(df_region_sumj, id_vars=['jour'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['jour'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)
df_bar = df_region_sumj

data = df_bar[df_bar["variable"] == "dc"]
fig = go.Figure(go.Bar(x=data['jour'], y=-data['value'], textposition='auto', name='Décès hosp. cumulés', marker_color='#000000', opacity=0.8))

data = df_bar[df_bar["variable"] == "rea"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], textposition='auto', name='Actuellement en réa.', marker_color='#FF0000', opacity=0.8))

data = df_bar[df_bar["variable"] == "hosp_nonrea"]
fig.add_trace(go.Bar(x=data['jour'], y=data['value'], textposition='auto', name="Actuellement en autre hosp.", marker_color='#FFA200', opacity=0.8))

"""if len(df_confirmed[df_confirmed["date"].isin([dates[-1]])]) > 0:
    data = df_confirmed[df_confirmed["date"].isin(dates)].reset_index()
    sum_df = df_bar[df_bar["variable"] == "dc"]['value'].reset_index() + df_bar[df_bar["variable"] == "rea"]['value'].reset_index() +  df_bar[df_bar["variable"] == "hosp_nonrea"]['value'].reset_index() + df_bar[df_bar["variable"] == "rad"]['value'].reset_index()
    fig.add_trace(go.Bar(x=data['date'], y=data['France'] - sum_df['value'], text = data['France'] - sum_df['value'], textposition='auto', name='Non hospitalisés', marker_color='grey', opacity=0.8))
"""
data = df_bar[df_bar["variable"] == "rad"]

fig.add_trace(go.Bar(x=data['jour'], y=data['value'], textposition='auto', name='Retours à domicile cumulés', marker_color='green', opacity=0.8))
fig.update_yaxes(title="Nb. de cas")

fig.update_layout(
            bargap=0,
            legend_orientation="h",
            barmode='relative',
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
                ticks="inside"
            ),
            annotations = [
                dict(
                    x=0,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)

name_fig = "situation_cas"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

fig.update_layout(
    bargap=0,
    legend_orientation="h",
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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# <br>
# <br>
# <br>
# 
# # Line charts

# ## Décès hospitalisations et réanimations (line chart)

# In[30]:


df_france = df.groupby('jour').sum().reset_index()

#fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['rea'],
                    mode='lines+markers',
                    name="Réanimations", #(<i>axe de gauche</i>)
                    line=dict(width=2),
                    marker_size=8,
                            ))
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['dc'],
                    mode='lines+markers',
                    name="décès hospitaliers cumulés", #(<i>axe de droite</i>)
                    line=dict(width=2),
                    marker_size=8,
                    
                            ),
             #secondary_y=True
             )
fig.add_trace(go.Scatter(x=df_france['jour'], y=df_france['hosp_nonrea'],
                    mode='lines+markers',
                    name="Autres hospitalisations", #(<i>axe de gauche</i>)
                    line=dict(width=2),
                    marker_size=8,
                            ))
    
#fig = px.line(, color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    legend_orientation="v",
    title={
                'text': "Nombre d'<b>hospitalisations et réanimations</b> et <b>décès</b> ", #(<i>Attention ! Axes distincs</i>)
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de personnes (réa et hosp)")
fig.update_yaxes(title="Nb. de décès hosp.", secondary_y=True)

name_fig = "dc_hosp_rea_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

if show_charts:
    fig.show()
print("> " + name_fig)


# ## Décès cumulés (line chart)

# In[31]:



fig = px.line(x=df_region['jour'], y=df_region['dc'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "Nombre de <b>décès cumulés</b>",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès hosp. cumulés")

name_fig = "dc_cum_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[32]:



fig = px.line(x = df_new_region['jour'], y = df_new_region['incid_dc'], color = df_new_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "Nombre de <b>décès quotidiens</b>",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès hosp. en 24h")

name_fig = "dc_journ_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations

# In[33]:



fig = px.line(x=df_region['jour'], y=df_region['hosp'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients hospitalisés")

name_fig = "hosp_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations (entrées - sorties) (line chart)

# In[34]:



fig = px.line(x=df_region['jour'], y=df_region['hosp_new'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "<b>Variation des hospitalisations</b> (entrées - sorties)",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de nouveaux patients hospitalisés")

name_fig = "hosp_variation_journ_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Admissions en hospitalisation (line chart)

# In[35]:



fig = px.line(x = df_new_region['jour'], y = df_new_region['incid_hosp'].rolling(window=7).mean(), color = df_new_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
#.rolling(window=7, center=True).mean()
fig.update_layout(
    title={
                'text': "<b>Nouvelles admissions en hospitalisation</b> (moyenne mobile 7 derniers j.)",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour", range=[dates[6], last_day_plot])
fig.update_yaxes(title="Admissions hospitalisations")

name_fig = "hosp_admissions_journ_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations par région (line chart)

# In[36]:


fig = px.line(x=df_region['jour'], y=df_region['rea'], color=df_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients en réanimation")

name_fig = "rea_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations par département (line chart)

# In[37]:


df_last_d = df[df['jour'] == dates[-1]]
#deps_ordered = df_last_d.sort_values(by=['rea'], ascending=False)["dep"].values
deps_ordered = df_last_d.sort_values(by=['dep'], ascending=True)["dep"].values

fig = go.Figure()
for dep in deps_ordered:
    fig.add_trace(go.Scatter(x=df['jour'], y=df[df["dep"] == dep]["rea"],
                    mode='lines+markers',
                    name=dep,
                    line=dict(width=2),
                    marker_size=8,
                            ))

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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients en réa. ou soins intensifs")

name_fig = "rea_dep"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations par département (line chart)

# In[38]:


df_last_d = df[df['jour'] == dates[-1]]
#deps_ordered = df_last_d.sort_values(by=['rea'], ascending=False)["dep"].values
deps_ordered = df_last_d.sort_values(by=['dep'], ascending=True)["dep"].values

fig = go.Figure()
for dep in deps_ordered:
    fig.add_trace(go.Scatter(x=df['jour'], y=df[df["dep"] == dep]["hosp"],
                    mode='lines+markers',
                    name=dep,
                    line=dict(width=2),
                    marker_size=8,
                            ))

fig.update_layout(
    title={
                'text': "Nb. de <b>patients hospitalisés</b> par département",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients hospitalisés")

name_fig = "hosp_dep"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Hospitalisations par habitant / région

# In[39]:


"""
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de patients hospitalisés/100k hab. (de ch. région)")

name_fig = "hosp_hab"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
if show_charts:
    fig.show()
"""


# <br>
# 
# ## Capacité réanimation (line chart)

# In[40]:


"""
df_rean = df.groupby('jour').sum().reset_index()
df_rean["lim_rea_prev"] = [14000 for i in range(len(dates))]
df_rean["lim_rea"] = [10000 for i in range(len(dates))]
df_rean = pd.melt(df_rean, id_vars=['jour'], value_vars=['rea', 'lim_rea', 'lim_rea_prev'])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'rea']['value'],
                    mode='lines+markers',
                    name='Nb. patients réa.',
                    line=dict(width=4),
                    marker_size=11,))

fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'lim_rea_prev']['value'],
                    mode='lines',
                    name='Capacité max. prévue',
                    line=dict(width=4),
                    marker_size=11,))

fig.add_trace(go.Scatter(x=df_rean['jour'], y=df_rean[df_rean['variable'] == 'lim_rea']['value'],
                    mode='lines',
                    name='Capacité approx. actuelle',
                    line=dict(width=4),
                    marker_size=11,))

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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "capacite_rea"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1000, height=700)

fig.update_layout(
    legend_orientation="h",
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
print("> " + name_fig)
if show_charts:
    fig.show()"""


# <br>
# 
# ## Décès cumulés (région)

# In[41]:


fig = px.line(x=df_region['jour'], y=df_region['dc'], color=df_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors).update_traces(mode='lines+markers')
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. de décès hosp. cumulés")

name_fig = "dc_cum_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Nouveaux décès quotidiens (line chart)

# In[42]:


fig = px.line(x=df_new_region['jour'], y=df_new_region['incid_dc'].rolling(window=7, center=True).mean(), color=df_new_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors).update_traces(mode='lines+markers')
fig.update_layout(
    yaxis_type="log",
    title={
                'text': "<b>Nouveaux décès</b> par région (moyenne mobile 7 j.)",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour", range=[dates[6], last_day_plot])
fig.update_yaxes(title="Nb. de décès hosp.")

name_fig = "dc_nouv_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# In[43]:


fig = go.Figure()

for col in ["black", "color"]:
    i=0  
    for dep in departements:
        if (i==len(colors)):
            i=0
            
        if col=="black":
            colortemp = "black"
            leg=False
            opa=0.07
            size=2
            vis=True
            gp="g"
        else:
            colortemp=colors[i]
            leg=True
            opa=0.9
            size=3.5
            vis='legendonly'
            gp="g"+dep
            
        if dep in ["13", "75", "69"]:
            vis=True
        
        
        df_incid_dep = df_incid[df_incid["dep"]==dep]
        fig.add_trace(go.Scatter(x=df_incid_dep['jour'], y=df_incid_dep['P'].rolling(window=7, center=False).mean(), marker_color=colortemp, mode="lines", line_width=size, name=dep, visible=vis, showlegend=leg, legendgroup=gp, opacity=opa))
        if leg:
            fig.add_trace(go.Scatter(x=[df_incid_dep['jour'].values[-1]], y=[df_incid_dep['P'].rolling(window=7, center=False).mean().dropna().values[-1]], marker_color=colortemp, mode="markers+text", marker_size=6, name=dep, text=[dep], textposition='middle right', visible=vis, legendgroup=gp, showlegend=False, opacity=opa))
        i+=1
                            
fig.update_layout(
    margin=dict(
                l=0,
                r=0,
                b=0,
                t=20,
                pad=0
            ),
    yaxis_type="log",
    
    title={
                'text': "",
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="Jour", fixedrange=True)
fig.update_yaxes(title="Nb. de cas positifs.", fixedrange=True)

name_fig = "testspositifs_nouv_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

fig.update_layout(
    margin=dict(
                l=20,
                r=190,
                b=0,
                t=0,
                pad=0
            ),
    annotations = [
                dict(
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    xanchor='center',
                    text='',
                    showarrow = False
                )]
                 )
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False, config={"displayModeBar": False})
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés par habitant (région)

# In[44]:


"""
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

fig.update_xaxes(title="Jour")
fig.update_yaxes(title="Nb. décès cumulés / 100k hab. de chaq. région")

name_fig = "dc_cum_hab_line"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
if show_charts:
    fig.show()
"""


# <br>
# <br>
# <br>
# <br>
# 
# # Other bar charts

# <br>
# 
# ## Décès cumulés par région / temps

# In[45]:


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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
    
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de décès cumulés")
#fig.show()

name_fig = "dc_cum_region"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=500)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés par région / 3 derniers jours

# In[46]:



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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "dc_cum_region_comp"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1300, height=600)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés VS. Décès cumulés par habitant / région

# In[47]:


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
                    text='Date : {}. Source : Santé publique France, INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_yaxes(title_text="Nb. décès cumulés", secondary_y=False)
fig.update_yaxes(title_text="Nb. décès cumulés/100k hab.", secondary_y=True)

name_fig = "dc_cum_hab_nonhab_comp"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Situation des malades / région

# In[48]:


#df_region_sumj = df_region.groupby('regionName').sum().reset_index()
df_region_sumj = df_region[df_region['jour'] == dates[-1]]

df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[49]:


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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    
                    showarrow = False
                )]
)
fig.update_xaxes(categoryorder="total descending")     

name_fig = "situation_cas_region"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Situation des malades par habitant / région

# In[50]:


df_region_sumj = df_region[df_region['jour'] == dates[-1]]
df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad_pop', 'rea_pop', 'dc_pop', 'hosp_nonrea_pop'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[51]:


"""data = df_region_sumj[df_region_sumj["variable"] == "dc_pop"]
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)
fig.update_xaxes(categoryorder="total descending")        

name_fig = "situation_cas_region_hab"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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
print("> " + name_fig)
if show_charts:
    fig.show()"""


# <br>
# <br>
# <br>
# <br>
# 
# # Expérimentations (brouillon)

# In[52]:


"""
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="")
fig.update_yaxes(title="Nb. de patients en réanimation")

name_fig = "rea_reg"
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1100, height=700)

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

if show_charts:
    fig.show()
"""

