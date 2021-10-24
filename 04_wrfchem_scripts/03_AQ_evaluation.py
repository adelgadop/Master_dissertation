#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 11:41:18 2021

@author: adelgado
"""

# import necessary libraries

import numpy as np
import pandas as pd
#from netCDF4 import Dataset
import matplotlib.pyplot as plt
import glob
import pickle as pkl
import scipy
import statsmodels.api as sm
import matplotlib.dates as md
import functions.mod_stats as ms
import functions.mod_eval as mev

#%% Import data

all_data = pd.read_pickle('01_data/processed/all_data.pkl')

# Remove data for specific dates
start_remove = pd.to_datetime('2018-09-14').tz_localize('America/Sao_Paulo')
end_remove = pd.to_datetime('2018-09-16').tz_localize('America/Sao_Paulo')
data = all_data.loc[(all_data.local_date < start_remove) | (all_data.local_date > end_remove)]
data.set_index('local_date', inplace = True)
data.loc[:,'month'] = data.index.month

#%% Import stations
stations = pd.read_csv('01_data/stations.csv')
not_stations = ['Santos',
                'Santos-Ponta da Praia',
                'Cubatão-Centro',
                'Cubatão-Vale do Mogi',
                'Cubatão-V.Parisi']
stations = stations.loc[(~stations.name.isin(not_stations)) & \
                        (stations.domain =='d02')]\
            .drop('domain', axis=1).sort_values(by='code')
stations.index = stations.code
print(stations.head())

#%% Hourly mean by station type
by_type = data.groupby(['local_date','type']).mean().reset_index().drop(['code'], axis=1)

#%% Statistical evaluation -----------------------------------------------------------

sep18 = data.loc[data.month == 9, :]
oct18 = data.loc[data.month == 10, :]

stats = {}
months = ['Sep. 2018', 'Oct. 2018']
dic = {months[0]: sep18, months[1]: oct18}

for name, df in dic.items():
    stats[name] = ms.aq_stats(df, polls=['o3', 'no', 'no2', 'nox','co']).round(2).T
    
    cut_df = df.copy()
    cut_df.loc[cut_df.o3_obs < 80, 'o3_obs'] = np.nan
    stat = ms.aq_stats(cut_df, polls = ['o3']).round(2).T
    
    stats[name].loc['NMB 2', 'o3'] = stat.loc['NMB', 'o3']
    stats[name].loc['NME 2', 'o3'] = stat.loc['NME', 'o3']
    
  
gl_sta = pd.concat([ stats[months[0]], stats[months[1]] ], axis=1, keys= months)

print(gl_sta.to_latex(caption='Global statistical results for air quality parameter', label='tab: gl_st'),
      file=open('05_output/evaluation/tab/gl_sta.tex','w'))

#%% Ozone evaluation by station type

n_stats = ['n','MB', 'MAGE', 'RMSE', 'NMB', 'NME', 'IOA', 'r', 'Mm', 'Om', 'Msd', 'Osd']
some_stats = ['NMB', 'NME']
o3_stats = {}

for name, df in dic.items():
    o3_stats1 = mev.o3stats_by('type', df, n_stats, stations)
    
    cut_df = df.copy()
    cut_df.loc[cut_df.o3_obs < 80, 'o3_obs'] = np.nan
    o3_stats2 = mev.o3stats_by('type', cut_df, some_stats, stations)
    o3_stats[name] = pd.concat([o3_stats1, o3_stats2])


o3_sta = pd.concat([ o3_stats[months[0]], o3_stats[months[1]] ], axis = 1, keys = months)

print(o3_sta.to_latex(caption='Statistical results for surface ozone', 
                      label='tab: o3_sta'),
      file=open('05_output/evaluation/tab/o3_sta.tex','w'))

#%% Ozone evaluation by station

# Only considering a cutoff value of 80 for NMB and NME

sta_nam = {}
n_stats = ['n','MB', 'MAGE', 'RMSE', 'IOA', 'r', 'Mm', 'Om', 'Msd', 'Osd']

for name, df in dic.items():
    
    o3sta_df1 = mev.o3stats_by('station', df, n_stats, stations)[n_stats+['station', 'abb', 'type']]
    
    cut_df = df.copy()
    cut_df.loc[cut_df.o3_obs < 80, 'o3_obs'] = np.nan
    
    o3sta_df2 = mev.o3stats_by('station', cut_df, n_stats, stations)[some_stats+['station', 'abb', 'type']]
    
    sta_nam[name] = o3sta_df1.merge(o3sta_df2, on = ['station', 'abb', 'type'])
    sta_nam[name] = sta_nam[name][['n', 'MB', 'MAGE', 'RMSE', 'IOA', 'NMB', 'NME','r',
                                   'Mm', 'Om', 'Msd', 'Osd',  'station', 'abb', 'type']]
    
#%% Figure of correlation coefficient -----------------------------------------------------------

fig, ax = plt.subplots(2, figsize = (8,8), sharex = True, sharey = True)

for i, df in enumerate(sta_nam.values()):
    st = df.station
    
    df.plot(x = 'station', y = 'r', 
            style = 'ko-', label = 'r',
            ax = ax[i], legend = False, 
            rot = 90, xticks = np.arange(0,len(st)) # increase frequency of xlabels
            )
        
    ax[i].plot(st,[0.5 for i in st],'r-', label='Criteria', lw=0.5)
    ax[i].plot(st,[0.75 for i in st],'b-', label='Goal', lw=1)
    ax[i].set_title(months[i], loc = 'left', fontsize = 10)
    #ax[i].xaxis.set_major_locator()
    #ax[i].set_xticklabels(st, rot = 'vertical', fontsize=8)

    ax[0].legend()
    ax[i].grid(color='0.2', ls='--', lw=0.5,alpha=0.2)
    
fig.text(0.06, 0.5,'Correlation coefficient for surface ozone', ha = 'center', va = 'center',
         rotation = 'vertical')
fig.savefig('05_output/evaluation/fig/o3_r_by_station.pdf',bbox_inches='tight')

#%% Figure for main statistical parameters -------------------------------------------------------

for name, df_stat in zip(['sep18', 'oct18'], sta_nam.values()):
    fig, ax = plt.subplots(2,2, figsize=(14,6),sharex=True, gridspec_kw={'wspace':0.15})
    
    # Script
    NMB = df_stat.reset_index(drop=True).set_index('abb')[['NMB']]
    NMB['PG'] = 5
    NMB['NG'] = -5  
    NMB['PC'] = 15
    NMB['NC'] = -15
    # ax[0,0]
    NMB.NMB.plot.bar(rot=90,ax=ax[0,0], color='0.7',edgecolor='k', alpha=0.5, label = 'NMB')
    NMB['PG'].plot(rot=90,ax=ax[0,0], color='b',label = 'Goal (-5% $\leq$ NMB $\leq$ 5%)')
    NMB['NG'].plot(rot=90,ax=ax[0,0], color='b',label = '')
    NMB['PC'].plot(rot=90,ax=ax[0,0], color='r',label = 'Criteria (-15% $\leq$ NMB $\leq$ 15%)')
    NMB['NC'].plot(rot=90,ax=ax[0,0], color='r',label = '')
    ax[0,0].legend(fontsize=7)
    ax[0,0].set_ylabel('[%]')

    # ax[0,1]
    NME = df_stat.reset_index(drop=True).set_index('abb')[['NME']]
    NME['G'] = 15
    NME['C'] = 25
    NME.NME.plot.bar(rot=90, color='0.7', edgecolor='k', alpha = 0.5,ax=ax[0,1], label='NME')
    NME['G'].plot(rot=90,ax=ax[0,1], color='b',linestyle='--', label='Goal (NME $\leq$ 15%)')
    NME['C'].plot(rot=90,ax=ax[0,1], color='r',linestyle='--', label='Critera (NME $\leq$ 25%)')
    ax[0,1].legend(fontsize=7)
    ax[0,1].set_ylabel('[%]')

    # ax[1,0]
    r = df_stat.reset_index(drop=True).set_index('abb')[['r']]
    r['G'] = 0.75
    r['C'] = 0.50
    r.r.plot.bar(rot=90, color='0.7', edgecolor='k', alpha = 0.5,ax=ax[1,0])
    r['G'].plot(rot=90,ax=ax[1,0], color='b',linestyle='--', label='Goal (r $\geq$ 0.75)')
    r['C'].plot(rot=90,ax=ax[1,0], color='r',linestyle='--', label='Critera (r $\geq$ 0.50)')
    ax[1,0].set_ylabel('Correlation Coefficient')
    ax[1,0].set_ylim([0.4,1])
    ax[1,0].set_xlabel('Stations')
    ax[1,0].legend(fontsize=7)
    
    # ax[1,1]
    IOA = df_stat.reset_index(drop=True).set_index('abb')[['IOA']]
    IOA.IOA.plot.bar(rot=90, color='0.7', edgecolor='k', alpha = 0.5,ax=ax[1,1], label='IOA')
    ax[1,1].legend(fontsize=7)
    ax[1,1].set_ylim([0.5,1])
    ax[1,1].set_xlabel('Stations')

    fig.savefig('05_output/evaluation/fig/o3_stats_'+name+'.pdf',bbox_inches='tight', facecolor='w')
    fig.savefig('dissertation/fig/o3_stats_'+name+'.pdf',bbox_inches='tight', facecolor='w')
    
#%% Figure of MDA8  ---------------------------------------------------------------------------

# Rolling 8 hour mean fo ozone
mda8 = {}

for mes, df in dic.items():
    o3 = df[['station','type', 'o3_obs','o3_mod']]
    roll_o3 = {}
    rollo3 = pd.DataFrame() 
    for i in o3.station.unique():
        roll_o3[i] = (o3[o3.station == i].rolling(window=8).mean()[['o3_obs','o3_mod']])
        roll_o3[i]['station'] = (i)
        roll_o3[i]['type'] = (o3[o3.station == i].type)
        df = roll_o3[i]
        rollo3 = pd.concat([rollo3,df])
        rollo3['day'] = rollo3.index.day
    mda8[mes] = rollo3.groupby(['day','station','type']).max().reset_index().dropna()

#%% Figure of MDA8 by month
types = ['Forest preservation', 'Industry', 'Regional urban', 'Urban', 'Urban park']

for mes, MDA8 in zip(['sep18', 'oct18'], mda8.values()):
    
    fig, ax = plt.subplots(len(types),
                       figsize=(5,7),
                       sharey=True,
                       sharex=True,
                       gridspec_kw={'hspace':0.4})
    
    for i in range(len(types)):
        MDA8.loc[MDA8.type ==types[i]].groupby(['type','day'])\
            .mean().reset_index().set_index('day')\
                .plot(ax=ax[i], legend=False, grid=True, fontsize=10,
                      color='kg', lw=3, marker='.', alpha=.7)
        ax[i].set_title(types[i],size=8, loc='left')
        ax[i].set_ylim([0,200])
        if mes == 'sep18':
            ax[0].text(0,150, "(a)", fontsize='large')
        else:
            ax[0].text(0,150, "(b)", fontsize='large')
        ax[2].set_ylabel('O$_3$ [$\mu$g.m$^{-3}$]')
        if i == len(types)-1:
            ax[i].legend(['Obs','WRF-Chem'],fontsize=6)
            
    fig.savefig('dissertation/fig/MDA8_type_'+mes+'.pdf',bbox_inches='tight', facecolor='w')
    
#%% Figure of ozone as times series by type

mev.subplots2(all_data.set_index('local_date'), #[data.station.isin(gr_1)]
         pol='o3',
         ylabel='O$_3$ [$\mu$gm$^{-3}$]',
         xlabel='Local Time',
         suffixes=['_obs','_mod'],
         legend=['Obs','WRF-Chem'],
         size=(8,8),
         n_yticks=5,
         n_xticks=2,
         filename = 'dissertation/fig/Sep_Oct18_type',
         alpha=.5,
         markersize=3,
         lw=2,
         labelsize=7, 
         by='type')

#%% Figure of ozone as times series by type for the article

mev.subplots2(all_data.set_index('local_date'), #[data.station.isin(gr_1)]
         pol='o3',
         ylabel='O$_3$ [$\mu$gm$^{-3}$]',
         xlabel='Local Time',
         suffixes=['_obs','_mod'],
         legend=['Obs','WRF-Chem'],
         size=(10,10),
         n_yticks=5,
         n_xticks=2,
         filename = '../article/fig/Sep_Oct18_type',
         alpha=.5,
         markersize=3,
         lw=2,
         labelsize=7, 
         by='type')

#%% Figure by some stations

st_names = ['Pico do Jaraguá','Paulínia','Campinas-Taquaral','Carapicuíba','Ibirapuera']
df_plot = all_data[all_data.station.isin(st_names)]

mev.subplots2(df_plot.set_index('local_date'),
         pol='o3',
         ylabel='O$_3$ [$\mu$gm$^{-3}$]',
         xlabel='Local Time',
         suffixes=['_obs','_mod'],
         legend=['Obs','WRF-Chem'],
         size=(8,8),
         n_yticks=5,
         n_xticks=2,
         filename='05_output/evaluation/fig/Sep_Oct18_station',
         alpha=.8,
         markersize=4,
         lw=2,
         labelsize=6, 
         by='station')

#%% NO and NOx concentrations

mev.subplots2(df_plot.set_index('local_date'), #[data.station.isin(gr_1)]
         pol='no',
         ylabel='NO [$\mu$gm$^{-3}$]',
         xlabel='Local Time',
         suffixes=['_obs','_mod'],
         legend=['Obs','WRF-Chem'],
         size=(8,8),
         n_yticks=5,
         n_xticks=2,
         filename='05_output/evaluation/fig/Sep_Oct18_station',
         alpha=.7,
         markersize=3,
         lw=2,
         labelsize=6, 
         by='station')

mev.subplots2(df_plot.set_index('local_date'), #[data.station.isin(gr_1)]
         pol='nox',
         ylabel='NO$_x$ [$\mu$gm$^{-3}$]',
         xlabel='Local Time',
         suffixes=['_obs','_mod'],
         legend=['Obs','WRF-Chem'],
         size=(8,8),
         n_yticks=5,
         n_xticks=3,
         filename='dissertation/fig/Sep_Oct18_station',
         alpha=.7,
         markersize=3,
         lw=2,
         labelsize=6, 
         by='station')


#%% Figure of CO concentrations for some stations

sta_co = ['Carapicuíba', 'Guarulhos-Pimentas', 'Parque D.Pedro II',
          'S.José Campos-Jd.Satelite', 'Taubaté']

legend = ['Obs', 'WRF-Chem', 'Not analyzed']

co_df = all_data[['local_date','station', 'type', 'co_obs', 'co_mod']].set_index('local_date')

fig, ax = plt.subplots(len(sta_co), figsize = (10, 8), gridspec_kw={'hspace':0.35},
                       sharex = True, sharey = True)
for i, st in enumerate(sta_co):
    co_df.loc[co_df.station == st,:].plot(y = 'co_obs', 
                                          style = 'k.',
                                          markersize = 2.5,
                                          legend = False,
                                          ax = ax[i])
    co_df.loc[co_df.station == st,:].plot(y = 'co_mod', legend = False,
                                          style = 'g-', 
                                          lw = 3, ax = ax[i], alpha = 0.7)
    ax[2].set_ylabel('CO [ppm]')
    ax[0].xaxis.set_major_formatter(md.DateFormatter('%a-%d'))
    ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,60, 2)))
    ax[0].xaxis.set_minor_locator(md.MonthLocator())
    ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n\n\n%b-%y'))
    ax[i].yaxis.set_major_locator(plt.MaxNLocator(5))
    ax[i].tick_params(axis='both', which='minor', labelsize=6)
    ax[i].tick_params(axis='both', labelsize=6)
    ax[i].set_xlabel('Local Time')
    ax[i].axvspan('2018-09-14', '2018-09-16 01:00', 
           label="Not analyzed",facecolor="0", alpha=0.2)
    ax[i].set_title(st,size=8, loc='left')
    if i == 4:
        ax[i].legend(legend,fontsize=7, ncol = 3)
        
fig.savefig('05_output/evaluation/fig/Sep_Oct18_station_subplot_co.pdf',
            bbox_inches = 'tight', facecolor = 'w')

#%% Figure of CO concentrations by station type
legend = ['Obs', 'WRF-Chem', 'Not analyzed']

fig, ax = plt.subplots(3, 
                       figsize = (8, 6), gridspec_kw={'hspace':0.35},
                       sharex = True, sharey = True)

for i, t in enumerate(['Regional urban', 'Urban', 'Urban park']): # only in 3 station types are observations
    co_df.loc[co_df.type == t,:].plot(y = 'co_obs', 
                                          style = 'k.',
                                          markersize = 2.5,
                                          legend = False,
                                          ax = ax[i])
    co_df.loc[co_df.type == t,:].plot(y = 'co_mod', legend = False,
                                          style = 'g-', 
                                          lw = 3, ax = ax[i], alpha = 0.7)
    ax[1].set_ylabel('CO [ppm]')
    ax[0].xaxis.set_major_formatter(md.DateFormatter('%a-%d'))
    ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,60, 2)))
    ax[0].xaxis.set_minor_locator(md.MonthLocator())
    ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n\n\n%b-%y'))
    ax[i].yaxis.set_major_locator(plt.MaxNLocator(5))
    ax[i].tick_params(axis='both', which='minor', labelsize=6)
    ax[i].tick_params(axis='both', labelsize=6)
    ax[i].set_xlabel('Local Time')
    ax[i].axvspan('2018-09-14', '2018-09-16 01:00', 
           label="Not analyzed",facecolor="0", alpha=0.2)
    ax[i].set_title(t,size=8, loc='left')
    if i == 2:
        ax[i].legend(legend,fontsize=7, ncol = 3)
        
fig.savefig('05_output/evaluation/fig/Sep_Oct18_type_subplot_co.pdf',
            bbox_inches = 'tight', facecolor = 'w')
fig.savefig('dissertation/fig/Sep_Oct18_type_subplot_co.pdf',
            bbox_inches = 'tight', facecolor = 'w')

#%% Figure by hour of day
fig, ax = plt.subplots(3, sharex=True, figsize=(5,8))
types = ['Urban', 'Urban park','Forest preservation']
alpha = .1
lw = 2

for i, t in enumerate(types):
    df = data[data.type == t][['o3_mod', 'no_mod', 'no2_mod', 'co_mod']]
    mean = df.groupby(df.index.hour).mean()
    sd = df.groupby(df.index.hour).std()
    
    mean.plot(y=['o3_mod', 'no_mod', 'no2_mod'], 
              style=['-o','-','-s'], color=['b', 'darkorange','r'], lw=lw,
              ax=ax[i], legend=False)
    ax[i].fill_between(mean.index, mean.o3_mod+sd.o3_mod,mean.o3_mod-sd.o3_mod,
                       color='b',alpha=alpha )
    ax[i].fill_between(mean.index, mean.no_mod+sd.no_mod,mean.no_mod-sd.no_mod,
                       color='darkorange',alpha=alpha)
    ax[i].fill_between(mean.index, mean.no2_mod+sd.no2_mod,mean.no2_mod-sd.no2_mod,
                       color='r',alpha=alpha)
    ax[i].set_ylim(0,160)
    ax[i].set_title(t, loc='left', fontsize=8)
    ax[i].set_xlabel('Hours (Local Time)')
    plt.xticks(np.arange(0,24,3))
    
    
    ax2 = ax[i].twinx()
    mean.plot(y='co_mod', ax=ax2, style='-^g', lw=lw, legend=False)
    ax2.set_ylim(0,1)
    ax2.fill_between(mean.index, mean.co_mod+sd.co_mod,mean.co_mod-sd.co_mod,
                       color='g',alpha=alpha )
    if i ==1:
        ax[i].set_ylabel('O$_3$, NO, NO$_2$ [$\mu$gm$^{-3}$]')
        ax2.set_ylabel('CO [ppm]')
    if i == 2:
        ax[i].legend(['O$_3$','NO','NO$_2$'], ncol=3, fontsize=7, loc=2)
        ax2.legend(['CO'], fontsize=7, loc=1)
fig.savefig('05_output/wrfchem/fig/Variation_pol_day.pdf', 
            bbox_inches='tight', facecolor='w')
fig.savefig('dissertation/fig/Variation_pol_day.pdf', 
            bbox_inches='tight', facecolor='w')



