#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 18:40:39 2021

@author: adelgado
"""

# Import necessary libraries
from functools import reduce
import pandas as pd
import os, fnmatch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib as mpl
import pickle as pkl
import functions.mod_eval as mev

#%% Import data ----------------------------------------------------------------------------
# Observed data
cet_obs = pd.read_pickle('01_data/processed/obs/obs18.pkl')\
            .set_index('local_date')\
            .drop(['pm10', 'pm2.5'], axis = 1)
            
iag_obs = pkl.load(open('01_data/processed/obs/iag_met.pkl',"rb")).drop(['sun','cc'], axis = 1)
iag_obs['type'] = 'Forest preservation'
iag_obs.rename(columns = {'name': 'station'}, inplace = True)

# join cetesb and IAG stations in one DataFrame
obs = pd.concat([cet_obs, iag_obs]).reset_index()

#%% Modeled data

# Import stations
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

#%% Read the model data  -------------------------------------------------------------
Mod = {}
Dir = {'sep18': '01_data/raw/mod/Y2018/sep18/',
       'oct18': '01_data/raw/mod/Y2018/oct18/'}

for k, v in Dir.items():
    
    # List all the files in the directory
    files = fnmatch.filter(os.listdir(v), '*FIN_d02*')
    
    # As pandas DataFrame
    Mod[k] = pd.DataFrame()
    
    # Read each csv station as pandas DataFrame and join
    for file in files:
        df = pd.read_csv(v + file)
        Mod[k] = pd.concat([Mod[k], df])
 
    # Format all the imported data
    Mod[k] = Mod[k][Mod[k].code.isin(stations.code)]
    Mod[k]['station'] = [stations[stations.code == i].name.values[0] for i in Mod[k].code]
    Mod[k]['type'] = [stations[stations.code == i].type.values[0] for i in Mod[k].code]
    
    # Format the time
    Mod[k].loc[:,'date'] = pd.to_datetime(Mod[k]['date'], 
                                          format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
    Mod[k].loc[:,'local_date']=Mod[k]['date'].dt.tz_convert('America/Sao_Paulo')
    
    Mod[k].rename(columns={'name':'station'})
    Mod[k] = Mod[k][['local_date','code','station','type',
                     'tc','rh','ws','wd','o3','no','no2','co']]
    Mod[k]['nox'] = Mod[k].no + Mod[k].no2

# Join as DataFrame two months in one
mod = pd.concat([Mod['sep18'], Mod['oct18']])
mod.to_pickle('01_data/processed/mod/curr_data.pkl')

#%% Merge obs and mod data in one
data = obs.merge(mod, 
                on=['local_date','station','code','type'],
                suffixes=('_obs', '_mod'))

# Find duplicated and remove it
data = data[~(data.duplicated())]

#%% Export the all data --------------------------------------------------------------

# Review this part, something wrong
data.to_pickle('01_data/processed/all_data.pkl')
data.to_csv('01_data/processed/all_data.csv')

#%% Processing only simulation results -----------------------------------------------

# Current scenario
curr = pd.read_pickle('01_data/processed/mod/curr_data.pkl')
curr['Mday'] = curr.local_date.dt.strftime('%b-%d-%H')

#%% RCP4.5 scenario
# ---------------
Mod = {}
Dir = {'sep30': '01_data/raw/mod/RCP4.5/sep30/',
       'oct30': '01_data/raw/mod/RCP4.5/oct30/'}

for k, v in Dir.items():
    
    # List all the files in the directory
    files = fnmatch.filter(os.listdir(v), '*rcp45*.csv')
    
    # As pandas DataFrame
    Mod[k] = pd.DataFrame()
    
    # Read each csv station as pandas DataFrame and join
    for file in files:
        df = pd.read_csv(v + file)
        Mod[k] = pd.concat([Mod[k], df])
        
    # Format all the imported data
    Mod[k] = Mod[k][Mod[k].code.isin(stations.code)]
    Mod[k]['station'] = [stations[stations.code == i].name.values[0] for i in Mod[k].code]
    Mod[k]['type'] = [stations[stations.code == i].type.values[0] for i in Mod[k].code]
    
    # Format the time
    Mod[k].loc[:,'date'] = pd.to_datetime(Mod[k]['date'], 
                                          format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
    Mod[k].loc[:,'local_date']=Mod[k]['date'].dt.tz_convert('America/Sao_Paulo')
    
    Mod[k].rename(columns={'name':'station'})
    Mod[k] = Mod[k][['local_date','code','station','type',
                     'tc','rh','ws','wd','o3','no','no2','co']]
    Mod[k]['nox'] = Mod[k].no + Mod[k].no2
    Mod[k]['Mday'] = Mod[k].local_date.dt.strftime('%b-%d-%H')
    
# Join as DataFrame two months in one
rcp45 = pd.concat([Mod['sep30'], Mod['oct30']])

# End -----------


#%% RCP8.5 scenario
# ---------------
Mod = {}
Dir = {
       'sep30': '01_data/raw/mod/RCP8.5/sep30/',
       'oct30': '01_data/raw/mod/RCP8.5/oct30/'
       }

for k, v in Dir.items():
    
    # List all the files in the directory
    files = fnmatch.filter(os.listdir(v), '*rcp85*.csv')
    
    # As pandas DataFrame
    Mod[k] = pd.DataFrame()
    
    # Read each csv station as pandas DataFrame and join
    for file in files:
        df = pd.read_csv(v + file)
        Mod[k] = pd.concat([Mod[k], df])
        
    # Format all the imported data
    Mod[k] = Mod[k][Mod[k].code.isin(stations.code)]
    Mod[k]['station'] = [stations[stations.code == i].name.values[0] for i in Mod[k].code]
    Mod[k]['type'] = [stations[stations.code == i].type.values[0] for i in Mod[k].code]
    
    # Format the time
    Mod[k].loc[:,'date'] = pd.to_datetime(Mod[k]['date'], 
                                          format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
    Mod[k].loc[:,'local_date']=Mod[k]['date'].dt.tz_convert('America/Sao_Paulo')
    
    Mod[k].rename(columns={'name':'station'})
    Mod[k] = Mod[k][['local_date','code','station','type',
                     'tc','rh','ws','wd','o3','no','no2','co']]
    Mod[k]['nox'] = Mod[k].no + Mod[k].no2
    Mod[k]['Mday'] = Mod[k].local_date.dt.strftime('%b-%d-%H')

# Join as DataFrame two months in one
rcp85 = pd.concat([Mod['sep30'], Mod['oct30']])

# End -----------

#%% Merge the three scenarios of simulations (curr, rcp4.5, and rcp8.5)

by = ['Mday','station','code','type']
mod_all = rcp45.merge(rcp85,on=by,suffixes=('_rcp45', '_rcp85')).merge(curr, on=by)

# to pickle
mod_all.to_pickle('01_data/processed/mod/mod_all_scen.pkl')
mod_all.to_csv('01_data/processed/mod/mod_all_scen.csv')

#%% Rainy conditions from simulations by scenarios -------------------------
stations = pd.read_csv('01_data/stations.csv')
not_stations = ['Santos',
                'Santos-Ponta da Praia',
                'Cubatão-Centro',
                'Cubatão-Vale do Mogi',
                'Cubatão-V.Parisi']
stations = stations.loc[(~stations.name.isin(not_stations)) & \
                        (stations.domain =='d02')]\
            .drop('domain', axis=1).sort_values(by='code')
stations.index =stations.code
print(stations)

path = '01_data/raw/mod/rain/'
paths = !ls {path+'*.pickle'}
rain = {}
files = ['sep2018','oct2018','rcp4.5sep2030','rcp8.5sep2030','rcp4.5oct2030','rcp8.5oct2030']
for p, f in zip(paths, files):
    rain[f] = pkl.load(open(p, "rb"))
    print(p,f)
    
#%% Import rainy data simulations 

rain_stations = list(rain['sep2018'].keys())
rain_2018 = pd.DataFrame()
for s in rain_stations:
    rain_df = pd.concat([rain['sep2018'][s],rain['oct2018'][s]]).set_index('local_date').drop('date', axis=1)
    rain_df['t_rain'] = rain_df.rainc+ rain_df.rainnc
    prev_total = [rain_df.rainc[i]+rain_df.rainnc[i] if i == 0 else 
                  rain_df.rainc[i-1]+rain_df.rainnc[i-1] for i in range(len(rain_df.index))]
    rain_df['prev_total'] = prev_total
    rain_df['rr'] = rain_df.t_rain - rain_df.prev_total
    rain_df.loc[rain_df.rr < 0] = 0
    rain_2018 = pd.concat([rain_2018,rain_df]).drop(['rainc','rainnc','t_rain','prev_total'], axis=1)
    rain_2018 = rain_2018[~rain_2018.name.isin(not_stations)]
    
rain_2018['type'] = [stations[stations.code == i].type.values[0] for i in rain_2018.code]

rain_rcp45 = pd.DataFrame()
for s in rain_stations:
    rain_df = pd.concat([rain['rcp4.5sep2030'][s],rain['rcp4.5oct2030'][s]]).set_index('local_date').drop('date', axis=1)
    rain_df['t_rain'] = rain_df.rainc+ rain_df.rainnc
    prev_total = [rain_df.rainc[i]+rain_df.rainnc[i] if i == 0 else 
                  rain_df.rainc[i-1]+rain_df.rainnc[i-1] for i in range(len(rain_df.index))]
    rain_df['prev_total'] = prev_total
    rain_df['rr'] = rain_df.t_rain - rain_df.prev_total
    rain_df.loc[rain_df.rr < 0] = 0
    rain_rcp45 = pd.concat([rain_rcp45,rain_df]).drop(['rainc','rainnc','t_rain','prev_total'], axis=1)
    rain_rcp45 = rain_rcp45[~rain_rcp45.name.isin(not_stations)]
    
rain_rcp45['type'] = [stations[stations.code == i].type.values[0] for i in rain_rcp45.code]

rain_rcp85 = pd.DataFrame()
for s in rain_stations:
    rain_df = pd.concat([rain['rcp8.5sep2030'][s],rain['rcp8.5oct2030'][s]]).set_index('local_date').drop('date', axis=1)
    rain_df['t_rain'] = rain_df.rainc+ rain_df.rainnc
    prev_total = [rain_df.rainc[i]+rain_df.rainnc[i] if i == 0 else 
                  rain_df.rainc[i-1]+rain_df.rainnc[i-1] for i in range(len(rain_df.index))]
    rain_df['prev_total'] = prev_total
    rain_df['rr'] = rain_df.t_rain - rain_df.prev_total
    rain_df.loc[rain_df.rr < 0] = 0
    rain_rcp85 = pd.concat([rain_rcp85,rain_df]).drop(['rainc','rainnc','t_rain','prev_total'], axis=1)
    rain_rcp85 = rain_rcp85[~rain_rcp85.name.isin(not_stations)]
    
rain_rcp85['type'] = [stations[stations.code == i].type.values[0] for i in rain_rcp85.code]
                                                
rain_2018.reset_index(inplace=True)
rain_rcp45.reset_index(inplace=True)
rain_rcp85.reset_index(inplace=True)

rain_2018['Mday']= rain_2018.local_date.dt.strftime('%b-%d %H:00')
rain_rcp45['Mday']= rain_rcp45.local_date.dt.strftime('%b-%d %H:00')
rain_rcp85['Mday']= rain_rcp85.local_date.dt.strftime('%b-%d %H:00')

#%% Join all scenarios of rainy simulations
by = ['Mday','name', 'code','name','type']
rain_mod = rain_rcp45.merge(rain_rcp85, on = by, 
           suffixes=('_rcp45','_rcp85')).merge(rain_2018,
                                               on = by)

rain_mod.set_index('local_date', inplace=True)

rain_mod['day'] = pd.to_datetime(rain_mod.index.strftime('%Y-%m-%d'), format='%Y-%m-%d')
#rain_mod['day'] = pd.to_datetime(rain_mod['day'], format='%Y-%m-%d')
rain_mod = rain_mod.groupby(['day','name','type']).sum().reset_index().set_index('day')
rain_mod.to_pickle('01_data/processed/mod/rain_mod.pkl')

