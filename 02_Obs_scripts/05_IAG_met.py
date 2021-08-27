#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 15:46:11 2021

@author: adelgado
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pickle as pkl

#%% Functions

def met_process(para, data, file):
    """
    Processing from Excel to Pandas DataFrame.

    Parameters
    ----------
    para : String
        Meteorological parameters from IAG station list.
    data : pandas DataFrame
        Range of hourly time series.
    file : String
        Path  location where Excel file is saved.

    Returns
    -------
    Pandas DataFrame.

    """
    for k,v in para.items():
        if k == 'ws_kph':
            df = pd.read_excel(file,sheet_name=k).set_index('day').stack().reset_index()
            df.rename(columns={0:k},inplace=True)
            data[v] = (df[k]/3.6).round(2)
        elif k == 'sunshine':
            df = pd.read_excel(file,sheet_name=k).fillna(0).set_index('day').stack().reset_index()
            df.rename(columns={0:k},inplace=True)
            data[v] = df[k]
        elif k == 'wd_card':
            df = pd.read_excel(file, sheet_name=k).set_index('day').stack().reset_index()
            df.rename(columns={0:k}, inplace=True)
            directions = {'N':0, 'NNE':22.5,'NE':45,'ENE':67.5,'E':90,
                          'ESE':112.5,'SE':135,'SSE':157.5,'S':180,
                          'SSW':202.5,'SW':225,'WSW':247.5,'W':270,
                          'WNW':292.5,'NW':315,'NNW':337.5}
            data[v]=df[k].replace(directions)
            data.loc[data[v]=='C',v] = np.nan
            data[v].fillna(method='ffill', inplace=True)
        elif k == 'cloud':
            df = pd.read_excel(file,sheet_name=k)
            df['local_date'] = pd.to_datetime(df.iloc[:,:4]).dt.tz_localize('America/Sao_Paulo')
            df.rename(columns={'cloud_cover [tenths]':v}, inplace=True)
            data = data.merge(df[['local_date',v]],how='left')
        
        else:
            df = pd.read_excel(file, sheet_name=k).set_index('day').stack().reset_index()
            df.rename(columns={0:k},inplace=True)
            data[v] = df[k]
    data.set_index('local_date', inplace=True)
    return data

#%% Processing data

para = {'ws_kph':'ws',   'wd_card':'wd','temp_c':'tc',   'rh':'rh',
        'pres_mb':'pres','rain_mm':'rr','sunshine':'sun','cloud':'cc'}

files = ['01_data/iag_met/iag_sep18.xlsx', '01_data/iag_met/iag_oct18.xlsx']

# September 2018
date = pd.date_range('2018-09-01 00:00', '2018-09-30 23:00', 
                     tz='America/Sao_Paulo',freq='H')
data = pd.DataFrame({'local_date':date,'name':'IAG','code':0})

sep2018 = met_process(para=para, data=data, file=files[0])

# October 2018
date = pd.date_range('2018-10-01 00:00','2018-10-31 23:00', 
                     tz='America/Sao_Paulo',freq='H')
data = pd.DataFrame({'local_date':date,'name':'IAG','code':0})
oct2018 = met_process(para=para, data=data, file=files[1])

#%% Join both data

data = pd.concat([sep2018, oct2018])

# %% Figure of IAG by parameter

fig, ax = plt.subplots(figsize=(10,8))
plt.subplots_adjust(wspace=0.2, hspace=0.1)

y_labels = ['[ms$^{-1}$]','degree','[ºC]','[%]',
            '[hPa]','[mm]','[hour]','[tenths]']

colores = ['0.5','g','b','skyblue','m','c','orange','b']

axes = data.iloc[:,2:].plot(subplots=True,sharex=True, ax = ax, 
                            layout=(4,2), xlabel='Local time', 
                            color= colores, style='-', lw=0.5, markersize=2)
i = [0,0,1,1,2,2,3,3]
j = [0,1,0,1,0,1,0,1]

for i,j,l in zip(i,j,y_labels):
    axes[i,j].set_ylabel(l)
    
fig.savefig('05_output/obs/fig/IAG_met.pdf', 
            bbox_inches='tight', facecolor='w')


#%% Only rain rate
data.rr.plot(xlabel = 'Local time',ylabel = 'Rain rate [mm]')

#%% Rain rate with cloud cover for both months

fig, ax = plt.subplots(figsize=(10,5))
data.resample('D')\
    .agg({'rr':'sum','cc':'mean'})\
    .plot(ax=ax, secondary_y='cc',
          style=['-oc','-^b'], lw=1,
          legend=True, ylabel='total daily rain [mm]')
    
plt.ylabel('Cloud cover mean [tenths]')
ax.legend(['Daily rain'],loc=2)
plt.legend(['Cloud cover'],bbox_to_anchor=(0.2, 0.25))
ax.set_xlabel('Day')
fig.savefig('05_output/obs/fig/rain_cc_IAG.pdf', 
            bbox_inches='tight', facecolor='w')

#%% Rain rate with cloud cover for September
met_iag = data.loc[:'2018-09-30 23',:]

met_iag['day'] = met_iag.index.day
met_iag = met_iag[['day','rr','cc']].groupby('day').agg({'rr':'sum','cc':'mean'})
fig, ax = plt.subplots(figsize=(8,4))
plot_rr = met_iag.rr.plot(kind='bar', rot=0, color='c', edgecolor='k', label='Total daily rain', legend=True)
ax.legend(loc=2)
ax2 = ax.twinx()
met_iag.cc.plot(rot=0,ax=ax2, lw=1, color='b',marker='o',label='Daily mean cloud cover', legend=True)
ax2.legend(bbox_to_anchor=(0.38, 0.25))
ax.set_ylabel('rain [mm]')
ax2.set_ylabel('cloud cover [tenths]')
def highlight(indices,ax):
    i=0
    while i<len(indices):
        ax.axvspan(indices[i]-0.5, indices[i]+0.5, facecolor='0', edgecolor='none', alpha=.2)
        i+=1
highlight([13,14], plot_rr)

fig.savefig('../4_Draft_Report/Dissertation/fig/rain_cc.pdf', bbox_inches='tight')

#%% Export data as pickle

data.to_pickle('01_data/processed/obs/iag_met.pkl')




    