#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 23:34:29 2021

@author: adelgado
"""

# Import necessary libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl

#%% Import stations

stations = pd.read_csv('01_data/stations_hc.csv')
#stations = stations.loc[stations.domain =='d02']\
#            .drop('domain', axis=1).sort_values(by='code')
stations.index =stations.code
print(stations)

aq_data = pd.read_pickle('01_data/processed/obs/data_all_photo.pkl')
parameters = ['o3', 'no', 'no2', 'co', 'ben', 'tol', 'pm10', 'pm2.5']
for p in parameters:
    aq_data[p] = aq_data[p].astype(float)
aq_data.info()

#%% Data analysis
fig, ax = plt.subplots(5, sharex=True, sharey=True,figsize=(8,12))

stat = ['Paulínia', 'Pinheiros', 'S.André-Capuava', 'S.José Campos',
        'S.José Campos-Vista Verde']

for i,n in enumerate(stat):
    aq_data[aq_data.station == n][['ben','tol']].plot(secondary_y='ben', alpha=.8,ax=ax[i], legend=False)
    ax[i].set_title(n + " ("+stations[stations.name == n].type.values[0]+")", loc='left')
    if i == 0:
        ax[i].legend(['Benzene'], loc=1)
        plt.legend(['Toluene'], loc=2)
    if i == 2:
        ax[i].set_ylabel("Toluene [$\mu$gm$^{-3}$]")
        plt.ylabel('Benzene [$\mu$gm$^{-3}$]')
        
fig.savefig('05_output/obs/fig/HC_CETESB_sep_oct2018.pdf',bbox_inches='tight',facecolor='w')

#%% Figure of daily profile
fig, ax = plt.subplots(sharex=True, figsize=(6,4))
t = 'Urban'
alpha = .1
df = aq_data[aq_data.type == t][['o3', 'no', 'no2', 'co','tol','ben']]
mean = df.groupby(df.index.hour).mean()
sd = df.groupby(df.index.hour).std()
    
mean.plot(y=['o3', 'no', 'no2'], 
          style=['-o','-','-s'], 
          color=['b', 'darkorange','r'], 
          lw=3,ax=ax, legend=False)
ax.fill_between(mean.index, mean.o3+sd.o3,mean.o3-sd.o3,
                       color='b',alpha=alpha )
#ax.fill_between(mean.index, mean.no+sd.no,mean.no-sd.no,
#                       color='darkorange',alpha=alpha)
#ax.fill_between(mean.index, mean.no2+sd.no2,mean.no2-sd.no2,
#                       color='r',alpha=alpha)
ax.set_ylim(0,120)
ax.set_title(t, loc='left', fontsize=8)
ax.set_xlabel('Hours (Local Time)')
plt.xticks(np.arange(0,24,2))
    
    
ax2 = ax.twinx()
mean.plot(y=['co','tol','ben'], ax=ax2, style=['-^g','-.c','-.k'], lw=2.5, legend=False)
ax2.set_ylim(0,8)
#ax2.fill_between(mean.index, mean.co+sd.co,mean.co-sd.co,
#                       color='g',alpha=alpha )
#ax2.fill_between(mean.index, mean.tol+sd.tol,mean.tol-sd.tol,
#                       color='c',alpha=alpha)
#ax2.fill_between(mean.index, mean.ben+sd.ben,mean.ben-sd.ben,
#                       color='k',alpha=alpha )

ax.set_ylabel('O$_3$, NO, NO$_2$ [$\mu$gm$^{-3}$]', loc='center')
ax2.set_ylabel('CO [ppm], Tol. and Ben. [$\mu$gm$^{-3}$]',loc='center')
ax.legend(['O$_3$','NO','NO$_2$'], ncol=3, fontsize=8, loc=2)
ax2.legend(['CO','Tol','Ben'], fontsize=8, loc=1, ncol=3)
fig.savefig('dissertation/fig/byhour_all_polls.pdf', bbox_inches='tight', facecolor='w')

