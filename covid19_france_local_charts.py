#!/usr/bin/env python
# coding: utf-8

# In[1]:


import france_data_management as data
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tqdm import tqdm
from datetime import datetime
from datetime import timedelta
import plotly
import plotly.express as px
import math
import json
import numpy as np
import locale

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet


# ## Data Import

# In[43]:


df, df_confirmed, dates, df_new, df_tests, _, df_sursaud, df_incid  = data.import_data()

df_incid["incidence"] = df_incid["P"]/df_incid["pop"]*100000
deps_incid = list(dict.fromkeys(list(df_incid['dep'].values))) 
deps_incid_name = list(dict.fromkeys(list(df_incid['departmentName'].values))) 

df = df.sort_values(by=['dep', 'jour'], axis=0).reset_index()
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")

df_sursaud['indic_clr'] = ["white" for i in range(len(df_sursaud))]

dates_sursaud = list(dict.fromkeys(list(df_sursaud['date_de_passage'].values))) 
dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 

df_region = df.groupby(['regionName', 'jour', 'regionPopulation']).sum().reset_index()
df_region["hosp_regpop"] = df_region["hosp"] / df_region["regionPopulation"]*1000000 
df_region["rea_regpop"] = df_region["rea"] / df_region["regionPopulation"]*1000000 
df_region["dc_new_regpop"] = df_region["dc_new"] / df_region["regionPopulation"]*1000000 
df_region["dc_new_regpop_rolling7"] = df_region["dc_new_regpop"].rolling(window=7, center=True).mean()
df_region["dc_new_rolling7"] = df_region["dc_new"].rolling(window=7).mean()

df_region["hosp_regpop_rolling7"] = df_region["hosp_regpop"].rolling(window=4, center=True).mean()
df_region["rea_regpop_rolling7"] = df_region["rea_regpop"].rolling(window=4, center=True).mean()

df["dc_new_deppop"] = df["dc_new"] / df["departmentPopulation"]*1000000 
df["dc_new_deppop_rolling7"] = df["dc_new_deppop"].rolling(window=7).mean()

df_tests_tot = df_tests.groupby(['jour']).sum().reset_index()

df_new_region = df_new.groupby(['regionName', 'jour']).sum().reset_index()
df_france = df.groupby('jour').sum().reset_index()

regions = list(dict.fromkeys(list(df['regionName'].values))) 
codes_reg = list(dict.fromkeys(list(df['code'].values))) 
lits_reas = pd.read_csv('data/france/lits_rea.csv', sep=",")

df_incid_region = df_incid.groupby(["jour", "regionName"]).sum().reset_index()
df_sursaud_region = df_sursaud.groupby(["date_de_passage", "regionName"]).sum().reset_index()


# In[44]:


df_sursaud[df_sursaud["dep"] == "95"]


# In[3]:


with open('data/france/dep.geojson') as response:
    dep_geojson = json.load(response)
    
with open('data/france/regions.geojson') as response:
    reg_geojson = json.load(response)
    
