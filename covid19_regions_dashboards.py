#!/usr/bin/env python
# coding: utf-8

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


# In[56]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
from datetime import datetime
from datetime import timedelta
import plotly
import math


# In[6]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[66]:


df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid.groupby(["jour", "regionName"]).sum().reset_index()
regions = list(dict.fromkeys(list(df_regions['regionName'].values))) 
dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")


# In[67]:


def cas_journ(region):
        
    df_incid_reg = df_incid_regions[df_incid_regions["regionName"] == region]
    df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_journ_"+region, [0, df_incid_reg["P"].max()]
    title = "<b>Cas positifs</b> au Covid19 - " + region

    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x = df_incid_reg["jour"],
        y = df_incid_reg_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='rgb(8, 115, 191)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_reg_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = df_incid_reg["jour"],
        y = df_incid_reg["P"],
        name = "",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_reg_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_incid_reg_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            opacity=1,
            ax=-40,
            ay=-70,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    print("> " + name_fig)


# In[68]:


def hosp_journ(region):   
    df_reg = df_regions[df_regions["regionName"] == region]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_journ_"+region
    title = "<b>Personnes hospitalisées</b> pour Covid19 - " + region

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
        y = df_reg["hosp"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(209, 102, 21)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_reg["hosp"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_reg["hosp"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_reg["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    print("> " + name_fig)


# In[69]:


def rea_journ(region):
    df_reg = df_regions[df_regions["regionName"] == region]
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "rea_journ_" + region
    title = "<b>Personnes en réanimation</b> pour Covid19 - " + region

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_reg["rea"],
        name = "Nouveaux décès hosp.",
        marker_color='rgb(201, 4, 4)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(201, 4, 4,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_reg["rea"].values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_reg["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_reg["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %B'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    print("> " + name_fig)


# In[70]:


def dc_journ(region): 
    df_reg = df_regions[df_regions["regionName"] == region]
    dc_new_rolling = df_reg["dc_new"].rolling(window=7).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ_"+region, [0, df_reg["dc_new"].max()]
    title = "<b>Décès hospitaliers quotidiens</b> du Covid19 - " + region

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(0,0,0,0.3)",
        showlegend=False
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
        x = df_reg["jour"],
        y = df_reg["dc_new"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        text='Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "décès quotidiens</b><br>en moyenne<br>du {} au {}.".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            opacity=0.8,
            ax=-50,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image("images/charts/france/departements_dashboards/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

    print("> " + name_fig)


# In[71]:


import cv2

for reg in regions:
    cas_journ(reg)
    hosp_journ(reg)
    rea_journ(reg)
    dc_journ(reg)
    
    
    im1 = cv2.imread('images/charts/france/departements_dashboards/cas_journ_{}.jpeg'.format(reg))
    im2 = cv2.imread('images/charts/france/departements_dashboards/hosp_journ_{}.jpeg'.format(reg))
    im3 = cv2.imread('images/charts/france/departements_dashboards/rea_journ_{}.jpeg'.format(reg))
    im4 = cv2.imread('images/charts/france/departements_dashboards/dc_journ_{}.jpeg'.format(reg))

    im_haut = cv2.hconcat([im1, im2])
    #cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite('images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg'.format(reg), im_totale)


# In[98]:


for reg in regions:
    
    heading = "<!-- wp:heading --><h2 id=\"{}\">{}</h2><!-- /wp:heading -->\n".format(reg, reg)
    string = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/departements_dashboards/dashboard_jour_{}.jpeg\" width=\"100%\"> </a></p>\n".format(reg, reg)
    space = "<!-- wp:spacer {\"height\":50} --><div style=\"height:50px\" aria-hidden=\"true\" class=\"wp-block-spacer\"></div><!-- /wp:spacer -->"
    retourmenu="<a href=\"#Menu\">Retour au menu</a>"
    print(space+retourmenu+heading+string)


# In[92]:


print("<!-- wp:buttons --><div class=\"wp-block-buttons\">\n")
for reg in regions:
    print("""<!-- wp:button {"className":"is-style-outline"} -->
    <div class="wp-block-button is-style-outline">""")
    
    print("<a class=\"wp-block-button__link\" href=\"#{}\">".format(reg))
    
    print("{}</a></div><!-- /wp:button --></div>\n".format(reg))
print("<!-- /wp:buttons -->")

