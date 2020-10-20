#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly
from datetime import datetime


# In[9]:


df_mortalite = pd.read_csv('data/france/deces_quotidiens_departement_csv.csv', sep=";", encoding="'windows-1252'")

df_mortalite_france = df_mortalite[df_mortalite["Zone"] == "France"]
df_mortalite_france.loc[:,"Total_deces_2018_diff"] = df_mortalite_france["Total_deces_2018"].diff().rolling(window=7).mean()
df_mortalite_france.loc[:,"Total_deces_2019_diff"] = df_mortalite_france["Total_deces_2019"].diff().rolling(window=7).mean()
df_mortalite_france.loc[:,"Total_deces_2020_diff"] = df_mortalite_france["Total_deces_2020"].diff().rolling(window=7).mean()


# In[19]:


print(df_mortalite_france.dropna()["Total_deces_2018"].values[-1])
print(df_mortalite_france.dropna()["Total_deces_2019"].values[-1])
print(df_mortalite_france.dropna()["Total_deces_2020"].values[-1])


# In[10]:


#### Construction du graphique
fig = make_subplots(specs=[[{"secondary_y": False}]])

# Ajout R_effectif estimé via les urgences au graph
fig.add_trace(go.Scatter(x = df_mortalite_france["Date_evenement"], y = df_mortalite_france["Total_deces_2018_diff"],
                    mode='lines',
                    line=dict(width=4, color="rgb(96, 178, 219)"),
                    name="Décès 2018",
                    marker_size=4,
                    showlegend=True
                       ))
fig.add_trace(go.Scatter(x = df_mortalite_france["Date_evenement"], y = df_mortalite_france["Total_deces_2019_diff"],
                    mode='lines',
                    line=dict(width=4, color="rgb(11, 131, 191)"),
                    name="Décès 2019",
                    marker_size=4,
                    showlegend=True
                       ))
fig.add_trace(go.Scatter(x = df_mortalite_france["Date_evenement"], y = df_mortalite_france["Total_deces_2020_diff"],
                    mode='lines',
                    line=dict(width=4, color="red"),
                    name="Décès 2020",
                    marker_size=4,
                    showlegend=True
                       ))

# Mise en valeur de la dernière valeur du R_effectif
mortalite_now = df_mortalite_france.dropna()["Total_deces_2020_diff"].values[-1]
fig.add_trace(go.Scatter(x = [df_mortalite_france.dropna()["Date_evenement"].values[-1]], y = [mortalite_now],
                    mode='markers',
                    name="",
                    line=dict(width=4, color="red"),
                    marker_color='red',
                    marker_size=10,
                    showlegend=False
                            ))
# Modification du layout
fig.update_layout(
    margin=dict(
            l=0,
            r=0,
            b=50,
            t=70,
            pad=0
        ),
    legend_orientation="h",
    title={
                'text': "<b>Mortalité en France</b><br><sub>Moyenne mobile de 7 jours pour lisser les irrégularités".format(),
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
    titlefont = dict(
                size=20),
    annotations = [
                dict(
                    x=0.5,
                    y=-0.1,
                    xref='paper',
                    yref='paper',
                    opacity=0.8,
                    text='Date : {}. Source : Santé publique France. Auteur : Guillaume Rozier - covidtracker.fr.'.format(datetime.now().strftime('%d %B %Y')),                    showarrow = False
                )]
                 )
fig.update_xaxes(title="", nticks=10)
fig.update_yaxes(title="")

name_fig = "mortalite"
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