def build_map(data_df, img_folder, date = dates_sursaud[-1], subtitle="", legend_str="", type_data="dep", date_str ="extract_date", dep_str = "departement", color_str = 'indic_synthese', legend_title="legend_title", title="title"):    
    date = max(list(dict.fromkeys(list(data_df[date_str].values))))
    data_df = data_df[data_df[date_str] == date]
    
    if type_data == "dep":
        geojson_data = dep_geojson
    else:
        geojson_data = reg_geojson
        
    fig = px.choropleth(geojson = geojson_data, 
                        locations = data_df[dep_str], 
                        featureidkey="properties.code",
                        color = data_df[color_str],
                        scope='europe',
                        labels={"color":"Couleur"},
                        #legend_title = "couleur",
                        color_discrete_map = {"green":"green", "orange":"orange", "red":"red"}
                        #category_orders = {"indic_synthese" :["vert", "orange", "rouge"]}
                              )
    date_title = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')

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
                text='Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr',
                showarrow = False
            ),
            dict(
                x=1,
                y=0.4,
                xref='paper',
                yref='paper',
                xanchor = 'right',
                align = "center",
                text = legend_str,
                showarrow = False,
                font=dict(
                    size=20
                        )
            ),

            dict(
                x=0.55,
                y=0.94,
                xref='paper',
                yref='paper',
                text= "{}, {}".format(subtitle, date_title),
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
    fig.write_image(img_folder.format("latest"), scale=2, width=1200, height=800)
    fig.write_image(img_folder.format(date), scale=2, width=1200, height=800)


# ## Subplots : régions
# Ce script génère 4 graphiques contenant les graphiques de :
# - nb d'hospitalisés,
# - nb d'hospitalisés par habitant des régions,
# - nb de réanimations,
# - nb de réanimations par habitant des régions,
# et ce pour toutes les régions françaises

# In[4]:


"""
for val in ["hosp_regpop", "rea_regpop", "dc_new_regpop_rolling7"]: #
    ni, nj = 5, 4
    i, j = 1, 1

    df_region[val+"_new"] = df_region[val].diff()
    max_value = df_region[val].max()
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles=[ "<b>"+ str(r) +"</b>" for r in (regions_ordered[:11] + [""] + regions_ordered[11:14]+[""]+regions_ordered[14:])], vertical_spacing = 0.06, horizontal_spacing = 0.01)
    #&#8681;
    
    sub = "<sub>{}par ordre décroissant des hospitalisations actuelles - guillaumerozier.fr</sub>"
    type_ppl = "hospitalisées"
    
    if "rea" in val:
        type_ppl = "en réanimation"
        
    if "dc" in val:
        type_ppl = "décédées"
        sub = "<sub>par million d'habitants, moyenne mobile sur 7 jours - guillaumerozier.fr</sub>"
        
    df_nonobj = df_region.select_dtypes(exclude=['object'])
    df_nonobj.loc[:,'jour'] = df_region.loc[:, 'jour']
    
    vals_quantiles=[]
    for q in range(25, 125, 25):
        vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())
        
    for region in regions_ordered:
        data_r = df_region[df_region["regionName"] == region]
        
        #data_r[val + "_new"] = data_r[val].diff()
        data_r.loc[:, val + "_new"] = data_r.loc[:, val].diff()
        ordered_values = df_region.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
        max_value_diff = ordered_values.quantile(.90)
        
        for data_quant in vals_quantiles:
            fig.add_trace(go.Bar(x=data_quant["jour"], y=data_quant[val], marker=dict(color="grey", opacity=0.1) #rgba(230,230,230,0.5)
                        ),
                      i, j)
        
        fig.add_trace(go.Bar(x=data_r["jour"], y=data_r[val].rolling(window=3, center=True).mean(),
                            marker=dict(color = data_r[val + "_new"].rolling(window=3, center=True).mean(), coloraxis="coloraxis"), ),
                      i, j)
        
        rangemin = "2020-03-15"
        if "dc" in val:
            rangemin = "2020-03-25"
        fig.update_xaxes(title_text="", range=[rangemin, last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, linewidth=1, linecolor='white', row=i, col=j)
        fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=1, linecolor='white', row=i, col=j)

        j+=1
        if j == nj+1 or ((i >= 3) & (j == nj) & (i<5)):
            i+=1
            j=1

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=15)

    #for annotation in fig['layout']['annotations']: 
            #annotation ['x'] = 0.5
    by_million_title = ""
    by_million_legend = ""
    if "pop" in val:
        by_million_title = "pour 1 million d'habitants, "
        by_million_legend = "pour 1M. d'hab."
    
    fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/covidtracker_logo.png",
            xref="paper", yref="paper",
            x=1, y=1.07,
            sizex=0.06, sizey=0.06, opacity=0.9,
            xanchor="right", yanchor="bottom"
            )
) 

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
                        tickfont=dict(size=12),
                        titlefont=dict(size=15)),
                      
                    showlegend=False,
    
                     title={
                        'text': ("COVID19 : <b>nombre de personnes {}</b><br>"+sub).format(type_ppl, by_million_title),
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
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1300, height=1600)

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


    #fig.show()"""


# In[5]:



for val in ["hosp_regpop", "rea_regpop", "dc_new_regpop_rolling7"]: #
    ni, nj = 5, 4
    i, j = 1, 1

    df_region[val+"_new"] = df_region[val].diff()
    max_value = df_region[val].max()
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles=[ "<b>"+ str(r) +"</b>" for r in (regions_ordered[:11] + [""] + regions_ordered[11:14]+[""]+regions_ordered[14:])], vertical_spacing = 0.06, horizontal_spacing = 0.01)
    #&#8681;
    
    sub = "<sub>{}par ordre décroissant des hospitalisations actuelles - guillaumerozier.fr</sub>"
    type_ppl = "hospitalisées"
    
    if "rea" in val:
        type_ppl = "en réanimation"
        
    if "dc" in val:
        type_ppl = "décédées"
        sub = "<sub>par million d'habitants, moyenne mobile sur 7 jours - guillaumerozier.fr</sub>"
        
    df_nonobj = df_region.select_dtypes(exclude=['object'])
    df_nonobj.loc[:,'jour'] = df_region.loc[:,'jour']
    
    vals_quantiles=[]
    for q in range(25, 125, 25):
        vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())
        
    for region in regions_ordered:
        data_r = df_region[df_region["regionName"] == region]
        
        data_r.loc[:,val + "_new"] = data_r.loc[:,val].diff()
        ordered_values = df_region.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
        max_value_diff = ordered_values.quantile(.90)
        
        for data_quant in vals_quantiles:
            fig.add_trace(go.Bar(x=data_quant["jour"], y=data_quant[val], marker=dict(color="grey", opacity=0.1) #rgba(230,230,230,0.5)
                        ),
                      i, j)
        
        fig.add_trace(go.Bar(x=data_r["jour"], y=data_r[val],
                            marker=dict(color = data_r[val + "_new"], coloraxis="coloraxis"), ),
                      i, j)
        
        rangemin = "2020-03-15"
        if "dc" in val:
            rangemin = "2020-03-25"
        fig.update_xaxes(title_text="", range=[rangemin, last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, linewidth=1, linecolor='white', row=i, col=j)
        fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=1, linecolor='white', row=i, col=j)

        j+=1
        if j == nj+1 or ((i >= 3) & (j == nj) & (i<5)):
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
                        yanchor="bottom", y=0.30, xanchor="left", x=0.85,
                        ticks="outside", tickprefix="  ", ticksuffix=" hosp.",
                        nticks=15,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15)),
                      
                    showlegend=False,
    
                     title={
                        'text': ("COVID19 : <b>nombre de personnes {}</b><br>"+sub).format(type_ppl, by_million_title),
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
                            y=0.27,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='25 % des données sont comprises<br>dans la courbe grise la plus foncée,<br>50 % dans la deuxième, 75 % dans<br>la troisième, 100 % dans la plus claire.',
                            showarrow = False,
                            font=dict(size=15), 
                            opacity=1,
                            align='left'
                        ))
    
    name_fig = "subplots_" + val 
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=1300, height=1600)

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


# In[31]:


ni, nj = 5, 4
i, j = 1, 1
std_gauss= 3
wind = 12
delai = 5

regions_ordered = list(dict.fromkeys(list(df_incid_region.sort_values(by=["regionName"], ascending=True)["regionName"].values)))[:]

fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles=[ "<b>"+ str(r) +"</b>" for r in (regions_ordered)], vertical_spacing = 0.06, horizontal_spacing = 0.01)
#&#8681;

sub = "<sub>{} - covidtracker.fr</sub>"

