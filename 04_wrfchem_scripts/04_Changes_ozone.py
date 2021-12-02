#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 22:07:28 2021

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
# from mpl_toolkits.basemap import Basemap # not installed
from uncertainties import ufloat

#%% Import data from simulations by scenarios ------------------------------------

mod_all = pd.read_pickle('01_data/processed/mod/mod_all_scen.pkl')

# Eliminamos duplicados
mod_all = mod_all[~mod_all.duplicated()]

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


#%% Rolling 8 hour mean ---------------------------------------------------------

mod_all['month'] = mod_all.local_date.dt.month
months = {'Sep': mod_all.loc[mod_all.month == 9,:],
          'Oct': mod_all.loc[mod_all.month == 10,:]}

MDA8 = {}


for mes, df in months.items():
    o3 = df[['local_date','station','type', 'o3','o3_rcp45','o3_rcp85']].set_index('local_date')
    roll_o3 = {}
    rollo3 = pd.DataFrame()
    for i in o3.station.unique():
        roll_o3[i] = (o3[o3.station == i].rolling(window=8).mean()[['o3','o3_rcp45','o3_rcp85']])
        roll_o3[i]['station'] = i
        roll_o3[i]['type'] = (o3[o3.station == i].type)
        df1 = roll_o3[i]
        rollo3 = pd.concat([rollo3,df1])
        rollo3['day'] = rollo3.index.day
        MDA8[mes] = rollo3.groupby(['day','station','type']).max().reset_index().dropna()
    
        types = list(MDA8[mes].sort_values(by='type',ascending=True).type.unique())


#%% Histogram 
plt.style.use("default")
fig, ax = plt.subplots(2, 1, figsize = (5,8), sharex = True, gridspec_kw={'hspace':0.10})

for i, (mes, df) in enumerate(months.items()):
    o3 = df[['local_date','station','type', 'o3','o3_rcp45','o3_rcp85']].set_index('local_date')
    o3.plot(kind = "hist", density = True, color = ['g','c','#D22523'], edgecolor = 'k', lw = 1,
            alpha = 0.65, bins = 15, ax = ax[i]) # change density to true, because KDE uses density
    # Plot KDE
    o3.plot(kind = "kde", ax = ax[i], color = ['g','c','#D22523'], lw = 3)

    # X
    ax[i].set_xlabel("Hourly O$_3$ ($\mu$g m$^{-3}$)")
    # Limit x range to 0-4
    x_start, x_end = 0, 250
    ax[i].set_xlim(x_start, x_end)

    # Y
    ax[i].set_ylim(0, 0.015)
    #ax[i].set_yticklabels([])
    ax[i].set_ylabel("")

    # Legend
    ax[i].legend(['Base case ('+mes+'. 2018)','RCP4.5 ('+mes+'. 2030)',
                          'RCP8.5 ('+mes+'. 2030)'],fontsize=10, ncol = 1)

    # Overall
    ax[i].grid(False)

    # Remove ticks and spines
    ax[i].tick_params(left = False, bottom = False)
    for ax[i], spine in ax[i].spines.items():
         spine.set_visible(False)

fig.savefig('../article/fig/hist_o3_sim.pdf', bbox_inches = 'tight', facecolor = 'w')

#%% Figures of MDA8 by station type only rcps-------------------------------------

for mes, df in MDA8.items():
    fig, ax = plt.subplots(len(types),
                           figsize=(6,8),
                           sharey=True,
                           sharex=True,
                           gridspec_kw={'hspace':0.25})
    for i in range(len(types)):
        df.loc[df.type ==types[i]].groupby(['type','day'])\
            .mean().reset_index().set_index('day')\
                .plot(ax=ax[i], y = ['o3_rcp45', 'o3_rcp85'],legend=False, grid=True, fontsize=8,
                      color=['c','#D22523'], lw=2.5, marker='.', alpha=.7)
        ax[i].set_title(types[i],size=8, loc='left')
        ax[2].set_ylabel('O$_3$ [$\mu$g.m$^{-3}$]')
        if i == len(types)-1:
            ax[i].legend(['RCP4.5 ('+mes+'. 2030)','RCP8.5 ('+mes+'. 2030)'],
                         fontsize=7, ncol = 3)
    fig.savefig('05_output/wrfchem/fig/MDA8_type_'+mes+'_only_rcps.pdf', bbox_inches = 'tight', facecolor = 'w')
   
