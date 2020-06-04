#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests
import pandas as pd
import json
from tqdm import tqdm


# In[1]:


# Download data from Santé publique France and export it to local files
def download_data():
    pbar = tqdm(total=8)
    url_metadata = "https://www.data.gouv.fr/fr/organizations/sante-publique-france/datasets-resources.csv"
    url_geojson = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
    url_deconf = "https://www.data.gouv.fr/fr/datasets/r/f2d0f955-f9c4-43a8-b588-a03733a38921"
    
    pbar.update(1)
    metadata = requests.get(url_metadata)
    pbar.update(2)
    geojson = requests.get(url_geojson)
    pbar.update(3)
    
    with open('data/france/metadata.csv', 'wb') as f:
        f.write(metadata.content)
    pbar.update(4)
    
    with open('data/france/dep.geojson', 'wb') as f:
        f.write(geojson.content)
        
    pbar.update(5)
    df_metadata = pd.read_csv('data/france/metadata.csv', sep=";")
    url_data = df_metadata[df_metadata['url'].str.contains("/donnees-hospitalieres-covid19")]["url"].values[0]
    url_data_new = df_metadata[df_metadata['url'].str.contains("/donnees-hospitalieres-nouveaux")]["url"].values[0]
    url_tests = df_metadata[df_metadata['url'].str.contains("/donnees-tests-covid19-labo-quotidien")]["url"].values[0]
    url_incidence = df_metadata[df_metadata['url'].str.contains("/sp-pe-tb-quot")]["url"].values[0]
    url_tests_viro = df_metadata[df_metadata['url'].str.contains("/sp-pos-quot-dep")]["url"].values[0]
    url_sursaud = df_metadata[df_metadata['url'].str.contains("sursaud.*departement")]["url"].values[0]
    
    pbar.update(6)
    data = requests.get(url_data)
    data_new = requests.get(url_data_new)
    data_tests = requests.get(url_tests)
    data_deconf = requests.get(url_deconf)
    data_sursaud = requests.get(url_sursaud)
    data_incidence = requests.get(url_incidence)
    data_tests_viro = requests.get(url_tests_viro)
    
    pbar.update(7)
    with open('data/france/donnes-hospitalieres-covid19.csv', 'wb') as f:
        f.write(data.content)
        
    with open('data/france/donnes-hospitalieres-covid19-nouveaux.csv', 'wb') as f:
        f.write(data_new.content)
        
    with open('data/france/donnes-tests-covid19-quotidien.csv', 'wb') as f:
        f.write(data_tests.content)
        
    with open('data/france/indicateurs-deconf.csv', 'wb') as f:
        f.write(data_deconf.content)
    
    with open('data/france/sursaud-covid19-departement.csv', 'wb') as f:
        f.write(data_sursaud.content)
        
    with open('data/france/taux-incidence-dep-quot.csv', 'wb') as f:
        f.write(data_incidence.content)
        
    with open('data/france/tests_viro-dep-quot.csv', 'wb') as f:
        f.write(data_tests_viro.content)
        
    pbar.update(8)


