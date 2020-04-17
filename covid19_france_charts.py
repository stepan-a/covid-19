#!/usr/bin/env python
# coding: utf-8

# # COVID-19 French Charts
# Guillaume Rozier, 2020

# In[161]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.guillaumerozier.fr
Mail : guillaume.rozier@telecomnancy.net

README:s
This file contains scripts that download data from data.gouv.fr and then process it to build many graphes.
I'm currently cleaning the code, please ask me if something is not clear enough.

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[216]:


from multiprocessing import Pool
import requests
import pandas as pd
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
import france_data_management import download_data

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet
show_charts = False


# # Data download and import

# In[215]:


download_data()


# In[164]:




df, df_confirmed, dates, df_new, df_tests = data.import_data()

df_region = df.groupby(['regionName', 'jour', 'regionPopulation']).sum().reset_index()
df_region["hosp_regpop"] = df_region["hosp"] / df_region["regionPopulation"]*1000000 
df_region["rea_regpop"] = df_region["rea"] / df_region["regionPopulation"]*1000000 

df_tests_tot = df_tests.groupby(['jour']).sum().reset_index()

df_new_region = df_new.groupby(['regionName', 'jour']).sum().reset_index()
df_france = df.groupby('jour').sum().reset_index()

regions = list(dict.fromkeys(list(df['regionName'].values))) 


# In[165]:


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
df_new_tot_last15 = df_new_tot[ df_new_tot["jour"].isin(dates[-19:]) ]
df_france_last15 = df_france[ df_france["jour"].isin(dates[-19:]) ]
df_tests_tot_last15 = df_tests_tot[ df_tests_tot["jour"].isin(dates[-19:]) ]


# # Graphes: bar charts

# ## Variation journée

# In[166]:


#VAR JOURN

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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "var_journ"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1400, height=800)

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


# In[ ]:





# ## Evolution jorunée

# In[167]:


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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "evol_journ"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1400, height=800)

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

# In[168]:


# TESTS

fig = make_subplots(specs=[[{"secondary_y": True}]])
#fig = go.Figure()

fig.add_trace(go.Bar(
    x = df_tests_tot["jour"],
    y = df_tests_tot["nb_pos"].rolling(window=4).mean(),
    name = "Tests positifs",
    marker_color='red',
    opacity=0.6
), secondary_y=False)

fig.add_trace(go.Bar(
    x = df_tests_tot["jour"],
    y = df_tests_tot["nb_test"].rolling(window=4).mean(),
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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                )]
                 )

name_fig = "tests_journ"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1400, height=800)

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

# In[169]:


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
    #paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    #plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
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
        range=["2020-03-26", (datetime.strptime(dates[-1], '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")  ], # Adding one day
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
                    text='moyenne mobile sur les 4 précédents jours',
                    font=dict(size=17),
                    showarrow = False),
            
                dict(
                    x=0,
                    y=1.04,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),           
                    showarrow = False)
                ]
                )

name_fig = "entrees_sorties_hosp_rea"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=2, width=1200, height=800)

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


# ## Entrées/Sorties hosp et réa - rolling mean (4 days)
# La moyenne glissante sur 4 jours permet de lisser les effets liés aux week-ends (moins de saisies de données, donc il y a un trou) et d'évaluer la tendance.

# In[170]:


fig = go.Figure()
#fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_rea"].rolling(window=4).mean(),
    name = "Admissions réanimation",
    marker_color='red',
    opacity=0.8
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_hosp_nonrea"].rolling(window=4).mean(),
    name = "Admissions hospitalisation (hors réa.)",
    marker_color='red',
    opacity=0.5
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dep_rea"].rolling(window=4).mean(),
    name = "Sorties réanimation",
    marker_color='green',
    opacity=0.8
))

fig.add_trace(go.Bar(
    x = df_new_tot_last15["jour"],
    y = df_new_tot_last15["incid_dep_hosp_nonrea"].rolling(window=4).mean(),
    name = "Sorties hospitalisation (hors réa.)",
    marker_color='green',
    opacity=0.5
))

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = df_france["rea_new"].rolling(window=4).mean(),
    name = "Solde réanimation",
    marker_color='black',
    mode="lines+markers",
    opacity=0.8
))

