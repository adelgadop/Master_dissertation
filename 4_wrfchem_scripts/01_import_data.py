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

#%% Read the model data and merge with observations in one ----------------------
Mod = {}
Dir = {'sep18': '01_data/processed/model/Y2018/sep18/',
       'oct18': '01_data/processed/model/Y2018/oct18/'}

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

# Merge obs and mod data in one
data = obs.merge(mod, 
                on=['local_date','station','code','type'],
                suffixes=('_obs', '_mod'), how = 'left')

#%% Export the all data --------------------------------------------------------------
data = data.loc[data.type.isin(mod.type.unique()), :]
data = data.loc[~(data.station.isin(not_stations)), :]
data.to_pickle('01_data/processed/all_data.pkl')

