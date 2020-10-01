#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[43]:



df_incid = pd.read_csv('data/france/taux-incidence-dep-quot.csv', sep=";")
df_incid_j1 = pd.read_csv('data/france/taux-incidence-dep-quot_J-1.csv', sep=";")
df_incid_j2 = pd.read_csv('data/france/taux-incidence-dep-quot_J-2.csv', sep=";")
df_incid_j4 = pd.read_csv('data/france/taux-incidence-dep-quot_J-4.csv', sep=";")

df_incid = df_incid[df_incid['cl_age90'] == 0]
df_incid_j1 = df_incid_j1[df_incid_j1['cl_age90'] == 0]
df_incid_j2 = df_incid_j2[df_incid_j2['cl_age90'] == 0]
df_incid_j3 = df_incid_j3[df_incid_j3['cl_age90'] == 0]
df_incid_j4 = df_incid_j4[df_incid_j4['cl_age90'] == 0]


# In[44]:


df_incid['P'].sum() - df_incid_j1['P'].sum()


# In[45]:


df_incid_j1['P'].sum() - df_incid_j2['P'].sum()


# In[46]:


df_incid_j2['P'].sum() - df_incid_j3['P'].sum()


# In[40]:


df_incid.groupby('jour').sum()


# In[41]:


df_incid_j1.groupby('jour').sum()


# In[42]:


df_incid_j2.groupby('jour').sum()


# In[47]:


df_incid_j3.groupby('jour').sum()


# In[48]:


df_incid_j4.groupby('jour').sum()


# In[ ]:




