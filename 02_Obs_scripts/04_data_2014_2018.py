#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 21:02:55 2021

@author: adelgado
"""

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

data = pd.read_pickle('01_data/processed/obs/air_data_5years.pkl').set_index('local_date').drop('date', axis = 1)
data['type'] = [stations[stations.code == i].type.values[0] for i in data.code]
data['month'] = data.index.month
data['year'] = data.index.year
data = data[data.year < 2019]

stat_sp = ['Paulínia', 'Interlagos', 
             'Carapicuíba', 'Campinas-Taquaral',
             'Pico do Jaraguá', 'Sorocaba',
             'Parque D.Pedro II', 'Ibirapuera',
             'Itaquera', 'Pinheiros']

data = data[data.station.isin(stat_sp)]
print(data.station.unique())

print(data[data.wd > 360].wd.unique())
data.loc[data.wd > 360,'wd'] = np.nan

#%% Figure as boxplot
plt.style.use('default')
param = list(['o3','no','no2','co', 'tc', 'rh', 'ws', 'wd'])
label = ['O$_3$ [$\mu$g m$^{-3}$]','NO [$\mu$g m$^{-3}$]','NO$_2$ [$\mu$g m$^{-3}$]',
         'CO [ppm]','2-m Temp. [ºC]','2-m RH [%]', '10-m W. Speed [m/s]', '10-m W. Dir. [º]']

fig, ax = plt.subplots(len(param),figsize=(12,18),sharex=True)
for i, p in enumerate(param):
    #print(i, p)
    sns.boxplot(x='month',y=p,hue='type', data=data,ax=ax[i],whis=6,fliersize=0.5, linewidth=0.5)
    ax[i].get_legend().remove()
    ax[i].set_xlabel('')
    ax[i].set_ylabel(label[i])
    if i == len(param)-1:
        ax[i].legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), ncol = 3)
        ax[i].set_xlabel('Month (years 2014-2018)')
fig.savefig("dissertation/fig/Air_Met_boxplot.pdf",bbox_inches='tight', facecolor='w')

#%% Figure as boxplot as daily profile
Urban = data[data.type == 'Urban park'].station.unique()
Urban = data[data.station.isin(Urban)][['station','type', 'no','no2','co']]
Urban['hour'] = Urban.index.time

fig, axes = plt.subplots(2,2, figsize=(12,8)) # create figure and axes
ylabels = ['ppm', '$\mu$gm$^{-3}$','$\mu$gm$^{-3}$']
for i,el in enumerate(['co','no','no2']):
    a = Urban.boxplot(el, by="hour", ax=axes.flatten()[i], rot=90,sym='k+', grid=False)
    ax=axes.flatten()[i].set_ylabel(ylabels[i])
    #plt.setp(a['fliers'], markersize=3.0)

fig.delaxes(axes[1,1]) # remove empty subplot
plt.tight_layout()
fig.savefig('05_output/obs/fig/boxplot_2014_2018_Urban_park.pdf',
            bbox_inches='tight', facecolor='w')

#%% 
data = data[data.station.isin(stat_sp)] 
ozone= data[['type','station','tc','o3']].groupby([data.index,'type']).mean().reset_index('type')
ozone['day'] = ozone.index.day
ozone['hour'] = ozone.index.time
ozone['year'] = ozone.index.year
ozone['month'] = ozone.index.strftime('%b')
ozone['rollo3'] = ozone.o3.rolling(window=8).mean()
ozone = ozone.loc[ozone.year < 2019]
print(ozone)

ozone_types = [stations[stations.name == i].type.values[0] for i in stat_sp]
table = pd.DataFrame({'Type':ozone_types,
                      'Station':stat_sp}).sort_values(by='Type').reset_index(drop=True)
print(table.to_latex(caption='xx', index=False, label='tab:xx'),
      file=open('05_output/obs/tab/stations_5years.tex','w'))

#%% Ozone by daily profile,by month and station type
types = ozone.type.unique()
styles = ['-ok','-.k','-,k','-xk',
          '-+k','-vk','-^k','-<k',
          '->k','-sk','-dr','-hb']
months = ['Jan','Feb', 'Mar', 'Apr','May','Jun', 
          'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec']
some_months = ['Jan','Feb', 'Mar', 'Apr','May','Jun', 'Jul', 'Aug','Nov', 'Dec']

h_ticks = 4*60*60*np.arange(6)
fig, ax = plt.subplots(len(types), figsize=(6,9),sharex=True, sharey=True)
for i, t in enumerate(types):
    df_1 = ozone[ozone.type == t].groupby(['hour','month']).mean()['o3'].unstack().loc[::,months]
    df_1.loc[::,some_months].plot(ax=ax[i], legend=False, xticks=h_ticks, style=styles[:-2], alpha=.3,markersize=6)
    df_1.loc[::,['Sep','Oct']].plot(ax=ax[i], legend=False, xticks=h_ticks, style=styles[-2:], alpha=.9, lw=2)
    ax[i].set_title(t,size=10, loc='left')
    ax[i].set_xlabel('Hour (local time) of the day \n (hourly mean for years 2014-2018, group by month)')
    if i == 2:
        ax[i].set_ylabel('1-hr Mean Ozone ($\mu$g m$^{3}$)')
    if i == len(types)-1:
        ax[i].legend(loc='upper right', bbox_to_anchor=(1.25, 4), ncol = 1)

fig.savefig("dissertation/fig/o3_hourly_type_obs.pdf",bbox_inches='tight', facecolor='w')

#%% MDA8 Ozone between  
fig, ax = plt.subplots(len(types), figsize=(8,10),sharex=True, sharey=True)
for i,t in enumerate(types):
    ozone[ozone.type==t][['o3']].resample('H').mean().rolling(window=8).mean().resample('D').max()\
    .plot(ax=ax[i], style=['.-g'], lw=1, alpha=.4, legend=False, markersize=5)
    ax1 = ax[i].twinx()
    ozone[ozone.type==t][['tc']].resample('W').mean().plot(ax=ax1, style='p-r', alpha=.3,
                                                          lw=3, legend=False, markersize=4)
    ax[i].set_title(t,size=10, loc='left')
    ax[i].set_xlabel('Local Time')
    ax[i].tick_params(axis="x", direction="in",length=3, width=1, colors='gray')
    ax[i].xaxis.set_major_locator(md.MonthLocator(bymonth=range(1,13,1),bymonthday=1,interval=4))
    ax[i].xaxis.set_minor_locator(md.YearLocator(1, month=1, day=1))
    ax[i].xaxis.set_major_formatter(md.DateFormatter('%b'))
    ax[i].xaxis.set_minor_formatter(md.DateFormatter('\n%Y'))

    if i == 0:
        ax[i].legend(['Surface ozone (max.)'], loc=0, fontsize=12)
        ax1.legend(['2-m Temp. (mean)'], loc=3, fontsize=12)
    if i == 2:
        ax[i].set_ylabel('MAD8 Ozone ($\mu$g m$^{3}$)')
        ax1.set_ylabel('2-m Temperature (ºC)')
fig.savefig("dissertation/fig/ozone_2014_2018_series.pdf",bbox_inches='tight', facecolor='w')