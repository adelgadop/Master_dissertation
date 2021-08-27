#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 10:51:40 2021

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


#%% Meteorological simulations for the IAG climatological station ------------------
# Import observations
iag_obs = pkl.load(open('01_data/processed/obs/iag_met.pkl',"rb")).drop(['name','code'],axis=1)


# Import data extracted using wrf_rain.py from WRF
paths = [i for i in sorted(glob.glob('01_data/processed/model/rain/*.pickle'))]
rain = {}
files = ['sep2018','oct2018','rcp4.5sep2030','rcp8.5sep2030','rcp4.5oct2030','rcp8.5oct2030']
for p, f in zip(paths, files):
    rain[f] = pkl.load(open(p, "rb"))

#%% Rain simulations at the IAG Climatological station

IAG_rain_mod = pd.concat([rain['sep2018']['IAG'],rain['oct2018']['IAG']]).set_index('local_date')[['rainc','rainnc']]
IAG_rain_mod['total_accum'] = IAG_rain_mod.rainc + IAG_rain_mod.rainnc
prev_total = [IAG_rain_mod.rainc[i]+IAG_rain_mod.rainnc[i] if i == 0 else 
              IAG_rain_mod.rainc[i-1]+IAG_rain_mod.rainnc[i-1] for i in range(len(IAG_rain_mod.index))]
IAG_rain_mod['prev_total'] = prev_total
IAG_rain_mod['rr'] = IAG_rain_mod.total_accum - IAG_rain_mod.prev_total
IAG_rain_mod.loc[IAG_rain_mod.rr < 0] = 0
IAG_rain_mod.rr.plot(xlabel='Local time')

#%% Import other meteorological parameters belonging to the IAG station

