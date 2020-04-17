#!/usr/bin/env python
# coding: utf-8

# In[3]:


from covid19_france_charts import import_data
import pandas as pd


# ## Data Import

# In[ ]:


df, df_confirmed, dates, df_new, df_tests = import_data()

df_region = df.groupby(['regionName', 'jour', 'regionPopulation']).sum().reset_index()
df_region["hosp_regpop"] = df_region["hosp"] / df_region["regionPopulation"]*1000000 
df_region["rea_regpop"] = df_region["rea"] / df_region["regionPopulation"]*1000000 

df_tests_tot = df_tests.groupby(['jour']).sum().reset_index()

df_new_region = df_new.groupby(['regionName', 'jour']).sum().reset_index()
df_france = df.groupby('jour').sum().reset_index()

regions = list(dict.fromkeys(list(df['regionName'].values))) 


# In[ ]:



import numpy as np
for val in ["hosp_deppop"]: #, "hosp", "rea", "rea_pop"
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
        
    
    for dep in tqdm(deps_ordered):
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
            
        """if j == nj+1:
            i+=1
            j=1"""
    cnt=0
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=14, color = str(colors[regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] )]))
        print(regions_ordered.index( df[df['departmentName'] == deps_ordered[cnt]]['regionName'].values[0] ))
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
                                    )
    
    name_fig = "subplots_dep_" + val 
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