fig.add_trace(go.Scatter(
    x = df_france["jour"],
    y = df_france["hosp_nonrea_new"].rolling(window=4).mean(),
    name = "Solde hosp. (hors réa.)",
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
        range=["2020-03-26", (datetime.strptime(dates[-1], '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")  ], # Adding one day
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
                    text='moyenne mobile sur les 4 précédents jours',
                    font=dict(size=17),
                    showarrow = False),
            
                dict(
                    x=0,
                    y=1.04,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),           
                    showarrow = False)
                ]
                )

name_fig = "entrees_sorties_hosp_rea_ROLLING"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=2, width=1200, height=800)

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

# In[171]:


fig = go.Figure()

"""fig.add_trace(go.Bar(
    x = df_france["jour"],
    y = df_france["hosp"],
    name = "Hospitalisations",
    opacity=0.6
))"""

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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1400, height=800)

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


# ## Subplots : régions
# Ce script génère 4 graphiques contenant les graphiques de :
# - nb d'hospitalisés,
# - nb d'hospitalisés par habitant des régions,
# - nb de réanimations,
# - nb de réanimations par habitant des régions,
# et ce pour toutes les régions françaises

# In[172]:



for val in ["hosp_regpop", "hosp", "rea", "rea_regpop"]:
    ni, nj = 5, 4
    i, j = 1, 1

    df_region[val+"_new"] = df_region[val].diff()
    max_value = df_region[val].max()
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles=[ "<b>"+ str(r) +"</b>" for r in (regions_ordered[:11] + [""] + regions_ordered[11:14]+[""]+regions_ordered[14:])], vertical_spacing = 0.06, horizontal_spacing = 0.01)
    #&#8681;
    
    type_ppl = "hospitalisées"
    if "rea" in val:
        type_ppl = "en réanimation"
        
    df_nonobj = df_region.select_dtypes(exclude=['object'])
    df_nonobj['jour'] = df_region['jour']
    
    vals_quantiles=[]
    for q in range(25, 125, 25):
        vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())
        
    for region in regions_ordered:
        data_r = df_region[df_region["regionName"] == region]
        
        data_r[val + "_new"] = data_r[val].diff()
        ordered_values = df_region.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
        max_value_diff = ordered_values.quantile(.90)
        
        for data_quant in vals_quantiles:
            fig.add_trace(go.Bar(x=data_quant["jour"], y=data_quant[val], marker=dict(color="grey", opacity=0.1) #rgba(230,230,230,0.5)
                        ),
                      i, j)
        
        fig.add_trace(go.Bar(x=data_r["jour"], y=data_r[val],
                            marker=dict(color = data_r[val + "_new"], coloraxis="coloraxis"), ),
                      i, j)
        
        

        fig.update_xaxes(title_text="", range=["2020-03-15", "2020-05-01"], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=i, col=j)
        fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=1, linecolor='white', row=i, col=j)

        j+=1
        if j == nj+1 or ((i >= 3) & (j == nj)):
            i+=1
            j=1
            
        """if j == nj+1:
            i+=1
            j=1"""

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=15)

    #for annotation in fig['layout']['annotations']: 
            #annotation ['x'] = 0.5
    by_million_title = ""
    by_million_legend = ""
    if "pop" in val:
        by_million_title = "pour 1 million d'habitants, "
        by_million_legend = "pour 1M. d'hab."

    fig.update_layout(
        barmode="overlay",
        margin=dict(
            l=0,
            r=15,
            b=0,
            t=170,
            pad=0
        ),
        bargap=0,
        paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
        plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5 
        coloraxis=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-max_value_diff, cmax=max_value_diff), 
                    coloraxis_colorbar=dict(
                        title="Solde quotidien de<br>pers. {}<br>{}<br> &#8205; ".format(type_ppl, by_million_legend),
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=400,
                        yanchor="bottom", y=0.26, xanchor="left", x=0.85,
                        ticks="outside", tickprefix="  ", ticksuffix=" hosp.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15)),
                      
                    showlegend=False,
    
                     title={
                        'text': "COVID19 : <b>nombre de personnes {}</b><br><sub>{}par ordre décroissant des hospitalisations actuelles - guillaumerozier.fr</sub>".format(type_ppl, by_million_title),
                        'y':0.97,
                        'x':0.5,
                        'xref':"paper",
                         'yref':"container",
                        'xanchor': 'center',
                        'yanchor': 'middle'},
                        titlefont = dict(
                        size=35,
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
                        ),
                            dict(
                            x=0.9,
                            y=0.21,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='25 % des données sont<br>comprises dans la courbe<br>grise la plus foncée,<br><br>50 % dans la deuxième,<br><br>75 % dans la troisième,<br><br>100 % dans la plus claire.',
                            showarrow = False,
                            font=dict(size=16), 
                            opacity=1,
                            align='left'
                        ))
    
    name_fig = "subplots_" + val 
    fig.write_image("images/charts/france/{}.png".format(name_fig), scale=2, width=1300, height=1600)

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