for region in regions_ordered:
    
    df_incid_reg = df_incid_region[df_incid_region["regionName"] == region]
    print(region)
    print(df_incid_reg["regionCode"])
    df_sursaud_reg = df_sursaud_region[df_sursaud_region["regionName"] == region]
    nbre_pass = df_sursaud_reg["nbre_pass_corona"]
    
    reffectif_tests = (df_incid_reg['T'].rolling(window= wind, win_type="gaussian").sum(std = std_gauss) / df_incid_reg['T'].rolling(window = wind, win_type="gaussian").sum(std = std_gauss).shift(delai) ).rolling(window=7).mean()
    reffectif_urgences = (nbre_pass.rolling(window= wind, win_type="gaussian").sum(std = std_gauss) / nbre_pass.rolling(window = wind, win_type="gaussian").sum(std = std_gauss).shift(delai) ).rolling(window=7).mean()
    reffectif_mean = pd.DataFrame(reffectif_tests, reffectif_urgences).mean(axis=1, skipna=False)
    
    fig.add_trace(go.Scatter(x = df_incid_reg["jour"], y = reffectif_tests,
                    mode='lines',
                    line=dict(width=2, color="rgba(108, 212, 141, 0.9)"),
                    name="À partir des données des tests PCR",
                    marker_size=5,
                    showlegend=True
                         ),
                 i, j)
    
    fig.add_trace(go.Scatter(x = df_sursaud_reg["date_de_passage"], y = reffectif_urgences,
                    mode='lines',
                    line=dict(width=2, color="rgba(96, 178, 219, 0.9)"),
                    name="À partir des données urgences",
                    marker_size=5,
                    showlegend=True
                         ),
                 i, j)
    
    """fig.add_trace(go.Scatter(x = df_sursaud_reg["date_de_passage"], y = reffectif_mean,
                    mode='lines',
                    line=dict(width=2, color="rgba(96, 178, 219, 0.9)"),
                    name="À partir des données urgences",
                    marker_size=5,
                    showlegend=True
                         ),
                 i, j)"""

    fig.update_xaxes(title_text="", range=["2020-03-17", last_day_plot], gridcolor='white', ticks="inside", tickformat='%d/%m', tickangle=0, linewidth=1, linecolor='white', row=i, col=j)
    fig.update_yaxes(title_text="", gridcolor='white', linewidth=1, linecolor='white', row=i, col=j)

    j+=1
    if j == nj+1:
        i+=1
        j=1

for i in fig['layout']['annotations']:
    i['font'] = dict(size=15)

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
    plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5 ,

    showlegend=False,

    title={
            'text': "COVID19 : <b>R_effectif</b><br>".format(),
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
                    ),)

name_fig = "subplots_reffectif" 
fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=1300, height=1600)

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


# In[37]:


df_sursaud_region[df_sursaud_region["regionCode"] == 160]


# ## Subplots : départements
# Ce script génère 4 graphiques contenant les graphiques de :
# - nb d'hospitalisés par habitant des départements,
# et ce pour toutes les régions françaises

# In[6]:


"""
import numpy as np
try:
    for val in ["dc_new_deppop_rolling7", "hosp_deppop"]: #, "hosp", "rea", "rea_pop"
        ni, nj = 12, 9
        i, j = 1, 1

        #df_region[val+"_new"] = df_region[val].diff()
        max_value = df[val].max()

        #deps_ordered = df[df['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["departmentName"].values
        #deps_ordered = list(dict.fromkeys(list(deps_ordered)))[:]
        deps_ordered = np.array(list(dict.fromkeys(list(df["departmentName"].values)))[:])
        deps_ordered_nb = np.array(list(dict.fromkeys(list(df["dep"].values)))[:])

        deps_ordered_nb = np.char.replace(deps_ordered_nb, "2A", "200")
        deps_ordered_nb = np.char.replace(deps_ordered_nb, "2B", "201")

        ind_deps = np.argsort(deps_ordered_nb.astype(int))

        deps_ordered_nb = deps_ordered_nb[ind_deps]
        deps_ordered = deps_ordered[ind_deps]

        deps_ordered_nb = deps_ordered_nb.astype(str)

        deps_ordered_nb = np.char.replace(deps_ordered_nb, "200", "2A")
        deps_ordered_nb = np.char.replace(deps_ordered_nb, "201", "2B")

        titles = []
        k=0
        for case in range(1, 109):
            if case in [80, 81, 89, 90, 98, 99, 108]:
                titles += [""] 
            else:
                titles += ["<b>" + deps_ordered_nb[k] + "</b> - " + deps_ordered[k]]
                k+=1

        fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles= titles, vertical_spacing = 0.025, horizontal_spacing = 0.002)
        #&#8681;

        df_nonobj = df.select_dtypes(exclude=['object'])
        df_nonobj.loc[:, 'jour'] = df.loc[:, 'jour']

        vals_quantiles=[]
        for q in range(25, 125, 25):
            vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())

        type_ppl = "hospitalisées"
        if "rea" in val:
            type_ppl = "en réanimation"
        if "dc" in val:
            type_ppl = "décédées"
        max_values_diff=[]


        for dep in tqdm(deps_ordered):
            data_dep = df[df["departmentName"] == dep]

            data_dep.loc[:, val + "_new"] = data_dep.loc[:, val].diff()
            ordered_values = data_dep.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
            max_values_diff += [ordered_values.quantile(.90)]

            for data_quant in vals_quantiles:
                fig.add_trace(go.Bar(x=data_quant["jour"], y=data_quant[val], marker=dict(color="grey", opacity=0.1) #rgba(230,230,230,0.5)
                            ),
                          i, j)


            fig.add_trace(go.Bar(x=data_dep["jour"], y=data_dep[val],
                                marker=dict(color = data_dep[val + "_new"], coloraxis="coloraxis"), ),
                          i, j)

            fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
            fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j)

            j+=1
            if j == nj+1 or ((i >= 9) & (j >= nj-1) & (i<12)): 
                i+=1
                j=1

            """if j == nj+1:
                i+=1
                j=1"""
        cnt=0
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=14, color = str(colors[regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] )]))
            #print(regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] ))
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
                            yanchor="bottom", y=0.14, xanchor="left", x=0.87,
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
                                size=45
                            )
        )

        fig["layout"]["annotations"] += ( dict(
                                x=0.95,
                                y=0.04,
                                xref='paper',
                                yref='paper',
                                xanchor='center',
                                yanchor='top',
                                text='Source :<br>Santé Publique<br>France',
                                showarrow = False,
                                font=dict(size=15), 
                                opacity=0.5
                            ),
                                dict(
                                x=0.9,
                                y=0.13,
                                xref='paper',
                                yref='paper',
                                xanchor='center',
                                yanchor='top',
                                text='25 % des données sont comprises<br>dans la courbe grise la plus foncée,<br>50 % dans la deuxième, 75 % dans<br>la troisième, 100 % dans la plus claire.',
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
                                        )

        name_fig = "subplots_dep_" + val 
        fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1600, height=2300)

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
except:
    print("ERROR 1")"""


# In[7]:



import numpy as np
ni, nj = 12, 9
i, j = 1, 1

#df_region[val+"_new"] = df_region[val].diff()
max_value = df_incid["incidence"].max()

titles = []
k=0
for case in range(1, 102):
    titles += ["<b>" + deps_incid[k] + "</b><br>" + deps_incid_name[k]]
    k+=1

fig = make_subplots(rows=ni, cols=nj, shared_yaxes=False, subplot_titles= titles, vertical_spacing = 0.025, horizontal_spacing = 0.02, specs=[ [{"secondary_y": True} for i in range(nj)] for j in range(ni)])
#&#8681;

#max_values=[]
for dep in tqdm(deps_incid):
    data_dep = df_incid[df_incid["dep"] == dep]
    data_dep["incid_rolling"] = data_dep["incidence"].rolling(window=7, center=True).mean()
    
    data_dep["tot"] = (data_dep["T"]/data_dep["pop"]*100000)
    data_dep["tot_rolling"] = data_dep["tot"].rolling(window=7, center=True).mean()
    
    data_dep["taux"] = data_dep["incidence"]/data_dep["tot"]*100
    data_dep["taux_rolling"] = data_dep["taux"].rolling(window=7, center=True).mean()
    
    #max_values += data_dep["tot_rolling"].max()
    
    if data_dep["taux"].values[-1] > 5:
        clr = "red"
    elif data_dep["taux"].values[-1] > 1:
        clr = "darkorange"
    else:
        clr = "green"
    
    fig.add_trace(go.Bar(x = data_dep["jour"].values[:-1], y = data_dep["incid_rolling"], marker_color='rgba(252, 19, 3, 0.3)'),
                  i, j, secondary_y=False)
    fig.add_trace(go.Bar(x = data_dep['jour'], y = data_dep["tot_rolling"], name = "Nombre de tests réalisés", showlegend=False, marker_color='rgba(186, 186, 186, 0.3)'),
                  i, j, secondary_y=False)
    fig.add_trace(go.Scatter(x = data_dep['jour'], y = data_dep["taux_rolling"], name = "Taux de tests positifs", showlegend=False, marker_opacity=0, line_width = 4, marker_color= clr),
                  i, j, secondary_y=True)
    #fig.add_trace(go.Scatter(x = [data_dep["jour"].values[-2]], y = [data_dep[data_dep["jour"] == data_dep["jour"].values[-2]]["incid_rolling"].values[-1]], line_color=clr, mode="markers", marker_size=15, marker_color=clr),
                 # i, j, secondary_y=False)
    

    fig.update_xaxes(title_text="", range=["2020-05-18", data_dep["jour"].values[-1]],gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
    #fig.update_yaxes(title_text="", range=[0, 5], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j, secondary_y=True)
    fig.update_yaxes(title_text="", range=[0, 2.5], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j, secondary_y=False, type="log")
    fig.update_yaxes(title_text="", range=[0, 15], gridcolor='white', linewidth=0, linecolor='white', ticksuffix="%", tickfont=dict(size=7, color=clr), nticks=8, row=i, col=j, secondary_y=True)

    #, range=[0, max_value]
    
    j+=1
    if j == nj+1: 
        i+=1
        j=1

cnt=0
#shapes = []
for i in fig['layout']['annotations']:
    #i['font'] = dict(size=14, color = str(colors[regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] )]))
    i['y'] = i['y'] - 0.02
    
    xref = "x"+str(cnt+1)
    yref = "y"+str(cnt+1)
    #shapes += [{'type': 'line', 'x0': "2020-05-18", 'y0': df_incid["incidence"].mean(), 'x1': data_dep["jour"].values[-1], 'y1': df_incid["incidence"].mean()+1, 'xref': xref, 'yref': yref, 'fillcolor': "black", 'layer' : "above", 'line_width':0, 'opacity' : 1}]
    cnt+=1
    
#fig['layout'].update(shapes=shapes)

max_value_diff = np.mean(max_values_diff) * 1.7
fig.update_layout(
    barmode="stack",
    bargap=0,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=30,
        pad=0
    ),
    paper_bgcolor='#fffdf5',#fcf8ed #faf9ed
    plot_bgcolor='#f5f0e4',#f5f0e4 fcf8ed f0e8d5
    showlegend=False,

    title={
                    'text': "",
                    'y':0.98,
                    'x':0.5,
                    'xref':"paper",
                    'yref':"container",
                    'xanchor': 'center',
                    'yanchor': 'middle'},
                    titlefont = dict(
                        size=45
                    )
)

fig["layout"]["annotations"] += ( dict(
                        x=0.95,
                        y=0.04,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='top',
                        text='',
                        showarrow = False,
                        font=dict(size=15), 
                        opacity=0.5
                    ),
                        dict(
                        x=0.2,
                        y=0.04,
                        xref='paper',
                        yref='paper',
                        xanchor='left',
                        yanchor='top',
                        text="",
                        #text='25 % des données sont comprises<br>dans la courbe grise la plus foncée,<br>50 % dans la deuxième, 75 % dans<br>la troisième, 100 % dans la plus claire.',
                        showarrow = False,
                        font=dict(size=16), 
                        opacity=1,
                        align='left'
                    ),
                        dict(
                        x=0,
                        y=1.03,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        yanchor='middle',
                        text='',
                        showarrow = False,
                        font=dict(size=30), 
                        opacity=1
                    ),
                                )


