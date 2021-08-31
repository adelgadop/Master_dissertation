#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 19:41:49 2021

@author: adelgado
"""

# import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import seaborn as sns
import functions.mod_stats as ms

#%%  Import stations of interest for Toluene and Benzene ----------------------------
# However, simulations only have Toluene.

stations = pd.read_csv('01_data/stations_hc.csv')
stations.index =stations.code
print(stations)

#%% Import observations and simulations ----------------------------------------------
def data_import(path, stations):
    """
    From dictionary to pandas DataFrame
    
    """
    files = open(path, "rb")
    pol = pkl.load(files)
    files.close()
    df = pd.DataFrame()

    for n in list(pol.keys()):
        df1 = pol[n]
        df1['station'] = n
        df1['type'] = stations[stations.name == n].type.values[0]
        df = pd.concat([df,df1])
    return df

# Observations
obs = pd.read_pickle('01_data/processed/obs/data_all_photo_toluene.pkl').drop('code',axis=1)
parameters = ['o3', 'no', 'no2', 'co', 'ben', 'tol', 'pm10', 'pm2.5']

for p in parameters:
    obs[p] = obs[p].astype(float)
obs.reset_index(inplace=True)
obs.rename(columns={'index':'local_date'}, inplace=True)

# SImulations
path = '01_data/raw/mod/Y2018/'
mod_sep18 = data_import(path+'sep18/FINd02_2018_09.pkl', stations)
mod_oct18 = data_import(path+'oct18/FINd02_2018_10.pkl', stations)

mod = pd.concat([mod_sep18,mod_oct18])
mod = mod.drop(['date','code','name'],axis=1)

#%% Merge both data types (Obs and Mod) -----------------------------------------------
data= obs.merge(mod, 
          on=['local_date','station','type'],
          suffixes=('_obs', '_mod')).drop(['tc','pm10','pm2.5','rh','ws','wd'], axis=1)
data.set_index('local_date', inplace=True)

#%% Figure by daily profile for O3, NO, NO2, CO and Toluene --------------------------
df_1 = data[['station','type','tol_obs','tol_mod','o3_obs','o3_mod',
           'no_obs','no_mod','no2_obs','no2_mod','co_obs','co_mod']].dropna(how='all')


fig, ax = plt.subplots(2,1,sharex=True, figsize=(6,4*2), gridspec_kw={'hspace':0.15})
alpha = .1
t = 'Urban'
df = df_1[df_1.type == t].dropna()
mean = df.groupby(df.index.hour).mean()
sd = df.groupby(df.index.hour).std()

# Observed values
mean.plot(y=['o3_obs', 'no_obs', 'no2_obs'], 
          style=['-o','-','-s'], 
          color=['b', 'darkorange','r'], 
          lw=3,ax=ax[0], legend=False)
ax[0].fill_between(mean.index, mean.o3_obs+sd.o3_obs,mean.o3_obs-sd.o3_obs,
                       color='b',alpha=alpha )
ax[0].set_ylim(0,150)
ax[0].set_title(str(df.station.unique()[0])+' - '+t + ' (Obs.)', loc='left', fontsize=10)
ax[0].set_xlabel('Hours (Local Time)')
plt.xticks(np.arange(0,24,2))
    
    
ax1 = ax[0].twinx()
mean.plot(y=['co_obs','tol_obs'], ax=ax1, style=['-g','-oc'], lw=2.5, legend=False)
ax1.set_ylim(0,14)

ax[0].set_ylabel('O$_3$, NO, NO$_2$ [$\mu$gm$^{-3}$]', loc='center')
ax1.set_ylabel('CO [ppm], Toluene [$\mu$gm$^{-3}$]',loc='center')
ax[0].legend(['O$_3$','NO','NO$_2$'], ncol=3, fontsize=8, loc=2)
ax1.legend(['CO','Tol'], fontsize=8, loc=1, ncol=2)

# Simulated values
mean.plot(y=['o3_mod', 'no_mod', 'no2_mod'], 
          style=['-o','-','-s'], 
          color=['b', 'darkorange','r'], 
          lw=3,ax=ax[1], legend=False)
ax[1].fill_between(mean.index, mean.o3_mod+sd.o3_mod,mean.o3_mod-sd.o3_mod,
                       color='b',alpha=alpha )
ax[1].set_ylim(0,150)
ax[1].set_title(str(df.station.unique()[0])+' - '+t + ' (Mod.)', loc='left', fontsize=10)
ax[1].set_xlabel('Hours (Local Time) \n (Sep-Oct, 2018), grouped by hour')
plt.xticks(np.arange(0,24,2))
    
ax2 = ax[1].twinx()
mean.plot(y=['co_mod','tol_mod'], ax=ax2, style=['-g','o-c'], lw=2.5, legend=False)
ax2.set_ylim(0,14)

ax[1].set_ylabel('O$_3$, NO, NO$_2$ [$\mu$gm$^{-3}$]', loc='center')
ax2.set_ylabel('CO [ppm], Toluene [$\mu$gm$^{-3}$]',loc='center')
#ax[1].legend(['O$_3$','NO','NO$_2$'], ncol=3, fontsize=8, loc=2)
#ax2.legend(['CO','Tol'], fontsize=8, loc=1, ncol=2)
fig.savefig('dissertation/fig/pol_hour_tol.pdf',bbox_inches='tight', facecolor='w')
fig.savefig('05_output/evaluation/fig/pol_hour_tol.pdf',bbox_inches='tight', facecolor='w')

#%% Toluene figures ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8,3))
data[data.station=='Pinheiros'].plot(y= 'tol_mod', style= '-g',
                                     lw = 2.5,
                                     alpha = 0.7,
                                     ax=ax)
data[data.station=='Pinheiros'].plot(y= 'tol_obs', style= '.k', 
                                     ax=ax, markersize=2.5)
ax.legend(['Mod.','Obs.'])
ax.set_xlabel('Hours (local time)')
ax.set_ylabel('Toluene [$\mu$g m$^{-3}$]')
ax.set_title('Pinheiros - Urban station', loc='left', fontsize=10)
fig.savefig('05_output/evaluation/fig/pol_Pinheiros_tol.pdf',bbox_inches='tight', facecolor='w')

#%% Toluene figure by station 
fig, ax = plt.subplots(5, figsize=(6.5,3*3), sharex=True, gridspec_kw={'hspace':0.25})
for i,n in enumerate(data.station.unique()[1:]):
    df_2 = data[data.station == n]
    df_2.plot(y='tol_obs', style='.k', markersize=2.5, ax = ax[i], legend=False, label = 'Obs.')
    df_2.plot(y='tol_mod', style='-g', lw=1.5, alpha = 0.7, ax = ax[i], legend=False, label = 'Mod.')
    ax[i].set_xlabel('Hours (local time)')
    t = stations[stations.name == n].type.values[0]
    ax[i].set_title(str(df_2.station.unique()[0])+' - '+t, loc='left', fontsize=10)                                
    ax[0].legend()
    ax[2].set_ylabel('Toluene [$\mu$g m$^{-3}$]')
fig.savefig('dissertation/fig/tseries_tol.pdf', bbox_inches='tight', facecolor='w')
fig.savefig('05_output/evaluation/fig/tseries_tol.pdf',bbox_inches='tight', facecolor='w')

#%% Statistical analysis -------------------------------------------------------------------
df = data[['station', 'type','tol_obs','tol_mod']].dropna()

by = 'station'
sites = df.station.unique()
stats = {}
stat_df = pd.DataFrame()
for i in sites:
    stats[i] = (ms.aq_stats(df[df[by].isin([i])],polls=['tol']))
    stats[i][by] = (i)
    df2 = stats[i]
    stat_df = pd.concat([stat_df,df2]).round(2)
    
stat_df.set_index(by, inplace=True)
print(stat_df)

df_1 = pd.DataFrame(index=['t-statistic', 't critical'])

for p in stat_df.index:
    df_1[p] = ms.r_pearson_sig(n=stat_df.loc[p,'n'],
                               r=stat_df.loc[p,'r'],
                               deg_free=stat_df.loc[p,'n']-2,
                               alpha=0.05)
df_1 = df_1.round(2).T
df_1['Significant'] = [(df_1['t-statistic'][i] > df_1['t critical'][i]) for i in range(len(df_1.index))]
print(df_1)

stats = pd.merge(stat_df,df_1, 
                 left_index=True, 
                 right_index=True).T.reset_index().rename(columns={'index':'Statistic'})
stats.set_index('Statistic', inplace=True)

order = ['Paulínia', 'Pinheiros', 'S.André-Capuava', 
         'S.José Campos', 'S.José Campos-Vista Verde']

stats = stats[order]

print(stats)

print(stats.to_latex(caption='Statistical results for toluene in Sep-Oct 2018 period',
                     label='tab:stats_tol'),
      file=open('05_output/evaluation/tab/stats_tol.tex','w'))