mod_sep18 = pd.read_csv('01_data/processed/model/Y2018/sep18/0_FIN_d02.csv')
mod_sep18.loc[:,'date'] = pd.to_datetime(mod_sep18['date'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
mod_sep18.loc[:,'local_date']=mod_sep18['date'].dt.tz_convert('America/Sao_Paulo')
mod_sep18.drop('date', axis=1, inplace=True)
mod_sep18.set_index('local_date', inplace=True)
mod_sep18 = mod_sep18.loc['2018-09':'2018-09-30 23:00',:]

mod_oct18 = pd.read_csv('01_data/processed/model/Y2018/oct18/0_FIN_d02.csv')
mod_oct18.loc[:,'date'] = pd.to_datetime(mod_oct18['date'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
mod_oct18.loc[:,'local_date']=mod_oct18['date'].dt.tz_convert('America/Sao_Paulo')
mod_oct18.drop('date', axis=1, inplace=True)
mod_oct18.set_index('local_date', inplace=True)
mod_oct18 = mod_oct18.loc['2018-10':'2018-10-31 20:00',:]

mod_iag = pd.concat([mod_sep18, mod_oct18])

#%% Join rain and other parameters in one pandas DataFrame

iag_mod = pd.merge(mod_iag, IAG_rain_mod,
                   right_index=True, 
                   left_index=True).drop(['rainc', 'rainnc',
                                          'total_accum', 'prev_total',
                                          'o3','no','no2','co','code','name'], axis=1)
#%% Simulation vs Observations ------------------------------------------------------

iag_met = pd.merge(iag_obs, iag_mod, left_index=True, right_index=True, suffixes=('_obs', '_mod'))
iag_met.loc[:,'station'] = 'IAG'
iag_met.loc[:,'code'] = 0
iag_met.loc[:,'type'] = 'Forest preservation'

#%% Figure by parameter
fig, ax= plt.subplots(5, figsize=(10,8),sharex=True)
iag_met.plot(y=['tc_obs','tc_mod'], ax=ax[0], style=['.k','-g'],ylabel='2-m Temp. [ºC]', legend = False,
            markersize = 2)
iag_met.plot(y=['rh_obs','rh_mod'], ax=ax[1], style=['.k','-g'],ylabel='2-m RH [%]',legend = False,
            markersize = 2)
iag_met.plot(y=['rr_obs','rr_mod'], ax=ax[2], style=['.k','-g'], ylabel='rain rate [mm]',legend = False,
            markersize = 2)
iag_met.plot(y=['ws_obs','ws_mod'], ax=ax[3], style=['.k','-g'],ylabel='10-m WS [m/s]',legend = False,
            markersize = 2)
iag_met.plot(y=['wd_obs','wd_mod'], ax=ax[4], style=['.k','-g'],ylabel='10-m WD [degree]',legend = False,
            markersize = 2)
ax[4].set_xlabel('Local Time')
ax[2].legend(['Obs', 'Mod'])

fig.savefig('05_output/evaluation/fig/met_IAG_comparison.pdf', 
            bbox_inches='tight', facecolor='w')
fig.savefig('dissertation/fig/met_IAG_comparison.pdf', 
            bbox_inches='tight', facecolor='w')

#%% Figure for rainfall
fig, ax = plt.subplots(figsize=(6,3))
iag_met.resample('D').sum().plot(y=['rr_obs','rr_mod'], style=['k','g'], ax=ax, lw=2)
ax.set_xlabel('Local Time')
ax.set_ylabel('Daily total rain [mm]')
ax.legend(['Obs','Mod'])
fig.savefig('dissertation/fig/iag_daily_rain.pdf',bbox_inches='tight', facecolor='w')

#%% Statistical Evaluation ----------------------------------------------------------------------
# IAG station

stats_df1 = ms.met_stats(iag_met,mets=['tc', 'rh','rr','ws','wd']).round(2)

para = ['tc','rh','ws','rr']
df_1 = pd.DataFrame(index=['t-stat', 't-crit'])

for p in para:
    df_1[p] = ms.r_pearson_sig(n=stats_df1.loc[p,'n'],
                             r=stats_df1.loc[p,'r'],
                             deg_free=stats_df1.loc[p,'n']-2,
                             alpha=0.05)
df_1 = df_1.round(2).T
print(df_1)

stats = pd.concat([stats_df1, df_1], axis =1).T


print(stats.to_latex(caption='Statistical results for meteorological parameters for Sep-Oct 2018 (IAG/USP station)',
                         label='tab:stats_iag'),
      file=open('05_output/evaluation/tab/stats_iag.tex','w'))

#%% Simulations CETESB stations + IAG station

met = pd.read_pickle('01_data/processed/all_data.pkl')\
            .set_index('local_date')\
            .drop_duplicates()
        

station_types = list(met.type.unique())
parameters = ['station','type','tc_obs','rh_obs','ws_obs','wd_obs',
              'tc_mod', 'rh_mod','ws_mod', 'wd_mod']
met = met[parameters]
met.loc[met.wd_obs > 360,'wd_obs'] = np.nan

# Export data with correction of wind direction
met.to_csv('01_data/processed/met_obs_mod_all.csv')

#%% Figures by meteorological parameter and station type ------------------------------------

def plot_type(met,alpha,para, ylabel,filename, station_types, n_yticks, path='./'):
    fig, ax = plt.subplots(len(station_types), figsize=(6,8),sharex=True,gridspec_kw={'hspace':.25})
    for i,t in enumerate(station_types):
        mean = met[met.type == t].resample('D').mean()
        mean.plot(y=[para+'_obs',para+'_mod'],style=['k','g'],
                  lw=3, alpha=.7,ax=ax[i], legend=False)
        std = met[met.type == t].resample('D').std()
        ax[i].fill_between(mean.index, mean[para+'_obs']+std[para+'_obs'], 
                           mean[para+'_obs']-std[para+'_obs'], color='k', alpha=alpha)
        ax[i].fill_between(mean.index, mean[para+'_mod']+std[para+'_mod'], 
                           mean[para+'_mod']-std[para+'_mod'], color='g', alpha=alpha)
        ax[i].set_title(t,size=8, loc='left')
        #ax[0].xaxis.set_major_formatter(md.DateFormatter('%d'))
        #ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,31,2)))
        #ax[0].xaxis.set_minor_locator(md.MonthLocator())
        #ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n%b'))
        ax[i].yaxis.set_major_locator(plt.MaxNLocator(n_yticks))
        ax[2].set_ylabel(ylabel)
        ax[len(station_types)-1].legend(['Obs.', "Mod."], fontsize=5,
                                       ncol = 2)
        ax[i].set_xlabel('Local Time')
    fig.savefig(path+filename+'.pdf', bbox_inches='tight', facecolor='w')
    

#%% Temperature
path = '05_output/evaluation/fig/'

plot_type(met, 
          alpha=0.2, 
          para='tc', 
          ylabel='2-m Temp. [ºC]', 
          station_types=station_types,
          n_yticks = 4, 
          filename='temp_cetesb_iag', 
          path= path)

#%% Relative humidity

plot_type(met, 
          alpha=0.2, 
          para='rh', 
          ylabel='2-m Relative Humidity [%]', 
          station_types=station_types,
          n_yticks = 4, 
          filename='rh_cetesb_iag', 
          path = path)

#%% Wind speed

plot_type(met, 
          alpha=0.2, 
          para='ws', 
          ylabel='10-m Wind Speed [ms$^{-1}$] \n', 
          station_types=station_types,
          n_yticks = 4, 
          filename='ws_cetesb_iag', 
          path = path)

#%% Statistical evaluations of all stations ----------------------------------------------

start_remove = pd.to_datetime('2018-09-14').tz_localize('America/Sao_Paulo')
end_remove = pd.to_datetime('2018-09-16').tz_localize('America/Sao_Paulo')

met = met.loc[(met.index < start_remove) | (met.index > end_remove)]
    

stats_df1 = ms.met_stats(met,mets=['tc', 'rh','ws','wd']).round(2)

# Significant relation

para = ['tc','rh','ws']
df_1 = pd.DataFrame(index=['t-statistic', 't-critical'])

for p in para:
    df_1[p] = ms.r_pearson_sig(n=stats_df1.loc[p,'n'],
                             r=stats_df1.loc[p,'r'],
                             deg_free=stats_df1.loc[p,'n']-2,
                             alpha=0.05)
    
df_1.round(2)
for p in para:
    df_1.loc['n',p] = stats_df1.loc[p,'n']
    
df_1 = df_1.rename(columns={'tc':'Temp.','rh':'Rel. Hum.', 'ws':'W. Speed'})
print(df_1.round(2))

print(stats_df1.to_latex(caption='Statistical results for meteorological parameters for Sep-Oct 2018 (all stations)',
                            label='tab:stats_all'),
      file=open('05_output/evaluation/tab/stats_met_all.tex','w'))

#%% By station type
stats_type = {}
sta_df = pd.DataFrame()
for i in station_types:
    stats_type[i] = (ms.met_stats(met[met.type.isin([i])],mets=['tc','rh','ws','wd']))
    stats_type[i]['type'] = (i)
    df = stats_type[i]
    sta_df = pd.concat([sta_df,df]).round(2)
    
print(sta_df.to_latex(caption='Statistical results for meteorological parameters for Sep-Oct 2018 by type',
                            label='tab:stats_all_type'),
      file=open('05_output/evaluation/tab/stats_met_all_type.tex','w'))