name_fig = "subplots_dep_incidence"
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


#fig.show()


# ## Subplots : départements - classé par régions
# Idem précédent mais les départements sont rangés dans leurs régions, et les régions classées par ordre décroissant du nb de personnes

# In[8]:


"""
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
            if case in [80, 89, 98, 99, 108]:
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
    df_nonobj.loc[:,'jour'] = df.loc[:,'jour']
    
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

            data_dep.loc[:,val + "_new"] = data_dep.loc[:,val].diff()
            ordered_values = data_dep.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
            max_values_diff += [ordered_values.quantile(.90)]

            for data_quant in vals_quantiles:
                fig.add_trace(go.Bar(x=data_quant["jour"], y=data_quant[val], marker=dict(color="grey", opacity=0.1) #rgba(230,230,230,0.5)
                            ),
                          i, j)


            fig.add_trace(go.Bar(x=data_dep["jour"], y=data_dep[val],
                                marker=dict(color = data_dep[val + "_new"], coloraxis="coloraxis"), ),
                          i, j)

            fig.update_xaxes(title_text="", range=["2020-03-15", last_day_plot], gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
            fig.update_yaxes(title_text="", range=[0, max_value], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j)

            j+=1
            if j == nj+1 or ((i >= 9) & (j >= nj-1) & (i < 12)): 
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
                        yanchor="bottom", y=0.14, xanchor="left", x=0.87,
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
                            x=0.95,
                            y=0.04,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='Source :<br>Santé Publique<br>France',
                            showarrow = False,
                            font=dict(size=15), 
                            opacity=0.5
                        ),
                            dict(
                            x=0.9,
                            y=0.13,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='25 % des données sont comprises<br>dans la courbe grise la plus foncée,<br>50 % dans la deuxième, 75 % dans<br>la troisième, 100 % dans la plus claire.',
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
    
    fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/covidtracker_logo.png",
            xref="paper", yref="paper",
            x=1, y=1.02,
            sizex=0.08, sizey=0.08,
            xanchor="right", yanchor="bottom"
            )
) 
    
    name_fig = "subplots_dep__class-par-reg" + val 
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=2, width=1600, height=2300)

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


    #fig.show()"""


# In[9]:


#TODO A CORRIGER
"""
for val in ["hosp_deppop"]: #, "hosp", "rea", "rea_pop"
    ni, nj = 13, 8
    i, j = 1, 1
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    #df_region[val+"_new"] = df_region[val].diff()
    max_value = df_sursaud["taux_covid"].max()*100
    
    #deps_ordered = df[df['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["departmentName"].values
    #deps_ordered = list(dict.fromkeys(list(deps_ordered)))[:]
    deps_ordered = np.array(list(dict.fromkeys(list(df["departmentName"].values)))[:])
    deps_ordered_nb = np.array(list(dict.fromkeys(list(df["dep"].values)))[:])
    
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "2A", "200")
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "2B", "201")
    
    ind_deps = np.argsort(deps_ordered_nb.astype(int))
    
    deps_ordered_nb = deps_ordered_nb[ind_deps]
    deps_ordered = deps_ordered[ind_deps]
    
    deps_ordered_nb = deps_ordered_nb.astype(str)
    
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "200", "2A")
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "201", "2B")

    
    titles = []
    k=0
    for case in range(1, len(deps_ordered_nb)+1):
        #if case in [80, 81, 89, 90, 98, 99]:
         #   titles += [""] 
        #else:
        titles += ["<b>" + deps_ordered_nb[k] + "</b> - " + deps_ordered[k] + ""] #&#9661; 
        k+=1

    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles= titles, vertical_spacing = 0.025, horizontal_spacing = 0.005) #specs=[ [{"secondary_y": True} for i in range(nj)] for i in range(ni)]
    #&#8681;
    
    df_nonobj = df.select_dtypes(exclude=['object'])
    df_nonobj.loc[:,'jour'] = df.loc[:,'jour']
    
    vals_quantiles=[]
    for q in range(25, 125, 25):
        vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())
    
    type_ppl = "hospitalisées"
    if "rea" in val:
        type_ppl = "en réanimation"
    max_values_diff=[]
        
    clrs_dep = []
    current_values = [[], []]
    for dep in tqdm(deps_ordered_nb):
        data_dep = df[df["departmentName"] == dep]
        
        data_dep[val + "_new"] = data_dep[val].diff()
        ordered_values = data_dep.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
        max_values_diff += [ordered_values.quantile(.90)]
                
        df_sursaud_dep = df_sursaud[df_sursaud["dep"] == dep]
        print(dep)
        values_y = (df_sursaud_dep["taux_covid"]*100).fillna(0)
        clrs=[]
        for tx in values_y.values:
            if tx < 6:
                clrs += ["green"]
            elif tx < 10:
                clrs += ["orange"]
            else:
                clrs += ["red"]
        
        current_values[0].append(values_y.values[-1])
        current_values[1].append(clrs[-1])
            
        mean_last7 = values_y[-7:].mean()
        max_last7 = values_y[-14:].max()
        
        if mean_last7 < 6:
            clrs_dep += [["green", max_last7]]
        elif mean_last7 < 10:
            clrs_dep += [["orange", max_last7]]
        else:
            clrs_dep += [["red", max_last7]]
        
        df_sursaud.loc[(df_sursaud["dep"] == dep) & (df_sursaud["date_de_passage"] == dates_sursaud[-1]), "indic1_clr"] = clrs_dep[-1][0]
            
        fig.add_trace(go.Bar(x = dates_sursaud, y = values_y,
                            marker_color=clrs),
                      i, j)
        #fig.add_trace(go.Scatter(x = df_sursaud_dep["date_de_passage"], y = df_sursaud_dep["nbre_pass_tot"],
         #                   marker_color="Black"),
          #            i, j, secondary_y=True,)
        #fig.add_trace(go.Scatter(x = df_sursaud_dep["date_de_passage"], y = df_sursaud_dep["nbre_pass_corona"],
         #                   marker_color="Blue"),
          #            i, j, secondary_y=True,)
        
        fig.update_xaxes(title_text="", range=["2020-04-25", last_day_plot], gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
        fig.update_yaxes(title_text="", range=[0, 25], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j)
        #fig.update_yaxes(title_text="", range=[0, 300], row=i, col=j, secondary_y=True)


        j+=1
        if j == nj+1: #or ((i >= 9) & (j >= nj-1)) 
            i+=1
            j=1

    cnt=0
    shapes=[]
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=15, color = clrs_dep[cnt][0])
        
        if clrs_dep[cnt][1] <= 20:
            i['y'] = i['y'] - 0.011
            
        if clrs_dep[cnt][1] <= 14:
            i['y'] = i['y'] - 0.016
            
        xref = "x"+str(cnt+1)
        yref = "y"+str(cnt+1)
        shapes += [{'type': 'rect', 'x0': dates_sursaud[-7], 'y0': 0, 'x1': dates_sursaud[-1], 'y1': 100, 'xref': xref, 'yref': yref, 'fillcolor': clrs_dep[cnt][0], 'layer' : "below", 'line_width':0, 'opacity' : 0.1}]

        cnt+=1
    
    #shapes = []
    #{'type': 'rect', 'x0': "2020-05-05", 'y0': 0, 'x1': "2020-05-12", 'y1': 100, 'xref': 'x1', 'yref': 'y1', 'fillcolor':"Green", 'layer' : "below", 'line_width':0, 'opacity' : 0.5}
    
    fig['layout'].update(shapes=shapes)
    
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
            t=140,
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
                        yanchor="bottom", y=0.14, xanchor="left", x=0.87,
                        ticks="outside", tickprefix="  ", ticksuffix=" hosp.",
                        nticks=5,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15)),
                      
                    showlegend=False,
    
                     title={
                        'text': "<b>Circulation du virus</b>",
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
    
    annot=()
    cnt=1
    for dep in deps_ordered_nb:
        annot += (dict(
            x = dates_sursaud[-1], y = current_values[0][cnt-1], # annotation point
            xref='x'+str(cnt), 
            yref='y'+str(cnt),
            text="<b>{}</b> % ".format(math.trunc(round(current_values[0][cnt-1]))),
            xshift=0,
            yshift=3,
            align='center',
            xanchor="right",
            font=dict(
                color=current_values[1][cnt-1],
                size=10
                ),
            ax = 0,
            ay = -20,
            arrowcolor=current_values[1][cnt-1],
            arrowsize=1,
            arrowwidth=1,
            arrowhead=4
        ),)
        cnt+=1
        
    fig["layout"]["annotations"] += annot + ( 
                        dict(
                            x=0.82,
                            y=0.05,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text="La moyenne des 7 deniers jours est considérée pour déterminer la<br>couleur d'un département. Couleurs : rouge (> 10 %), orange (6 à 10%),<br>vert (< 6%).",
                            showarrow = False,
                            font=dict(size=16), 
                            opacity=1,
                            align='left'
                        ),
                        dict(
                            x=0.82,
                            y=0.015,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='Source : Santé Publique France',
                            showarrow = False,
                            font=dict(size=15), 
                            opacity=0.5
                        ),
                            
                            dict(
                            x=0.5,
                            y=1.02,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='middle',
                            text='taux de suspicion Covid aux urgences - guillaumerozier.fr',
                            showarrow = False,
                            font=dict(size=30), 
                            opacity=1
                        ),
                                    )
    
    name_fig = "subplots_deconf_indic1"
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=1600, height=2300)

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


    #fig.show()"""


# In[10]:


#TODO A CORRIGER
"""build_map(df_sursaud, date_str="date_de_passage", legend_str="Rouge : > 10%<br>Orange : 6 à 10%<br>Vert : < 10%", dep_str="dep", color_str="indic1_clr", img_folder="images/charts/france/indic1/{}.png", title="Indicateur 1 : circulation du virus (par département)", subtitle="taux de suspicion Covid19 aux urgences")"""


# In[11]:


"""
dta = df_sursaud[df_sursaud["dep"] == "18"]
fig = go.Figure()
clrs = ["black"] * len(dta["taux_covid"])
fig.add_trace(go.Bar(x = dta["date_de_passage"], y = dta["taux_covid"]*100, marker_color=clrs))
#fig.update_xaxes(range=["2020-04-15", "2020-05-12"])
fig.show()"""


# In[12]:



