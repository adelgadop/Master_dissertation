#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 15:38:29 2021

@author: adelgado
"""

from functools import reduce
import pandas as pd
import os, fnmatch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib as mpl
import pickle as pkl
import scipy
import statsmodels.api as sm
import functions.mod_stats as ms

#%% Functions

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
    
    
def subplots(df,pol,ylabel,xlabel,suffixes,legend, size, n_yticks, n_xticks,filename,alpha,lw,markersize,labelsize, by):
    """
    Return lineplot subplots by station only completed data to be compared.
    
    Parameters
    ----------
    df       : pandas DataFrame with datetime as index
               time series with colnames as station and meteorological and air quality parameters
    pol      : str
               air quality parameter, for instance, pol = 'o3'
    ylabel   : str
    xlabel   : str
    suffixes : list of two strings, for instance suffixes = ['_obs','_mod']
    legend   : list of two strings
    size     : tuple, default size = (6,8)
    n_yticks : int
               Number of yaxis labels
    n_xticks : int
               Interval number of xaxis labels               
    path     : str
               path location where the figure will be located
    name     : str
               suffix name of figure
    alpha    : float between 0 and 1. Default 0.7
    lw       : int
    markersize : int
    labelsize : int
    by       : str
               subplots by specific name based column names
    
    Returns
    -------
    Figure exported as pdf plot in a specific path
    
    """
    df_1 = df[['station','type',pol+suffixes[0],pol+suffixes[1]]].dropna()
    locs = list(df_1.sort_values(by=by,ascending=True)[by].unique())
    
    fig, ax = plt.subplots(df_1[by].nunique(),
                           figsize=size, 
                           sharex=True, sharey=True,
                           gridspec_kw={'hspace':0.4})
    for i in range(df_1[by].nunique()):
        df_1.loc[df_1[by] == locs[i]][pol+suffixes[0]].\
        plot(ax=ax[i],color='k', marker='.', markersize=markersize, #alpha=alpha,
             markeredgecolor='none', linestyle='none', label=legend[0])
        
        df_1.loc[df_1[by] == locs[i]][pol+suffixes[1]].\
        plot(ax=ax[i],color='g', alpha=alpha,
             #marker='.', markersize=markersize,
             #markeredgecolor='none', #linestyle='none',
             linestyle='-', 
             lw=lw, label=legend[1])
        ax[2].set_ylabel(ylabel)
        ax[0].xaxis.set_major_formatter(md.DateFormatter('%a-%d'))
        ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,31,n_xticks)))
        ax[0].xaxis.set_minor_locator(md.MonthLocator())
        ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n\n\n%b-%y'))
        ax[i].yaxis.set_major_locator(plt.MaxNLocator(n_yticks))
        ax[i].tick_params(axis='both', which='minor', labelsize=labelsize)
        ax[i].tick_params(axis='both', labelsize=labelsize)
        ax[i].set_xlabel(xlabel)
        ax[i].set_title(locs[i],size=8, loc='left')
        if i == len(df_1[by].unique())-1:
            ax[i].legend(fontsize=7)
    fig.savefig(filename+'_subplot_'+pol+'.pdf',bbox_inches='tight', facecolor='w')
    
def subplots2(df,pol,ylabel,xlabel,suffixes,legend, size, n_yticks, n_xticks,filename,alpha,lw,markersize,labelsize, by):
    """
    Return lineplot subplots by station only completed data to be compared.
    
    Parameters
    ----------
    df       : pandas DataFrame with datetime as index
               time series with colnames as station and meteorological and air quality parameters
    pol      : str
               air quality parameter, for instance, pol = 'o3'
    ylabel   : str
    xlabel   : str
    suffixes : list of two strings, for instance suffixes = ['_obs','_mod']
    legend   : list of two strings
    size     : tuple, default size = (6,8)
    n_yticks : int
               Number of yaxis labels
    n_xticks : int
               Interval number of xaxis labels               
    path     : str
               path location where the figure will be located
    name     : str
               suffix name of figure
    alpha    : float between 0 and 1. Default 0.7
    lw       : int
    markersize : int
    labelsize : int
    by       : str
               subplots by specific name based column names
    
    Returns
    -------
    Figure exported as pdf plot in a specific path
    
    """
    df_1 = df[['station','type',pol+suffixes[0],pol+suffixes[1]]].dropna()
    locs = list(df_1.sort_values(by=by,ascending=True)[by].unique())
    
    fig, ax = plt.subplots(df_1[by].nunique(),
                           figsize=size, 
                           sharex=True, sharey=True,
                           gridspec_kw={'hspace':0.4})
    for i in range(df_1[by].nunique()):
        plot_pol1 = df_1.loc[df_1[by] == locs[i]][pol+suffixes[0]].\
        plot(ax=ax[i],color='k', marker='.', markersize=markersize, #alpha=alpha,
             markeredgecolor='none', linestyle='none', label=legend[0])
        
        plot_pol2 = df_1.loc[df_1[by] == locs[i]][pol+suffixes[1]].\
        plot(ax=ax[i],color='g', alpha=alpha,
             #marker='.', markersize=markersize,
             #markeredgecolor='none', linestyle='none',
             linestyle='-', 
             lw=lw, label=legend[1])
        ax[2].set_ylabel(ylabel)
        ax[0].xaxis.set_major_formatter(md.DateFormatter('%a-%d'))
        ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,31,n_xticks)))
        ax[0].xaxis.set_minor_locator(md.MonthLocator())
        ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n\n\n%b-%y'))
        ax[i].yaxis.set_major_locator(plt.MaxNLocator(n_yticks))
        ax[i].tick_params(axis='both', which='minor', labelsize=labelsize)
        ax[i].tick_params(axis='both', labelsize=labelsize)
        ax[i].set_xlabel(xlabel)
        ax[i].set_title(locs[i],size=8, loc='left')
        ax[i].axvspan('2018-09-14', '2018-09-16 01:00', 
           label="Not analyzed",facecolor="0", alpha=0.2)
        if i == len(df_1[by].unique())-1:
            ax[i].legend(fontsize=5,ncol=3)
    fig.savefig(filename+'_subplot_'+pol+'.pdf',bbox_inches='tight', facecolor='w')
    #start_remove = pd.to_datetime('2018-09-14').tz_localize('America/Sao_Paulo')
    #end_remove = pd.to_datetime('2018-09-16').tz_localize('America/Sao_Paulo')
    
    
def o3stats_by(by, data, stats, stations):
    
    sites = list(data[[by,'o3_obs','o3_mod']]
                 .dropna()
                 .sort_values(by=by,ascending=True)[by]
                 .unique())
    
    o3_stats = {}
    o3sta_df = pd.DataFrame()
    
    for i in sites:
        o3_stats[i] = (ms.aq_stats(data[data[by].isin([i])],polls=['o3']))
        o3_stats[i][by] = (i)
        df = o3_stats[i]
        o3sta_df = pd.concat([o3sta_df,df]).round(2)
    o3sta_df = o3sta_df.sort_values(by='r', ascending=False).loc['o3']
    
    if by == 'type':
        o3sta_df = o3sta_df.set_index(by).T.rename(columns={'Industry':'Ind',
                                                            'Forest preservation':'F. pre.',
                                                            'Regional urban':'R. urb.',
                                                            'Urban park': 'U. park',
                                                            'Urban':'Urb'})
        o3sta_df = o3sta_df[['F. pre.','Urb','U. park','Ind','R. urb.']]
        o3_sel = o3sta_df.loc[stats, :]
    
    else:
        o3sta_df['abb'] = [stations[stations.name == i].abb.values[0] for i in o3sta_df.station]
        o3sta_df['type'] = [stations[stations.name == i].type.values[0] for i in o3sta_df.station]
        o3_sel = o3sta_df
        
    return o3_sel

def plot_type(met,alpha,para, ylabel,filename, station_types, n_yticks, path='./'):
    fig, ax = plt.subplots(len(station_types), figsize=(8,8),sharex=True,gridspec_kw={'hspace':.25})
    for i,t in enumerate(station_types):
        mean = met[met.type == t].resample('D').mean()
        mean.plot(y=[para,para+'_rcp45',para+'_rcp85'],style=['g','c','#D22523'],
                  lw=3, alpha=.7,ax=ax[i], legend=False)
        std = met[met.type == t].resample('D').std()
        ax[i].fill_between(mean.index, mean[para]+std[para], mean[para]-std[para], color='g', alpha=alpha)
        ax[i].fill_between(mean.index, mean[para+'_rcp45']+std[para+'_rcp45'], 
                           mean[para+'_rcp45']-std[para+'_rcp45'], color='c', alpha=alpha)
        ax[i].fill_between(mean.index, mean[para+'_rcp85']+std[para+'_rcp85'], 
                           mean[para+'_rcp85']-std[para+'_rcp85'], color='#D22523', alpha=alpha)
        ax[i].set_title(t,size=8, loc='left')
        ax[0].xaxis.set_major_formatter(md.DateFormatter('%d'))
        ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,31,4)))
        ax[0].xaxis.set_minor_locator(md.MonthLocator())
        ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n%b'))
        ax[i].yaxis.set_major_locator(plt.MaxNLocator(n_yticks))
        ax[2].set_ylabel(ylabel)
        ax[len(station_types)-1].legend(['2018', "RCP 4.5 (2030)","RCP 8.5 (2030)"], fontsize=5,
                                       ncol = 3)
        ax[i].set_xlabel('Local Time')
    fig.savefig(path+filename+'.pdf', bbox_inches='tight', facecolor='w')
    
def subplots_rcp(df,pol,ylabel,xlabel,suffixes,legend, legend_size, hspace,
                 size, n_yticks, n_xticks,filename,alpha,lw,markersize,labelsize, by):
    """
    Return lineplot subplots by station only completed data to be compared.
    
    Parameters
    ----------
    df       : pandas DataFrame with datetime as index
               time series with colnames as station and meteorological and air quality parameters
    pol      : str
               air quality parameter, for instance, pol = 'o3'
    ylabel   : str
    xlabel   : str
    suffixes : list of two strings, for instance suffixes = ['_rcp45','_rcp85']
    legend   : list of three strings
    leg_size : int
    hspace   : float
    size     : tuple, default size = (6,8)
    n_yticks : int
               Number of yaxis labels
    n_xticks : int
               Interval number of xaxis labels               
    path     : str
               path location where the figure will be located
    name     : str
               suffix name of figure
    alpha    : float between 0 and 1. Default 0.7
    lw       : int
    markersize : int
    labelsize : int
    by       : str
               subplots by specific name based column names
    
    Returns
    -------
    Figure exported as pdf plot in a specific path
    
    """
    df_1 = df[[by,pol,pol+suffixes[0],pol+suffixes[1]]].dropna()
    locs = list(df_1.sort_values(by=by,ascending=True)[by].unique()) 
    
    fig, ax = plt.subplots(df_1[by].nunique(),
                           figsize=size, 
                           sharex=True, sharey=True,
                           gridspec_kw={'hspace':hspace})
    for i in range(df_1[by].nunique()):
        df_1.loc[df_1[by] == locs[i]][pol].\
        plot(ax=ax[i],color='g', marker='.',linestyle='none',
             markersize=markersize, label=legend[0])
        df_1.loc[df_1[by] == locs[i]][pol+suffixes[0]].\
        plot(ax=ax[i],color='c', linestyle='-',lw=lw, alpha=alpha, label=legend[1]) #86B2D6
        df_1.loc[df_1[by] == locs[i]][pol+suffixes[1]].\
        plot(ax=ax[i],color='#D22523', linestyle='-',lw=lw, alpha=alpha, label=legend[2])
        ax[0].xaxis.set_major_formatter(md.DateFormatter('%d'))
        ax[0].xaxis.set_major_locator(md.DayLocator(np.arange(0,60,n_xticks)))
        ax[0].xaxis.set_minor_locator(md.MonthLocator())
        ax[0].xaxis.set_minor_formatter(md.DateFormatter('\n\n%b'))
        ax[i].yaxis.set_major_locator(plt.MaxNLocator(n_yticks))
        ax[i].tick_params(axis='both', which='minor', labelsize=labelsize)
        ax[i].tick_params(axis='both', labelsize=labelsize)
        ax[2].set_ylabel(ylabel)
        ax[i].set_xlabel(xlabel)
        ax[i].set_title(locs[i],size=8, loc='left')
        if i == len(df_1[by].unique())-1:
            ax[i].legend(fontsize=legend_size, ncol = 3)
    fig.savefig(filename+'_subplot_'+pol+'.pdf',bbox_inches='tight', facecolor='w')
