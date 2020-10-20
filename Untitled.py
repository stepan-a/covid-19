#!/usr/bin/env python
# coding: utf-8

# In[47]:


import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import plotly
import france_data_management as data


# In[22]:


df_capa = pd.read_csv("/Users/guillaumerozier/Downloads/sp-capa-quot-fra-2020-10-18-19h15.csv", sep=";")


# In[41]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[54]:


df_tests_viros = df_tests_viros.groupby(["jour"]).sum().reset_index()
df_tests = df_tests.groupby(["jour"]).sum().reset_index()


# In[53]:


df_tests


# In[56]:


title = "<b>Estimations des cas</b> du Covid19 à partir des décès<br>"
sub = "Hypothèses : taux de mortalité de 0,5 % ; décalage de 21 j. entre cas et décès"

fig = go.Figure()

#estimated_rolling = df_france.diff().rolling(window=7).mean().shift(-21).dropna()/0.005
#confirmed_rolling = df_france.diff().rolling(window=7, center=True).mean()

fig.add_trace(go.Scatter(
    x = df_tests_viros["jour"],
    y = df_tests_viros["T"],
    name = "Est.",
    marker_color='black',
    line_width=6,
    opacity=0.6,
    fill='tozeroy',
    fillcolor="rgba(0,0,0,0.3)",
    showlegend=False
))

fig.add_trace(go.Scatter(
    x = df_tests["jour"],
    y = df_tests["nb_test"],
    name = "Conf",
    marker_color='red',
    line_width=4,
    opacity=0.8,
    fill='tozeroy',
    fillcolor="rgba(201, 4, 4,0.3)",
    showlegend=False
))

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
                size=30),
    xaxis=dict(
            title='',
            tickformat='%d/%m'),

                 )

fig.write_image("images/charts/france/{}.jpeg".format("test_asuppr"), scale=2, width=900, height=600)

#plotly.offline.plot(fig, filename = 'images/html_exports/france/{}.html'.format(t), auto_open=False)
print("> " + "name_fig")