for val in ["hosp_deppop"]: #, "hosp", "rea", "rea_pop"
    ni, nj = 13, 8
    i, j = 1, 1
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    #df_region[val+"_new"] = df_region[val].diff()
    max_value = 100
    
    #deps_ordered = df[df['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["departmentName"].values
    #deps_ordered = list(dict.fromkeys(list(deps_ordered)))[:]
    deps_ordered = np.array(list(dict.fromkeys(list(df["departmentName"].values)))[:])
    deps_ordered_nb = np.array(list(dict.fromkeys(list(df["dep"].values)))[:])
    
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "2A", "200")
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "2B", "201")
    
    ind_deps = np.argsort(deps_ordered_nb.astype(int))
    
    deps_ordered_nb = deps_ordered_nb[ind_deps]
    deps_ordered = deps_ordered[ind_deps]
    
    deps_ordered_nb = deps_ordered_nb.astype(str)
    
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "200", "2A")
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "201", "2B")
    
    titles = []
    k=0
    for case in range(1, len(deps_ordered_nb)+1):
        
        titles += ["<b>" + deps_ordered_nb[k] + "</b> - " + deps_ordered[k] + ""] #&#9661; 
        k+=1

    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles= titles, vertical_spacing = 0.025, horizontal_spacing = 0.002)
    #&#8681;
    
    df_nonobj = df.select_dtypes(exclude=['object'])
    df_nonobj.loc[:,'jour'] = df.loc[:,'jour']
    
    vals_quantiles=[]
    for q in range(25, 125, 25):
        vals_quantiles.append(df_nonobj.groupby('jour').quantile(q=q/100).reset_index())
    
    type_ppl = "hospitalisées"
    if "rea" in val:
        type_ppl = "en réanimation"
    max_values_diff=[]
    
    clrs_dep = []
    current_values = [[], []]
    for dep in tqdm(deps_ordered_nb):
        data_dep = df[df["departmentName"] == dep]
        
        data_dep[val + "_new"] = data_dep[val].diff()
        ordered_values = data_dep.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
        max_values_diff += [ordered_values.quantile(.90)]
                
        df_dep_temp = df[df["dep"] == dep]
        
        values_y = 100 * df_dep_temp["rea"] / lits_reas[lits_reas["nom_dpt"] == deps_ordered[list(deps_ordered_nb).index(dep)]]["LITS"].values[0]
        
        clrs=[]
        for tx in values_y.values:
            if tx < 60:
                clrs += ["green"]
            elif tx < 80:
                clrs += ["orange"]
            else:
                clrs += ["red"]
        current_values[1].append(clrs[-1])
        
        mean_last7 = values_y[-7:].mean()
        if mean_last7 < 60:
            clrs_dep += ["green"]
        elif mean_last7 < 80:
            clrs_dep += ["orange"]
        else:
            clrs_dep += ["red"]
        
        df_sursaud.loc[(df_sursaud["dep"] == dep) & (df_sursaud["date_de_passage"] == dates_sursaud[-1]), "indic2_clr"] = clrs_dep[-1]
            
        current_values[0].append(values_y.values[-1])
        fig.add_trace(go.Bar(x = df["jour"], y = values_y,
                            marker_color=clrs),
                      i, j)
        
        fig.update_xaxes(title_text="", range=["2020-04-25", last_day_plot], gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
        fig.update_yaxes(title_text="", range=[0, 150], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j)

        j+=1
        if j == nj+1: #or ((i >= 9) & (j >= nj-1)) 
            i+=1
            j=1
            
    shapes=[]
    cnt=0
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=14, color = clrs_dep[cnt])
        #print(regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] ))
        xref = "x"+str(cnt+1)
        yref = "y"+str(cnt+1)
        shapes += [{'type': 'rect', 'x0': dates[-7], 'y0': 0, 'x1': dates[-1], 'y1': 200, 'xref': xref, 'yref': yref, 'fillcolor': clrs_dep[cnt], 'layer' : "below", 'line_width':0, 'opacity' : 0.1}]

        cnt+=1
        
    fig['layout'].update(shapes=shapes)

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
                        yanchor="bottom", y=0.20, xanchor="left", x=0.87,
                        ticks="outside", tickprefix="  ", ticksuffix=" hosp.",
                        nticks=5,
                        tickfont=dict(size=12),
                        titlefont=dict(size=15)),
                      
                    showlegend=False,
    
                     title={
                        'text': "<b>Saturation des services de réanimation</b>",
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
    
    annot=()
    cnt=1
    for dep in deps_ordered_nb:
        annot += (dict(
            x=dates[-1], y = current_values[0][cnt-1], # annotation point
            xref='x'+str(cnt), 
            yref='y'+str(cnt),
            text="<b>{}</b> % ".format(math.trunc(round(current_values[0][cnt-1]))),
            xshift=0,
            yshift=3,
            align='center',
            xanchor="right",
            font=dict(
                color=current_values[1][cnt-1],
                size=10
                ),
            ax = 0,
            ay = -20,
            arrowcolor=current_values[1][cnt-1],
            arrowsize=1,
            arrowwidth=1,
            arrowhead=4
        ),)
        cnt+=1

    fig["layout"]["annotations"] += annot + ( 
                        dict(
                            x=0.82,
                            y=0.05,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text="La moyenne des 7 deniers jours est considérée pour déterminer la<br>couleur d'un département. Couleurs : rouge (> 80 %), orange (60 à 80%),<br>vert (< 60%).",
                            showarrow = False,
                            font=dict(size=16), 
                            opacity=1,
                            align='left'
                        ),
                        dict(
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
                            x=0.5,
                            y=1.03,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='middle',
                            text="par rapport au nb de lits en réa. avant l'épidémie - guillaumerozier.fr",
                            showarrow = False,
                            font=dict(size=30), 
                            opacity=1
                        ),
                                    ) 
    
    name_fig = "subplots_deconf_indic2"
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=1.5, width=1600, height=2300)

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


# In[13]:


#build_map(df_sursaud, date_str="date_de_passage", dep_str="code", type_data="reg", color_str="indic2_clr", img_folder="images/charts/france/indic2/{}.png", title="Indicateur 2 : saturation des réa")


# In[14]:


df_groupby = df.groupby(['code', 'jour']).sum().reset_index()
df_groupby["capa_rea"] = 100 * df_groupby['rea'].values/df_groupby['LITS'].values


# In[15]:


for code in codes_reg:
    df_reg_temp = df_groupby[df_groupby['code'] == code]
    capa_rea= df_reg_temp['capa_rea'].values[-7:].mean()
    
    if capa_rea > 80:
        clr= "red"
    elif capa_rea > 60:
        clr="orange"
    else:
        clr="green"
    df_groupby.loc[(df_groupby['jour'] == dates[-1]) & (df_groupby['code'] == code), 'capa_rea_clr'] = clr 
    df_groupby.loc[(df_groupby['jour'] == dates[-1]) & (df_groupby['code'] == code), 'synthese_indics'] = "green" 


# In[16]:


build_map(df_groupby, date = dates[-1], date_str="jour", dep_str="code", type_data="reg", color_str="capa_rea_clr", img_folder="images/charts/france/indic2/{}.png", legend_str = "Rouge : > 80%<br>Orange : 60 à 80%<br>Vert : < 60%", title="Indicateur 2 : tension hospitalière (par région)", subtitle="proportion de lits de réa. occupés par des patients Covid19")


# In[17]:


build_map(df_sursaud, date = dates[-1], date_str="date_de_passage", dep_str="dep", type_data="dep", color_str="indic2_clr", img_folder="images/charts/france/indic2_deps/{}.png", legend_str = "Rouge : > 80%<br>Orange : 60 à 80%<br>Vert : < 60%", title="Indicateur 2 : tension hospitalière (par département)", subtitle="proportion de lits de réa. occupés par des patients Covid19")


# In[18]:


build_map(df_groupby, date = dates[-1], date_str="jour", dep_str="code", type_data="reg", color_str="synthese_indics", img_folder="images/charts/france/synthese_indics/{}.png", title="Synthèse des indicateurs de déconfinement", subtitle="synthèse des indicateurs 1 et 2")


# In[19]:


"""
for val in ["hosp_deppop"]: #, "hosp", "rea", "rea_pop"
    ni, nj = 12, 9
    i, j = 1, 1
    
    regions_ordered = df_region[df_region['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["regionName"].values
    regions_ordered = list(dict.fromkeys(list(regions_ordered)))[:]
    
    #df_region[val+"_new"] = df_region[val].diff()
    max_value = 100
    
    #deps_ordered = df[df['jour'] == dates[-1]].sort_values(by=[val], ascending=False)["departmentName"].values
    #deps_ordered = list(dict.fromkeys(list(deps_ordered)))[:]
    deps_ordered = np.array(list(dict.fromkeys(list(df["departmentName"].values)))[:])
    deps_ordered_nb = np.array(list(dict.fromkeys(list(df["dep"].values)))[:])
    
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "2A", "200")
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "2B", "201")
    
    ind_deps = np.argsort(deps_ordered_nb.astype(int))
    
    deps_ordered_nb = deps_ordered_nb[ind_deps]
    deps_ordered = deps_ordered[ind_deps]
    
    deps_ordered_nb = deps_ordered_nb.astype(str)
    
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "200", "2A")
    deps_ordered_nb = np.char.replace(deps_ordered_nb, "201", "2B")
    
    titles = []
    k=0
    for case in range(1, ni * nj - 1):
        if case in [80, 81, 89, 90, 98, 99]:
            titles += [""] 
        else:
            titles += ["<b>" + deps_ordered_nb[k] + "</b> - " + deps_ordered[k]]
            k+=1

    fig = make_subplots(rows=ni, cols=nj, shared_yaxes=True, subplot_titles= titles, vertical_spacing = 0.025, horizontal_spacing = 0.002)
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
    
    clrs_dep = []
    for dep in tqdm(deps_ordered_nb):
        data_dep = df[df["departmentName"] == dep]
        
        data_dep[val + "_new"] = data_dep[val].diff()
        ordered_values = data_dep.sort_values(by=[val + "_new"], ascending=False)[val + "_new"]
        max_values_diff += [ordered_values.quantile(.90)]
                
        df_dep_temp = df[df["dep"] == dep]
        
        values_y = 100 * df_dep_temp["rea"]/lits_reas[lits_reas["nom_dpt"] == deps_ordered[list(deps_ordered_nb).index(dep)]]["LITS"].values[0]
        clrs=[]
        for tx in values_y.values:
            if tx < 60:
                clrs += ["green"]
            elif tx < 80:
                clrs += ["orange"]
            else:
                clrs += ["red"]
        
        mean_last7 = values_y[-7:].mean()
        if mean_last7 < 60:
            clrs_dep += ["green"]
        elif mean_last7 < 80:
            clrs_dep += ["orange"]
        else:
            clrs_dep += ["red"]
            
        #fig.add_trace(go.Bar(x = df["jour"], y = values_y,
                        #    marker_color=clrs),
                    #  i, j)
        fig.add_trace(go.Scatter(x = df[df["dep"] == dep]["jour"], y = df[df["dep"] == dep][""],
                            marker_color=clrs),
                      i, j)
        
        fig.update_xaxes(title_text="", range=["2020-04-25", "2020-05-12"], gridcolor='white', showgrid=False, ticks="inside", tickformat='%d/%m', tickfont=dict(size=7), tickangle=0, nticks=6, linewidth=0, linecolor='white', row=i, col=j)
        #fig.update_yaxes(title_text="", range=[0, 150], gridcolor='white', linewidth=0, linecolor='white', tickfont=dict(size=7), nticks=8, row=i, col=j)

        j+=1
        if j == nj+1 or ((i >= 9) & (j >= nj-1)): 
            i+=1
            j=1

    cnt=0
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=14, color = clrs_dep[cnt])
        #print(regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] ))
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
                        'text': "Indicateur 2 : <b>saturation des réanimations par les patients Covid</b>",
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

    fig["layout"]["annotations"] += ( 
                        dict(
                            x=0.9,
                            y=0.17,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='top',
                            text='Rouge : > 80 %<br><br><br>Orange : 60 à 80 %<br><br><br>Vert : < 60 %',
                            showarrow = False,
                            font=dict(size=16), 
                            opacity=1,
                            align='left'
                        ),
                        dict(
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
                            x=0.5,
                            y=1.03,
                            xref='paper',
                            yref='paper',
                            xanchor='center',
                            yanchor='middle',
                            text="par rapport au nb de lits en réa. avant l'épidémie - guillaumerozier.fr",
                            showarrow = False,
                            font=dict(size=30), 
                            opacity=1
                        ),
                                    )
    
    name_fig = "subplots_deconf_synthese"
    fig.write_image("images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1600, height=2300)

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


    #fig.show()"""

