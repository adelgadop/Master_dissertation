#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 19:54:57 2021

@author: adelgado
"""

# Import necessary libraries

import pandas as pd
import os, fnmatch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.dates as md
import seaborn as sns
#from netCDF4 import Dataset
#from wrf import getvar, to_np, get_cartopy, latlon_coords
#import wrf
import pickle as pkl
#from mpl_toolkits.basemap import Basemap
import glob

#%% import data

st       = pd.read_csv('01_data/stations.csv') # encoding = "ISO-8859-1")
stations = st
sites    = st.loc[st.domain=='d02',:].reset_index(drop=True)
types    = list(st.type.unique())
print(types)
reg      = sites.loc[sites.type == types [0]].reset_index(drop=True)
urb      = sites.loc[sites.type == types [1]].reset_index(drop=True)
urp      = sites.loc[sites.type == types [2]].reset_index(drop=True)
idt      = sites.loc[sites.type == types [3]].reset_index(drop=True)
fpr      = sites.loc[sites.type == types [4]].reset_index(drop=True)
coa      = sites.loc[sites.type == types [5]].reset_index(drop=True)

types = ['Urban','Urban park','Forest preservation','Regional urban','Industry']
sts = stations[stations.type.isin(types)].sort_values('type')[['name','lat','lon','type','abb']].iloc[0:,:]
print(sts.to_latex(index=False)) 

#%% Import only September and October 2018 - Measured data
obs18 = pd.read_pickle('01_data/processed/obs/obs18.pkl').set_index('local_date')

#%% Temperature and particles from observations

obs18.loc[:,'Month'] = obs18.index.month
obs18 = obs18[obs18.Month <11]
print(f"stations: {list(obs18.station.unique())}")
print(obs18)

#%% Figure of PM and Temperature
df_1=obs18.groupby([obs18.index,'type']).mean()[['tc','pm10','pm2.5']].reset_index('type')
types_masp = ['Urban','Urban park','Forest preservation']
obs18_day = {types_masp[0]:df_1.loc[df_1.type == types_masp[0]],
             types_masp[1]:df_1.loc[df_1.type == types_masp[1]],
             types_masp[2]:df_1.loc[df_1.type == types_masp[2]]}

fig, ax = plt.subplots(3,figsize=(10,8), sharex=True, sharey=False)
for i,t in enumerate(types_masp):
    obs18_day[t][['pm10','pm2.5']].plot(ax = ax[i], color=['r','0.5'], alpha=.9, legend=False)
    ax[i].set_ylabel('[$\mu$g m$^{-3}$]')
    ax1 = ax[i].twinx()
    obs18_day[t][['tc']].plot(ax = ax1, lw=3,legend=False, color='royalblue', style='-', alpha=.5)
    ax1.set_ylabel('[ºc]')
    ax[i].set_title(t,size=10, loc='left')
    ax[i].set_xlabel('Local Time (daily mean)')
    ax[i].tick_params(axis="x", direction="in",length=3, width=1, colors='k')
    if i == 2:
        ax[i].legend(['PM$_{10}$','PM$_{2.5}$'],fontsize=10, loc=8)
        ax1.legend(['Temp. 2-m'],fontsize=10, loc=4)
fig.savefig("05_output/obs/fig/pm_temp_type.pdf",bbox_inches='tight', facecolor='w')

#%%
pm10_station = list(obs18[['station','tc','pm10','pm2.5']].dropna(thresh=2).station.unique())
pm10_types = [stations[stations.name == i].type.values[0] for i in pm10_station]
pm_df = pd.DataFrame({'Type':pm10_types,'Station':pm10_station}).sort_values(by='Type').reset_index(drop=True)
print(pm_df[pm_df.Type.isin(types_masp)].reset_index(drop=True))

#%% Urban park and Urban for CO, NO, NO2
Urban = obs18[obs18.type == 'Urban park'].station.unique()
Urban = obs18[obs18.station.isin(Urban)][['station','type', 'no','no2','co']]
Urban['hour'] = Urban.index.time

fig, axes = plt.subplots(2,2, figsize=(12,8)) # create figure and axes
ylabels = ['ppm', '$\mu$gm$^{-3}$','$\mu$gm$^{-3}$']
for i,el in enumerate(['co','no','no2']):
    a = Urban.boxplot(el, by="hour", ax=axes.flatten()[i], rot=90,sym='k+', grid=False)
    ax=axes.flatten()[i].set_ylabel(ylabels[i])
    #plt.setp(a['fliers'], markersize=3.0)

fig.delaxes(axes[1,1]) # remove empty subplot
plt.tight_layout()
fig.savefig('05_output/obs/fig/boxplot_sep_oct_2018_Urban_park.pdf',
            bbox_inches='tight', facecolor='w')

#%% NO2 and NO relationship for Appendix dissertation -----------------------------------------
obs18['day'] = obs18.index.day
obs18['hour'] = obs18.index.hour
by_month= obs18.groupby(['day','hour','type']).mean()[['no','no2']].reset_index()
by_month = by_month.loc[(~by_month.type.isin(['Coastal urban', 'Industry', 'Regional urban']))]

# Figure
plt.style.use('seaborn')
day = np.array([8,9,10,11,12,13,14,15,16,17])
night = np.array([20,21,22,23,0,1,2,3,4,5])
df_day = by_month[by_month.hour.isin(day)]
groups = df_day.groupby('type')
# Plot
fig, ax = plt.subplots(1,2,sharey=True,figsize=(8,4),gridspec_kw={'wspace': 0.1})
color = cm.Set1 # see how put this on the figure 
ax[0].margins(0.05) # Optional, just adds 5% padding to the autoscaling
for name, group in groups: # name is ok for groupby, to verify print(name) and print(group) to understand
    ax[0].plot(group.no, group.no2, marker='.',  # be careful with the marker = '+' doesn't work for all plt.style
            linestyle='', ms=10, label=name, alpha=.7)
    ax[0].set_xlabel('NO ($\mu$g m$^{-3}$)')
    ax[0].set_ylabel('NO$_2$ ($\mu$g m$^{-3}$)')
    ax[0].set_xlim([-1,100])
ax[0].legend(loc='upper center', bbox_to_anchor=(1, -0.15), ncol = 3)
ax[0].set_title('Daytime (8-17 h)')

night = np.array([20,21,22,23,0,1,2,3,4,5])
df_night = by_month[by_month.hour.isin(night)]
groups = df_night.groupby('type')
# Plot
color = cm.Set1 # see how put this on the figure 
ax[1].margins(0.05) # Optional, just adds 5% padding to the autoscaling
for name, group in groups: # name is ok for groupby, to verify print(name) and print(group) to understand
    ax[1].plot(group.no, group.no2, marker='.',  # be careful with the marker = '+' doesn't work for all plt.style
            linestyle='', ms=10, label=name, alpha = .7)
    ax[1].set_xlabel('NO ($\mu$g m$^{-3}$)')
    ax[1].set_xlim([-1,100])
    #ax[1].set_ylabel('NO$_2$ ($\mu$g m$^{-3}$)')
ax[1].set_title('Night-time (20-5 h)')
fig.savefig("dissertation/fig/NoNo2_ratio.pdf",bbox_inches='tight')

#%% Variation by daily profile
# Style of the Canvas
plt.style.use('seaborn-whitegrid')
sns.set_style("ticks")
by_type = 'Urban'
aqData = obs18[obs18.type == by_type]
# Data
Mean = aqData.groupby(aqData.index.hour).mean()[['co','no','no2','o3']]
Max = aqData.groupby(aqData.index.hour).max()[['co','no','no2','o3']]
Min = aqData.groupby(aqData.index.hour).min()[['co','no','no2','o3']]
SD  = aqData.groupby(aqData.index.hour).std()[['co','no','no2','o3']]
# Design
fig= plt.figure(figsize=(6,4))

ax1 = fig.gca()
plt.xticks(np.arange(0,24,1))
ax1.grid(False)
alpha = 0.1
ax1.fill_between(SD.index, Mean.o3+SD.o3, Mean.o3-SD.o3, color='b', alpha=alpha)
ax1.plot(Mean.index,Mean.o3, color='b', label='Ozone',lw=3, marker = 'o')
ax1.fill_between(Mean.index, Mean.no+SD.no, Mean.no-SD.no, color='darkorange', alpha=alpha)
ax1.plot(Mean.index,Mean.no, color='darkorange', label='NO',lw=3)
ax1.fill_between(Mean.index, Mean.no2+SD.no2, Mean.no2-SD.no2, color='r', alpha=alpha)
ax1.plot(Mean.index,Mean.no2, color='r', label='NO$_2$', lw=3)
ax1.set_ylabel('1-hr mean of surface Ozone, NO and NO$_2$ ($\mu$g m$^{-3}$)')
ax1.legend(loc='upper left', ncol = 3) #bbox_to_anchor=(0.5, -0.15)
ax1.tick_params(axis="x", direction="in",length=3, width=1, colors='gray')
ax1.tick_params(axis="y", direction="in",length=3, width=1, colors='gray')
ax1.set_ylim(0, 140)
ax1.set_title(by_type, loc='left')

ax2 = ax1.twinx()
ax2.tick_params(axis="y", direction="in",length=3, width=1, colors='gray')
ax2.fill_between(Mean.index, Mean.co-SD.co, Mean.co+SD.co, color='g', alpha=alpha)
ax2.plot(Mean.index,Mean.co, color='g', label='CO',lw=3)
ax2.set_ylabel('CO (ppm)')
ax2.set_ylim(0.1, 1.5)

ax2.yaxis.label.set_color('g')
ax2.legend(loc='upper right', ncol = 3) #bbox_to_anchor=(0.5, -0.20)
ax1.set_xlabel('Hour of the day (local time) for September and October (2018)')
fig.savefig("05_output/obs/fig/aqHourSep_"+by_type+".pdf",bbox_inches='tight')