#%% Figures of MDA8 for all scenarios

for mes, df in MDA8.items():
    fig, ax = plt.subplots(len(types),
                           figsize=(6,8),
                           sharey=True,
                           sharex=True,
                           gridspec_kw={'hspace':0.25})

    for i in range(len(types)):
        df.loc[df.type ==types[i]].groupby(['type','day'])\
            .mean().reset_index().set_index('day')\
            .plot(ax=ax[i], legend=False, grid=True, fontsize=8,
                  color=['g','c','#D22523'], lw=2.5, marker='.', alpha=.7)
        ax[i].set_title(types[i],size=8, loc='left')
        ax[2].set_ylabel('O$_3$ [$\mu$g.m$^{-3}$]')
        if i == len(types)-1:
            ax[i].legend([mes+'. 2018','RCP4.5 ('+mes+'. 2030)',
                          'RCP8.5 ('+mes+'. 2030)'],fontsize=7, ncol = 3)

    fig.savefig('dissertation/fig/MDA8_'+mes+'_type_rcps.pdf',bbox_inches='tight', facecolor='w')
    fig.savefig('05_output/wrfchem/fig/MDA8_'+mes+'_type_rcps.pdf',bbox_inches='tight', facecolor='w')

#%% Figure of ozone as time series ----------------------------------------------

mev.subplots_rcp(mod_all.set_index('local_date'), #[data.station.isin(gr_1)]
         pol='o3',
         ylabel='O$_3$ [$\mu$gm$^{-3}$]',
         xlabel='Local Time',
         suffixes=['_rcp45','_rcp85'],
         legend=['Sep-Oct 2018','RCP4.5 (Sep-Oct 2030)','RCP8.5 (Sep-Oct 2030)'],
         legend_size=7,
         size=(10,10),
         hspace=0.3,
         n_yticks=5,
         n_xticks=2,
         filename='dissertation/fig/rcp_2030',
         alpha=.5,
         markersize=1,
         lw=2,
         labelsize=8, 
         by='type')

#%% Spatial variation -------------------------------------------------------------
o3_mda8_mean = {}

for m, df in MDA8.items():
    o3_mda8_mean[m] = df.groupby('station').mean().reset_index().drop('day',axis=1)
    o3_mda8_mean[m]['lat'] = [stations[stations.name == i].lat.values[0] for i in o3_mda8_mean[m].station]
    o3_mda8_mean[m]['lon'] = [stations[stations.name == i].lon.values[0] for i in o3_mda8_mean[m].station]

