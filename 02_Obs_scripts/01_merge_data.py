#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:03:18 2021

@author: adelgado
"""

import pandas as pd
import os
import numpy as np
import glob
import pickle as pkl
import fnmatch

#%% Data processing

stations = pd.read_csv('01_data/stations.csv')
#                      encoding = "ISO-8859-1")

# Meteorological parameters
f14 = [file for file in sorted(glob.glob('01_data/Y2014/*met*'))]
f15 = [file for file in sorted(glob.glob('01_data/Y2015/*met*'))]
f16 = [file for file in sorted(glob.glob('01_data/Y2016/*met*'))]
f17 = [file for file in sorted(glob.glob('01_data/Y2017/*met*'))]
f18 = [file for file in sorted(glob.glob('01_data/Y2018/*met*'))]

# Function
def readDat(files):
    Data = pd.DataFrame()

    for file in files:
        df = pd.read_csv(file)
        Data = pd.concat([Data,df])
    return Data
# End

met14 = readDat(f14)
met15 = readDat(f15)
met16 = readDat(f16)
met17 = readDat(f17)
met18 = readDat(f18)

metData = pd.concat([met14,met15,met16,met17,met18])
metData['station'] = [stations[stations.code == i].name.values[0] for i in metData.code]

# Air quality parameters
f14 = [file for file in sorted(glob.glob('01_data/Y2014/*photo*'))]
f15 = [file for file in sorted(glob.glob('01_data/Y2015/*photo*'))]
f16 = [file for file in sorted(glob.glob('01_data/Y2016/*photo*'))]
f17 = [file for file in sorted(glob.glob('01_data/Y2017/*photo*'))]
f18 = [file for file in sorted(glob.glob('01_data/Y2018/*photo*'))]

aq14 = readDat(f14)
aq15 = readDat(f15)
aq16 = readDat(f16)
aq17 = readDat(f17)
aq18 = readDat(f18)

aqData = pd.concat([aq14,aq15,aq16,aq17,aq18])
aqData['station'] = [stations[stations.code == i].name.values[0] for i in aqData.code]
data = pd.merge(metData, aqData)
data.loc[:,'local_date'] = pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
data.to_pickle('05_output/obs/air_data.pkl')

#%% Data processed from csv downloaded from QUALAR by station codes
def read_Dat(files, path, time_zone, stations, from_wrf = True):
    """
    Read time series csv files for each station code from a specific path
    
    Parameters
    ----------
    files : str list
        name of csv files
    path  : str
        path location
    time_zone : str
        for instance 'America/Sao_Paulo'
    
    Returns
    -------
    Pandas DataFrame
    """
    Data = pd.DataFrame()
    
    if from_wrf:
        for file in files:
            df = pd.read_csv(path + file)
            Data = pd.concat([Data,df])
        Data = Data[Data.code.isin(stations.code)]
        Data['station'] = [stations[stations.code == i].name.values[0] for i in Data.code]
        Data['type'] = [stations[stations.code == i].type.values[0] for i in Data.code]
        Data.loc[:,'date'] = pd.to_datetime(Data['date'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize("UTC")
        Data.loc[:,'local_date']=Data['date'].dt.tz_convert(time_zone)
        return Data
    
    else: # observations
        for file in files:
            df = pd.read_csv(path + file)
            Data = pd.concat([Data,df])
        Data = Data[Data.code.isin(stations.code)]
        Data['station'] = [stations[stations.code == i].name.values[0] for i in Data.code]
        Data['type'] = [stations[stations.code == i].type.values[0] for i in Data.code]
        Data.loc[:,'date'] = pd.to_datetime(Data['date'], format='%Y-%m-%d %H:%M:%S')
        Data.rename(columns={'date':'local_date'}, inplace = True)
        Data.loc[:,'local_date']=Data['local_date'].dt.tz_localize(time_zone)
        return Data
    
Dir_1 = '01_data/SEP18/'
Dir_2 = '01_data/OCT18/'
fs18 = fnmatch.filter(os.listdir(Dir_1), 'all_met*.csv')
fo18 = fnmatch.filter(os.listdir(Dir_2), 'all_met*.csv')
met_s18 = read_Dat(fs18, Dir_1, 'America/Sao_Paulo', stations, False)
met_o18 = read_Dat(fo18, Dir_2, 'America/Sao_Paulo', stations, False)

# Air quality parameters observations
fs18 = fnmatch.filter(os.listdir(Dir_1), 'all_photo*.csv')
fo18 = fnmatch.filter(os.listdir(Dir_2), 'all_photo*.csv')
aq_s18 = read_Dat(fs18, Dir_1, 'America/Sao_Paulo', stations, False)
aq_o18 = read_Dat(fo18, Dir_2, 'America/Sao_Paulo', stations, False)
sep18 = pd.merge(met_s18, aq_s18)
sep18['nox']=sep18.no+sep18.no2
oct18 = pd.merge(met_o18, aq_o18)
oct18['nox']=oct18.no+oct18.no2
obs18 = pd.concat([sep18,oct18])

# to pickle
obs18.to_pickle("05_output/obs/obs18.pkl")

#%% Toluene and Benzene for some pollutants

stations = pd.read_csv('01_data/stations_hc.csv')
#stations = stations.loc[stations.domain =='d02']\
#            .drop('domain', axis=1).sort_values(by='code')
stations.index =stations.code
print(stations)

st = {c:n for c,n in zip(list(stations.code), list(stations.name))}
st_type = {c:n for c,n in zip(list(stations.code), list(stations.type))}

photo = [file for file in sorted(glob.glob('01_data/obs/*photo_*'))]
met = [file for file in sorted(glob.glob('01_data/obs/*met_*'))]

aq_data = pd.DataFrame()

for s in list(photo):
    df = pd.read_pickle(s)
    df['station'] = st[int(df.code.unique()[0])]
    df['type'] = st_type[int(df.code.unique()[0])]
    aq_data = pd.concat([aq_data,df])

aq_data.to_pickle('05_output/obs/data_all_photo.pkl')

met_data = pd.DataFrame()

for s in list(met):
    df = pd.read_pickle(s)
    df['station'] = st[int(df.code.unique()[0])]
    df['type'] = st_type[int(df.code.unique()[0])]
    met_data = pd.concat([met_data,df])

met_data.to_pickle('05_output/obs/data_all_met.pkl')