# ## Subplots : départements
# Ce script génère 4 graphiques contenant les graphiques de :
# - nb d'hospitalisés par habitant des départements,
# et ce pour toutes les régions françaises

# In[173]:





# ## Subplots : départements - classé par régions
# Idem précédent mais les départements sont rangés dans leurs régions, et les régions classées par ordre décroissant du nb de personnes

# In[174]:



import numpy as np
for val in ["hosp_deppop"]: #, "hosp", "rea", "rea_pop"
    ni, nj = 12, 9
    i, j = 1, 1

    #df_region[val+"_new"] = df_region[val].diff()
    max_value = df[val].max()
    
    #deps_ordered = df[df['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["departmentName"].values
    #deps_ordered = list(dict.fromkeys(list(deps_ordered)))[:]
    
    
    titles = []
    k=0
    deps_by_reg=[]
    case=1
    for reg in regions_ordered:
        deps_ordered = df[(df['regionName']==reg) & (df['jour'] == dates[-1])].sort_values(by=val, ascending=False)
        
        deps_by_reg += [[deps_ordered['dep'].values, deps_ordered['departmentName'].values]]
        
        for d in range(len(deps_ordered)):
            if case in [80, 89, 98]:
                titles += ["", ""]
                titles += ["" + deps_ordered['dep'].values[d] + " - " + deps_ordered['departmentName'].values[d] + ""]
                case+=3
            else:
                titles += ["" + deps_ordered['dep'].values[d] + " - " + deps_ordered['departmentName'].values[d] + ""]
                case+=1
        k+=1
        
    """for case in range(1, ni * nj - 1):
        if case in [80, 81, 89, 90, 98, 99]:
            titles += [""] 
        else:
            titles += ["<b>" + deps_ordered_nb[k] + "</b> - " + deps_ordered[k]]
            k+=1"""

    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles= titles, vertical_spacing = 0.030, horizontal_spacing = 0.002)
    #&#8681;
    
    df_nonobj = df.select_dtypes(exclude=['object'])
    df_nonobj['jour'] = df['jour']
    
    vals_quantiles=[]
    for q in range(25, 125, 25):
        vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())
    
    type_ppl = "hospitalisées"
    if "rea" in val:
        type_ppl = "en réanimation"
    max_values_diff=[]
        
    
    for reg in tqdm(deps_by_reg):
        for dep in reg[1]:

            data_dep = df[df["departmentName"] == dep]

            data_dep[val + "_new"] = data_dep[val].diff()
            ordered_values = data_dep.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
            max_values_diff += [ordered_values.quantile(.90)]

            for data_quant in vals_quantiles:
                fig.add_trace(go.Bar(x=data_quant["jour"], y=data_quant[val], marker=dict(color="grey", opacity=0.1) #rgba(230,230,230,0.5)
                            ),
                          i, j)


            fig.add_trace(go.Bar(x=data_dep["jour"], y=data_dep[val],
                                marker=dict(color = data_dep[val + "_new"], coloraxis="coloraxis"), ),
                          i, j)

            fig.update_xaxes(title_text="", range=["2020-03-15", "2020-05-01"], gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
            fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j)

            j+=1
            if j == nj+1 or ((i >= 9) & (j >= nj-1)): 
                i+=1
                j=1

    cnt = 0
    reg = 0
    annotations_to_add = ()
    for i in fig['layout']['annotations']:
        if len(i['text']) > 1:
            
            if ((reg==0) & (cnt==0)) or (cnt == len(deps_by_reg[reg][0])):
                if (cnt == len(deps_by_reg[reg][0])):
                    reg +=1
                    cnt = 0
            annotations_to_add += ( dict(         
                            x=i['x'],
                            y=str(float(i['y'])+0.006),
                            xref= 'paper',
                            yref= 'paper',
                            xanchor= 'center',
                            yanchor= 'bottom',
                            align='left',
                            text= "<b>" + regions_ordered[reg] + "</b>",
                            showarrow = False,
                            font=dict(size=11, color = str(colors[reg])), 
                            opacity=1
                        ),)    
            i['font'] = dict(size=11, color = str(colors[reg]))
            i['align'] = 'center'
            cnt+=1
    
        
    #for annotation in fig['layout']['annotations']: 
            #annotation ['x'] = 0.5
    by_million_title = ""
    by_million_legend = ""
    if "pop" in val:
        by_million_title = "pour 100 000 habitants, "
        by_million_legend = "pour 100k hab."
        
    max_value_diff = np.mean(max_values_diff) * 1.7
    fig.update_layout(
        barmode='overlay',
        margin=dict(
            l=0,
            r=15,
            b=0,
            t=160,
            pad=0
        ),
        bargap=0,
        paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
        plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
        coloraxis=dict(colorscale=["green", "#ffc832", "#cf0000"], cmin=-max_value_diff, cmax=max_value_diff), 
                    coloraxis_colorbar=dict(
                        title="Solde quotidien de<br>pers. {}<br>{}<br> &#8205; ".format(type_ppl, by_million_legend),
                        thicknessmode="pixels", thickness=15,
                        lenmode="pixels", len=350,
                        yanchor="bottom", y=0.15, xanchor="left", x=0.87,
                        ticks="outside", tickprefix="  ", ticksuffix=" hosp.",
                        nticks=5,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15)),
                      
                    showlegend=False,
    
                     title={
                        'text': "COVID19 : <b>nombre de personnes {}</b>".format(type_ppl, by_million_title),
                        'y':0.98,
                        'x':0.5,
                        'xref':"paper",
                        'yref':"container",
                        'xanchor': 'center',
                        'yanchor': 'middle'},
                        titlefont = dict(
                            size=50
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
                            font=dict(size=15), 
                            opacity=0.5
                        ),
                            dict(
                            x=0.9,
                            y=0.14,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='25 % des données sont<br>comprises dans la courbe<br>grise la plus foncée,<br><br>50 % dans la deuxième,<br><br>75 % dans la troisième,<br><br>100 % dans la plus claire.',
                            showarrow = False,
                            font=dict(size=16), 
                            opacity=1,
                            align='left'
                        ),
                            dict(
                            x=0.5,
                            y=1.03,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='middle',
                            text='pour 100 000 habitants de chaque département - guillaumerozier.fr',
                            showarrow = False,
                            font=dict(size=30), 
                            opacity=1
                        ),
                                    ) + annotations_to_add
    
    name_fig = "subplots_dep__class-par-reg" + val 
    fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1600, height=2300)

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