#%% Map of differences 
for mes, o3_mean in o3_mda8_mean.items():
    diff = {'RCP 4.5 ('+mes+'. 2030) - '+mes+'. 2018':o3_mean.o3_rcp45.values - o3_mean.o3.values,
            'RCP 8.5 ('+mes+'. 2030) - '+mes+'. 2018':o3_mean.o3_rcp85.values - o3_mean.o3.values}

    min_v = -20
    max_v = 20
    fig, ax = plt.subplots(2,2, figsize=(10,10),gridspec_kw={'hspace':0.0,'wspace':0})
    res = 'h'
    for i, d in enumerate(diff):
        m = Basemap(projection='merc',llcrnrlon=-50,llcrnrlat=-24.5,
                    urcrnrlon=-44,urcrnrlat=-21.5, resolution=res, ax=ax[0,i])
        m.drawcoastlines(color='0.2',linewidth=0.2)
        m.drawstates(color='k',linewidth=0.5)
        m.drawmapboundary(fill_color='aqua')
        if i ==0:
            m.drawparallels(np.arange(-60, 0, 0.5),linewidth=0.05,labels=[1,0,0,0])
        m.drawparallels(np.arange(-60, 0, 0.5),linewidth=0.05,labels=[0,0,0,0], fontsize=8, alpha=0.8)
        m.drawmeridians(np.arange(-60, 0, 0.85),linewidth=0.05, labels=[0,0,0,1], fontsize=8, alpha=0.8)
        m.fillcontinents(color='0.45',lake_color='0.5')
        m.readshapefile("01_data/MunRM07",'sp', drawbounds=True, color='0.3',
                default_encoding='ISO-8859-1',linewidth=0.3)

        cb = m.scatter(o3_mean.lon.values, o3_mean.lat.values, marker='o',vmin=min_v,vmax=max_v,
                       latlon=True,c=diff[d], cmap='RdBu_r', alpha=1, s = 10,zorder=100)
        ax[0,i].set_title(d)
    
        m = Basemap(projection='merc',llcrnrlon=-47.5,llcrnrlat=-24.25,
                    urcrnrlon=-45.5,urcrnrlat=-23, resolution=res, ax=ax[1,i])
        m.drawcoastlines(color='0.2',linewidth=0.2)
        m.drawstates(color='k',linewidth=0.5)
        m.drawmapboundary(fill_color='aqua')
        if i ==0:
            m.drawparallels(np.arange(-60, 0, 0.25),linewidth=0.05,labels=[1,0,0,0])
        m.drawparallels(np.arange(-50, 0, 0.25),linewidth=0.05,labels=[0,0,0,0], fontsize=8, alpha=0.8)
        m.drawmeridians(np.arange(-50, 0, 0.35),linewidth=0.05, labels=[0,0,0,1], fontsize=8, alpha=0.8)
        m.fillcontinents(color='0.45',lake_color='0.5')
        m.readshapefile("01_data/MunRM07",'sp', drawbounds=True, 
                        default_encoding='ISO-8859-1',linewidth=0.3)

        cb = m.scatter(o3_mean.lon.values, o3_mean.lat.values, marker='o',vmin=min_v,vmax=max_v,
                       latlon=True,c=diff[d], cmap='RdBu_r', alpha=1, s = 20,zorder=100)    
    
    fig.colorbar(cb, label='MDA8 ozone mean difference [$\mu$gm$^{-3}$]', 
                 orientation='horizontal', ax=ax, pad=0.03)
    
    fig.savefig('dissertation/fig/mda8_spatial_station_'+mes+'.pdf',
                bbox_inches='tight', facecolor='w')
    
#%% Changes by station types ------------------------------------------------------

# September
o3_mean_type = MDA8['Sep'].groupby('type').mean().reset_index().drop('day',axis=1).round(2).set_index("type")
o3_std_type = MDA8['Sep'].groupby('type').std().reset_index().drop('day',axis=1).round(2).set_index("type")


o3_mean_type.rename(columns={"o3": "Sep. 2018", 
                             "o3_rcp45": "Sep. 2030 (RCP 4.5)", 
                             "o3_rcp85": "Sep. 2020 (RCP 8.5)"}, inplace = True)

o3_std_type.rename(columns={"o3": "Sep. 2018", 
                             "o3_rcp45": "Sep. 2030 (RCP 4.5)", 
                             "o3_rcp85": "Sep. 2020 (RCP 8.5)"}, inplace = True)


print(o3_mean_type.to_latex(label="o3_sep_type", caption = "MDA8 ozone monthly average for September"),
      file=open('05_output/wrfchem/tab/o3_changes_type_Sep.tex','w'))

print(o3_std_type.to_latex(label="o3_sep_type", caption = "MDA8 ozone monthly std for September"),
      file=open('05_output/wrfchem/tab/o3_std_type_Sep.tex','w'))

# October
o3_mean_type = MDA8['Oct'].groupby('type').mean().reset_index().drop('day',axis=1).round(2).set_index("type")
o3_std_type = MDA8['Oct'].groupby('type').std().reset_index().drop('day',axis=1).round(2).set_index("type")

o3_mean_type.rename(columns={"o3": "Oct. 2018", 
                             "o3_rcp45": "Oct. 2030 (RCP 4.5)", 
                             "o3_rcp85": "Oct. 2020 (RCP 8.5)"}, inplace = True)
o3_std_type.rename(columns={"o3": "Sep. 2018", 
                             "o3_rcp45": "Sep. 2030 (RCP 4.5)", 
                             "o3_rcp85": "Sep. 2020 (RCP 8.5)"}, inplace = True)

print(o3_mean_type.to_latex(label="o3_oct_type", caption = "MDA8 ozone monthly average for October"),
      file=open('05_output/wrfchem/tab/o3_changes_type_Oct.tex','w'))
print(o3_std_type.to_latex(label="o3_oct_type", caption = "MDA8 ozone monthly std for October"),
      file=open('05_output/wrfchem/tab/o3_std_type_Oct.tex','w'))

#%% Sum of uncertainties


Sep = {'Industry'           : {'2018': ufloat(100.45, 23.41), 'rcp45': ufloat(94.35, 15.70), 'rcp85': ufloat( 98.55, 21.54)},
       'Regional urban'     : {'2018': ufloat( 97.04, 20.75), 'rcp45': ufloat(90.66, 18.66), 'rcp85': ufloat( 99.93, 19.40)},
       'Forest preservation': {'2018': ufloat( 92.67, 25.57), 'rcp45': ufloat(84.77, 32.05), 'rcp85': ufloat(106.13, 29.23)},
       'Urban'              : {'2018': ufloat( 90.47, 24.21), 'rcp45': ufloat(81.82, 30.29), 'rcp85': ufloat(105.48, 28.81)},
       'Urban park'         : {'2018': ufloat( 90.24, 23.01), 'rcp45': ufloat(81.99, 30.20), 'rcp85': ufloat(105.37, 29.01)},
       }

Oct = {'Industry'           : {'2018': ufloat( 95.04, 15.60), 'rcp45': ufloat(104.81, 24.17), 'rcp85': ufloat( 98.64, 22.70)},
       'Regional urban'     : {'2018': ufloat( 91.42, 16.34), 'rcp45': ufloat( 98.15, 24.26), 'rcp85': ufloat( 91.00, 23.63)},
       'Forest preservation': {'2018': ufloat( 79.69, 25.87), 'rcp45': ufloat( 89.70, 33.26), 'rcp85': ufloat( 84.20, 30.23)},
       'Urban'              : {'2018': ufloat( 80.04, 27.80), 'rcp45': ufloat( 87.73, 34.27), 'rcp85': ufloat( 80.26, 28.06)},
       'Urban park'         : {'2018': ufloat( 80.38, 28.35), 'rcp45': ufloat( 87.36, 34.95), 'rcp85': ufloat( 80.98, 28.86)},
       }

umda8 = pd.concat([pd.DataFrame(Sep), pd.DataFrame(Oct)], keys = (['Sep', 'Oct'])).T

print('Sep RCP4.5: ')
for k in Sep.keys():
    print('{:10.2f}'.format(Sep[k]['rcp45'] - Sep[k]['2018']))

print('Sep RCP8.5: ')
for k in Sep.keys():
    print('{:10.2f}'.format(Sep[k]['rcp85'] - Sep[k]['2018']))

print('Oct RCP4.5: ')
for k in Oct.keys():
    print('{:10.2f}'.format(Oct[k]['rcp45'] - Oct[k]['2018']))

print('Oct RCP8.5: ')
for k in Oct.keys():
    print('{:10.2f}'.format(Oct[k]['rcp85'] - Oct[k]['2018']))


