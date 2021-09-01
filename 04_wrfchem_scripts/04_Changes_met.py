#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 20:26:03 2021

@author: adelgado
"""

import pandas as pd
import os, fnmatch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib as mpl
import pickle as pkl
import functions.mod_eval as mev

#%% Import stations -----------------------------------------------------------
mod = pd.read_pickle('01_data/processed/mod/mod_all_scen.pkl')
print(mod.info())

#%%  Only met 

station_types = ['Regional urban', 'Industry', 'Forest preservation',
                 'Urban', 'Urban park']
parameters = ['local_date','station','Mday','type','tc','rh','ws','wd',
              'tc_rcp45', 'rh_rcp45','ws_rcp45', 'wd_rcp45',
              'tc_rcp85', 'rh_rcp85', 'ws_rcp85', 'wd_rcp85']
met = mod[parameters]
met.loc[:,'Mday'] = met.local_date.dt.strftime('%b-%d %H:00')
met.set_index('local_date',inplace=True)
#met.to_csv('met_rcp_changes.csv') # useful for R to build Wind Rose plots.
print(met)

#%% Figures by meteorological parameter --------------------------------------

# Temperature
mev.plot_type(met, alpha=.15, para='tc', ylabel='2-m Temp. [ºC]',
              filename='tc_change', station_types=station_types, 
              n_yticks = 4,
              path = '05_output/wrfchem/fig/')

# Relative humidity
mev.plot_type(met, alpha=.15, para='rh', ylabel='2-m RH [%]',
              filename='rh_change', station_types = station_types, 
              n_yticks = 4,
              path = '05_output/wrfchem/fig/')

# Wind speed
mev.plot_type(met, alpha=.15, para='ws', ylabel='10-m Wind Speed [ms$^{-1}$]',
              filename='ws_change', 
          station_types=station_types, n_yticks = 4,
          path = '05_output/wrfchem/fig/')


#%% Figure by station as monthly mean and by scenario
met_2 = met.copy().reset_index()
met_2.loc[:,'Month'] = met_2.local_date.dt.strftime('%b')
fig, ax = plt.subplots(2,figsize=(8,6), sharex= True, gridspec_kw={'hspace':0.07})
for i, m in enumerate(['Sep','Oct']):
    df = met_2.loc[met_2.Month == m].groupby(['station']).mean()[['tc','tc_rcp45','tc_rcp85']]
    df.plot(rot=90, ax=ax[i], style=['go','co','ro'], markersize = 4.5, markeredgecolor = '0.4')
    ax[i].legend(['Current ('+m+'. 2018)','RCP 4.5 ('+m+'. 2030)','RCP 8.5 ('+m+'. 2030)'], fontsize=7, ncol=3)
    ax[i].set_ylabel('2-m temp. [ºc]')
    xtick_labels = list(df.index)
    ax[i].set_xticks(range(len(xtick_labels)))
    ax[i].set_ylim(18,30)
    ax[i].grid(color='0.9', linestyle='-', linewidth=1)
    ax[i].set_xticklabels(xtick_labels, rotation='vertical', fontdict={'fontsize':7})
    ax[0].text(0, 28, '(a)', fontsize=18)
    ax[1].text(0, 28, '(b)', fontsize=18)
fig.savefig('dissertation/fig/temp_sep_oct.pdf',bbox_inches='tight', facecolor='w')

#%% Increase of Temperature
# September
tc_incr = met_2.loc[met_2.Month =="Sep"].groupby(['station']).mean()[['tc','tc_rcp45','tc_rcp85']].round(2)
mean = np.around((tc_incr['tc_rcp45'] - tc_incr['tc']).mean(), 2)
sd = np.around((tc_incr['tc_rcp45'] - tc_incr['tc']).std(), 2)
print(f"Temperature increase Sep RCP4.5: {mean} +/- {sd} ")

# October
tc_incr = met_2.loc[met_2.Month =="Oct"].groupby(['station']).mean()[['tc','tc_rcp45','tc_rcp85']].round(2)
mean = np.around((tc_incr['tc_rcp45'] - tc_incr['tc']).mean(), 2)
sd = np.around((tc_incr['tc_rcp45'] - tc_incr['tc']).std(), 2)
print(f"Temperature increase Oct RCP4.5: {mean} +/- {sd} ")

# September
tc_incr = met_2.loc[met_2.Month =="Sep"].groupby(['station']).mean()[['tc','tc_rcp45','tc_rcp85']].round(2)
mean = np.around((tc_incr['tc_rcp85'] - tc_incr['tc']).mean(), 2)
sd = np.around((tc_incr['tc_rcp85'] - tc_incr['tc']).std(), 2)
print(f"Temperature increase Sep RCP8.5: {mean} +/- {sd} ")

# October
tc_incr = met_2.loc[met_2.Month =="Oct"].groupby(['station']).mean()[['tc','tc_rcp45','tc_rcp85']].round(2)
mean = np.around((tc_incr['tc_rcp85'] - tc_incr['tc']).mean(), 2)
sd = np.around((tc_incr['tc_rcp85'] - tc_incr['tc']).std(), 2)
print(f"Temperature increase Oct RCP8.5: {mean} +/- {sd} ")

#%% Increase or decrease of relative humidity

# September
tc_incr = met_2.loc[met_2.Month =="Sep"].groupby(['station']).mean()[['rh','rh_rcp45','rh_rcp85']].round(2)
mean = np.around((tc_incr['rh_rcp45'] - tc_incr['rh']).mean(), 2)
sd = np.around((tc_incr['rh_rcp45'] - tc_incr['rh']).std(), 2)
print(f"Rh increase Sep RCP4.5: {mean} +/- {sd} ")

# October
tc_incr = met_2.loc[met_2.Month =="Oct"].groupby(['station']).mean()[['rh','rh_rcp45','rh_rcp85']].round(2)
mean = np.around((tc_incr['rh_rcp45'] - tc_incr['rh']).mean(), 2)
sd = np.around((tc_incr['rh_rcp45'] - tc_incr['rh']).std(), 2)
print(f"Rh increase Oct RCP4.5: {mean} +/- {sd} ")

# September
tc_incr = met_2.loc[met_2.Month =="Sep"].groupby(['station']).mean()[['rh','rh_rcp45','rh_rcp85']].round(2)
mean = np.around((tc_incr['rh_rcp85'] - tc_incr['rh']).mean(), 2)
sd = np.around((tc_incr['rh_rcp85'] - tc_incr['rh']).std(), 2)
print(f"Rh increase Sep RCP8.5: {mean} +/- {sd} ")

# October
tc_incr = met_2.loc[met_2.Month =="Oct"].groupby(['station']).mean()[['rh','rh_rcp45','rh_rcp85']].round(2)
mean = np.around((tc_incr['rh_rcp85'] - tc_incr['rh']).mean(), 2)
sd = np.around((tc_incr['rh_rcp85'] - tc_incr['rh']).std(), 2)
print(f"RH increase Oct RCP8.5: {mean} +/- {sd} ")

#%% Figure of Relative humidity as monthly mean by station ------------------------
fig, ax = plt.subplots(2,figsize=(8,6), sharex= True, gridspec_kw={'hspace':0.07})
for i, m in enumerate(['Sep','Oct']):
    df = met_2.loc[met_2.Month == m].groupby(['station']).mean()[['rh','rh_rcp45','rh_rcp85']]
    df.plot(rot=90, ax=ax[i], style=['go','co','ro'], markersize = 4.5, markeredgecolor = '0.4')
    ax[i].legend(['Current ('+m+'. 2018)','RCP 4.5 ('+m+'. 2030)','RCP 8.5 ('+m+'. 2030)'], fontsize=7, ncol=3)
    ax[i].set_ylabel('2-m relative humidity [%]')
    xtick_labels = list(df.index)
    ax[i].set_xticks(range(len(xtick_labels)))
    ax[i].set_ylim(45,90)
    ax[i].grid(color='0.9', linestyle='-', linewidth=1)
    ax[i].set_xticklabels(xtick_labels, rotation='vertical', fontdict={'fontsize':7})
    ax[0].text(0, 82, '(a)', fontsize=18)
    ax[1].text(0, 82, '(b)', fontsize=18)
fig.savefig('dissertation/fig/rh_sep_oct.pdf',bbox_inches='tight', facecolor='w')

for m in ['Sep', 'Oct']:
    rh_incr = met_2.loc[met_2.Month == m].groupby(['station']).mean()[['rh','rh_rcp45','rh_rcp85']].round(2)
    mean = np.around((rh_incr['rh_rcp85'] - rh_incr['rh']).mean(), 2)
    sd = np.around((rh_incr['rh_rcp85'] - rh_incr['rh']).std(), 2)
    print("RH decrease " + m + f": {mean} +/- {sd}")

#%% Rain conditions -----------------------------------------------------------
rain_mod = pd.read_pickle('01_data/processed/mod/rain_mod.pkl')

#%% Figure of rainy conditions by station types
fig, ax = plt.subplots(len(station_types), figsize=(6,8), 
                       sharex=True, gridspec_kw={'hspace':0.3})
alpha = .2

for i,t in enumerate(station_types):
    mean = rain_mod[rain_mod.type == t].resample('D').mean()
    mean.plot(y=['rr','rr_rcp45','rr_rcp85'],style=['g','c','#D22523'],
                  lw=3, alpha=.7,ax=ax[i], legend=False)
    std = rain_mod[rain_mod.type == t].resample('D').std()
    ax[i].fill_between(mean.index, mean['rr']+std['rr'], mean['rr']-std['rr'], color='g', alpha=alpha)
    ax[i].fill_between(mean.index, mean['rr_rcp45']+std['rr_rcp45'], mean['rr_rcp45']-std['rr_rcp45'], 
                       color='c', alpha=alpha)
    ax[i].fill_between(mean.index, mean['rr_rcp85']+std['rr_rcp85'], 
                           mean['rr_rcp85']-std['rr_rcp85'], color='#D22523', alpha=alpha)
    ax[i].set_title(t,size=8, loc='left')
    ax[0].xaxis.set_major_formatter(md.DateFormatter('%d'))
    ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,31,4)))
    ax[0].xaxis.set_minor_locator(md.MonthLocator())
    ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n%b'))
    ax[i].yaxis.set_major_locator(plt.MaxNLocator(6))
    ax[2].set_ylabel('Daily total rain mean by station type [mm]')
    ax[1].legend(['2018', "RCP 4.5 (2030)","RCP 8.5 (2030)"], fontsize=6, loc=2,
                                       ncol = 3)
    ax[i].set_xlabel('Local Time')

    fig.savefig('dissertation/fig/rain_change_all.pdf', bbox_inches='tight', facecolor='w') 

#%% Figure of rainy conditions at the IAG Climatological station

fig,ax = plt.subplots()
rain_mod[rain_mod.name =='IAG'].plot(y=['rr','rr_rcp45','rr_rcp85'], ax= ax,
                                    style=['g','c','#D22523'],lw=3)
ax.xaxis.set_major_formatter(md.DateFormatter('%d'))
ax.xaxis.set_major_locator(md.DayLocator(np.arange(0,31,4)))
ax.xaxis.set_minor_locator(md.MonthLocator())
ax.xaxis.set_minor_formatter(md.DateFormatter('\n%b'))
ax.yaxis.set_major_locator(plt.MaxNLocator(6))
ax.set_ylabel('Daily total rain [mm]')
ax.set_xlabel('Local Time')
ax.legend(['2018', "RCP 4.5 (2030)","RCP 8.5 (2030)"], fontsize=6, loc=2,
                                       ncol = 1)
fig.savefig('dissertation/fig/rain_change_iag.pdf', bbox_inches='tight', facecolor='w')

#%% Figure of rainy conditions by month
rain_iag = rain_mod[rain_mod.name =='IAG'].drop('code',axis=1).loc['2018-09-01':,:]

fig, ax = plt.subplots()
rain_iag.groupby(rain_iag.index.month).sum().plot(kind='bar',y=['rr','rr_rcp45','rr_rcp85'],
                                                  color=['g','c','#D22523'], 
                                                  label=['Current (2018)','RCP 4.5 (2030)','RCP 8.5 (2030)'],
                                                  rot=0, 
                                                  xlabel='Month', 
                                                  ylabel='Rain rate [mm]',
                                                  edgecolor='k', ax=ax)
ax.set_xticklabels(['September','October'])
ax.legend(ncol=1, fontsize=7)
fig.savefig('dissertation/fig/rain_bymonth.pdf',bbox_inches='tight', facecolor='w')