# ## Hospitalisations et réanimations (bar charts subplot)

# In[175]:



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

fig.update_xaxes(title_text="", range=["2020-03-15", "2020-05-01"], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=1, col=1)
fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=1, col=1)

fig.update_xaxes(title_text="", range=["2020-03-15", "2020-05-01"], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, nticks=10, linewidth=1, linecolor='white', row=2, col=1)
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
                        text='guillaumerozier.fr - {}'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.8
                    ),)

name_fig = "hosp_rea_bar"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=2, width=1100, height=1200)

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

# In[176]:



df_region_sumj = df_region.groupby('jour').sum().reset_index()
df_region_sumj = pd.melt(df_region_sumj, id_vars=['jour'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['jour'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)
df_bar = df_region_sumj

data = df_bar[df_bar["variable"] == "dc"]
fig = go.Figure(go.Bar(x=data['jour'], y=data['value'], text=data['value'], textposition='auto', name='Décès hosp.', marker_color='#000000', opacity=0.8))

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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
                    showarrow = False
                )]
)

name_fig = "situation_cas"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

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


# <br>
# <br>
# <br>
# <br>
# 
# # Line charts

# ## Décès hospitalisations et réanimations (line chart)

# In[177]:


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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

if show_charts:
    fig.show()
print("> " + name_fig)