# Import data from previously exported files to dataframes
def import_data():
    
    pbar = tqdm(total=4)
    pbar.update(1)
    df = pd.read_csv('data/france/donnes-hospitalieres-covid19.csv', sep=";")
    df_sursaud = pd.read_csv('data/france/sursaud-covid19-departement.csv', sep=",")
    df_new = pd.read_csv('data/france/donnes-hospitalieres-covid19-nouveaux.csv', sep=";")
    df_tests = pd.read_csv('data/france/donnes-tests-covid19-quotidien.csv', sep=";")
    df_deconf = pd.read_csv('data/france/indicateurs-deconf.csv', sep=",")
    df_incid = pd.read_csv('data/france/taux-incidence-dep-quot.csv', sep=",")
    df_tests_viro = pd.read_csv('data/france/tests_viro-dep-quot.csv', sep=",")
    
    lits_reas = pd.read_csv('data/france/lits_rea.csv', sep=",")
    
    df_regions = pd.read_csv('data/france/departments_regions_france_2016.csv', sep=",")
    df_reg_pop = pd.read_csv('data/france/population_grandes_regions.csv', sep=",")
    df_dep_pop = pd.read_csv('data/france/dep-pop.csv', sep=";")
    
    ###
    df = df.merge(df_regions, left_on='dep', right_on='departmentCode')
    df = df.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df = df.merge(df_dep_pop, left_on='dep', right_on='dep')
    df = df[df["sexe"] == 0]
    df['hosp_nonrea'] = df['hosp'] - df['rea']
    df = df.merge(lits_reas, left_on="departmentName", right_on="nom_dpt")
    
    df_incid = df_incid[df_incid["cl_age90"] == 0]
    df_tests_viro = df_tests_viro[df_tests_viro["cl_age90"] == 0]
    
    df_incid = df_incid.merge(df_regions, left_on='dep', right_on='departmentCode')
    df_incid = df_incid.merge(df_tests_viro.drop("p", axis=1).drop("cl_age90", axis=1), left_on=['jour', 'dep'], right_on=['jour', 'dep'])
    
    df_new = df_new.merge(df_regions, left_on='dep', right_on='departmentCode')
    df_new = df_new.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df_new = df_new.merge(df_dep_pop, left_on='dep', right_on='dep')
    df_new['incid_hosp_nonrea'] = df_new['incid_hosp'] - df_new['incid_rea']
    
    df_sursaud = df_sursaud.merge(df_regions, left_on='dep', right_on='departmentCode')
    df_sursaud = df_sursaud.merge(df_reg_pop, left_on='regionName', right_on='regionName')
    df_sursaud = df_sursaud.merge(df_dep_pop, left_on='dep', right_on='dep')
    
    df_sursaud = df_sursaud[df_sursaud["sursaud_cl_age_corona"] == "0"]
    df_sursaud["taux_covid"] = df_sursaud["nbre_pass_corona"] / df_sursaud["nbre_pass_tot"]
    
    pbar.update(2)
    
    df['rea_pop'] = df['rea']/df['regionPopulation']*100000
    df['rea_deppop'] = df['rea']/df['departmentPopulation']*100000
    
    df['rad_pop'] = df['rad']/df['regionPopulation']*100000
    
    df['dc_pop'] = df['dc']/df['regionPopulation']*100000
    df['dc_deppop'] = df['dc']/df['departmentPopulation']*100000
    
    df['hosp_pop'] = df['hosp']/df['regionPopulation']*100000
    df['hosp_deppop'] = df['hosp']/df['departmentPopulation']*100000
    
    df['hosp_nonrea_pop'] = df['hosp_nonrea']/df['regionPopulation']*100000
    pbar.update(3)
    df_confirmed = pd.read_csv('data/data_confirmed.csv')
    pbar.update(4)
    
    deps = list(dict.fromkeys(list(df['departmentCode'].values))) 
    for d in deps:
        for col in ["dc", "rad", "rea", "hosp_nonrea", "hosp"]:
            vals = df[df["dep"] == d][col].diff()
            df.loc[vals.index,col+"_new"] = vals
            df.loc[vals.index,col+"_new_deppop"] = vals / df.loc[vals.index,"departmentPopulation"]*100000
    
    df_tests = df_tests.drop(['nb_test_h', 'nb_pos_h', 'nb_test_f', 'nb_pos_f'], axis=1)
    df_tests = df_tests[df_tests['clage_covid'] == "0"]
    
    # Correction du 14/05 (pas de données)
    #cols_to_change = df.select_dtypes(include=np.number).columns.tolist()
    cols_to_change = [s for s in df.columns.tolist() if "new" in s]
    
    #for dep in deps:
        #ligne = df.loc[(df["jour"] == "2020-05-15") & (df["dep"] == dep),:]

        #moitié = ligne.loc[:, cols_to_change]/2
        #df.loc[ (df["jour"] == "2020-05-15") & (df["dep"] == dep), cols_to_change] = moitié

        #ligne.loc[:, cols_to_change] = moitié
        #ligne.loc[:,["jour"]] = ["2020-05-14"]
        #df = df.append(ligne)
        
    dates = sorted(list(dict.fromkeys(list(df['jour'].values))))
    return df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid


# In[22]:


df_incid = pd.read_csv('data/france/taux-incidence-dep-quot.csv', sep=",")
df_tests_viro = pd.read_csv('data/france/tests_viro-dep-quot.csv', sep=",")
df_regions = pd.read_csv('data/france/departments_regions_france_2016.csv', sep=",")

#df_incid = df_incid.merge(df_tests_viro.drop("p", axis=1).drop("cl_age90", axis=1), left_on=['jour', 'dep'], right_on=['jour', 'dep'])

df_incid = df_incid[df_incid["cl_age90"] == 0]
df_tests_viro = df_tests_viro[df_tests_viro["cl_age90"] == 0]
    
df_incid = df_incid.merge(df_regions, left_on='dep', right_on='departmentCode')
df_incid = df_incid.merge(df_tests_viro.drop("p", axis=1).drop("cl_age90", axis=1), left_on=['jour', 'dep'], right_on=['jour', 'dep'])
    


# In[23]:


df_incid