# ## Décès cumulés (line chart)

# In[178]:



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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[179]:



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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations

# In[180]:



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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations (entrées - sorties) (line chart)

# In[181]:



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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Admissions en hospitalisation (line chart)

# In[182]:



fig = px.line(x = df_new_region['jour'], y = df_new_region['incid_hosp'], color = df_new_region["regionName"], color_discrete_sequence=colors).update_traces(mode='lines+markers', marker_size=7.5, line=dict(width=2.5))
fig.update_layout(
    title={
                'text': "<b>Nouvelles admissions en hospitalisation</b>",
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
fig.update_yaxes(title="Admissions hospitalisations")

name_fig = "hosp_admissions_journ_line"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)


plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations par région (line chart)

# In[183]:


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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)

plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations : Rhin (line chart)

# In[184]:


df_rhin = df[df["dep"].isin(["67", "68"])]
fig = px.line(x=df_rhin['jour'], y=df_rhin['rea'], color=df_rhin["dep"], labels={'color':'Département'}, color_discrete_sequence=colors).update_traces(mode='lines+markers')

fig.update_layout(
    title={
                'text': "Nombre de <b>patients en réanimation</b> en Ht et Bas Rhin",
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
fig.update_yaxes(title="Nb. de patients en réa. ou soins intensifs")

name_fig = "rea_rhin"
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1100, height=700)
plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Réanimations par département (line chart)

# In[185]:


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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Hospitalisations par département (line chart)

# In[186]:


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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Hospitalisations par habitant / région

# In[187]:


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
if show_charts:
    fig.show()
"""


# <br>
# 
# ## Capacité réanimation (line chart)

# In[188]:



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
fig.write_image("images/charts/france/{}.png".format(name_fig), scale=3, width=1000, height=700)

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


# <br>
# 
# ## Décès cumulés (région)

# In[189]:


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
print("> " + name_fig)
if show_charts:
    fig.show()


# ## Nouveaux décès quotidiens (line chart)

# In[190]:


fig = px.line(x=df_new_region['jour'], y=df_new_region['incid_dc'], color=df_new_region["regionName"], labels={'color':'Région'}, color_discrete_sequence=colors).update_traces(mode='lines+markers')
fig.update_layout(
    title={
                'text': "<b>Nouveaux décès</b> par région",
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
fig.update_yaxes(title="Nb. de décès hosp.")

name_fig = "dc_nouv_line"
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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés par habitant (région)

# In[191]:


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

# In[192]:


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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés par région / 3 derniers jours

# In[193]:



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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Décès cumulés VS. Décès cumulés par habitant / région

# In[194]:


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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Situation des malades / région

# In[195]:


#df_region_sumj = df_region.groupby('regionName').sum().reset_index()
df_region_sumj = df_region[df_region['jour'] == dates[-1]]

df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad', 'rea', 'dc', 'hosp_nonrea'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[196]:


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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# 
# ## Situation des malades par habitant / région

# In[197]:


df_region_sumj = df_region[df_region['jour'] == dates[-1]]
df_region_sumj = pd.melt(df_region_sumj, id_vars=['regionName'], value_vars=['rad_pop', 'rea_pop', 'dc_pop', 'hosp_nonrea_pop'])
df_region_sumj.drop(df_region_sumj[df_region_sumj['regionName'].isin(['Guyane', 'Mayote', 'La Réunion', 'Guadeloupe', 'Martinique'])].index, inplace = True)


# In[198]:


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
                    text='Date : {}. Source : INSEE et CSSE. Auteur : guillaumerozier.fr.'.format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B %Y')),
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
print("> " + name_fig)
if show_charts:
    fig.show()


# <br>
# <br>
# <br>
# <br>
# 
# # Expérimentations (brouillon)

# In[199]:


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

if show_charts:
    fig.show()
"""

