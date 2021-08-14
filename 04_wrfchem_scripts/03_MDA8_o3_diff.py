#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 10:51:46 2021

@author: adelgado
"""

# Import necessary libraries
import pandas as pd
import os, fnmatch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib as mpl
import pickle as pkl
import xarray as xr
import h5py
from netCDF4 import Dataset
import glob
import wrf
import pytz
from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from mpl_toolkits.axes_grid1 import AxesGrid
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

#%% MDA8 diferences for September and October --------------------------------
path = '../data/wrfout/'
wrfout = [Dataset(i) for i in sorted(glob.glob(path+'*'))]

t2 = wrf.getvar(wrfout, 'T2', timeidx=wrf.ALL_TIMES, method='cat')
rh2 = wrf.getvar(wrfout, 'rh2', timeidx=wrf.ALL_TIMES, method='cat')
wind = wrf.getvar(wrfout, 'uvmet10_wspd_wdir', timeidx=wrf.ALL_TIMES, method='cat')
ws = wind.sel(wspd_wdir='wspd')
wd = wind.sel(wspd_wdir='wdir')
psfc = wrf.getvar(wrfout, 'PSFC', timeidx=wrf.ALL_TIMES, method='cat')

o3 = wrf.getvar(wrfout, 'o3', timeidx=wrf.ALL_TIMES, method='cat')
o3_sfc  = o3.isel(bottom_top=0)
R = 8.3144598 # J/K mol
o3_u = o3_sfc * psfc * (16 * 3) / (R * t2)
o3_u[0,:,:].plot()

lon = t2.XLONG[0,:].values
lat = t2.XLAT[:,0].values
print(lon, lat)

#%% Construction of xarray dataset from h5py file

data = {'sep':{'curr' : h5py.File(path + 'curr_201809.h5', 'r').get('o3_u')[3:,:,:],
               'rcp45': h5py.File(path + 'rcp45_203009.h5', 'r').get('o3_u')[3:,:,:],
               'rcp85': h5py.File(path + 'rcp85_203009.h5', 'r').get('o3_u')[3:,:,:]
              },
        'oct':{'curr' : h5py.File(path + 'curr_201810.h5', 'r').get('o3_u')[3:,:,:],
               'rcp45': h5py.File(path + 'rcp45_203010.h5', 'r').get('o3_u')[3:,:,:],
               'rcp85': h5py.File(path + 'rcp85_203010.h5', 'r').get('o3_u')[3:,:,:]}
       }

print(data['sep']['curr'].shape)
print(data['oct']['curr'].shape)
print(lon.shape, lat.shape)

# Local times as UTC because there are issues if I consider tz as America/Sao_Paulo
local_sep = pd.date_range("2018-09-01 00:00", periods = 717, freq = 'H') # , tz = 'America/Sao_Paulo'
local_oct = pd.date_range("2018-10-01 00:00", periods = 741, freq = 'H') # , tz = 'America/Sao_Paulo'
times = {'sep': local_sep, 'oct': local_oct}
print(times)

#%% Make a Dataset for both months --------------------------------------------
dset = {'sep':xr.Dataset(), 'oct':xr.Dataset()}
for k in dset.keys():
    dset[k]['curr'] = (('time', 'lat', 'lon'), data[k]['curr'])
    dset[k]['rcp45'] = (('time', 'lat', 'lon'), data[k]['rcp45'])
    dset[k]['rcp85'] = (('time', 'lat', 'lon'), data[k]['rcp85'])
    dset[k].coords['lat'] = (('lat'), lat)
    dset[k].coords['lon'] = (('lon'), lon)
    dset[k].coords['time'] = times[k]
    dset[k].attrs['title'] = k
    print(dset[k])

dset['sep']['curr'][0,:,:].plot()

#%% Make a MDA8 Dataset -------------------------------------------------------
mda8 = {'sep': xr.Dataset(), 'oct': xr.Dataset()}
for k in mda8.keys():
    mda8[k]['curr']  = dset[k]['curr'].rolling(time = 8).mean().dropna("time")
    mda8[k]['rcp45'] = dset[k]['rcp45'].rolling(time = 8).mean().dropna("time")
    mda8[k]['rcp85'] = dset[k]['rcp85'].rolling(time = 8).mean().dropna("time")
    
diff = {'sep': xr.Dataset(), 'oct': xr.Dataset()}
for k in diff.keys():
    for scen in ['rcp45', 'rcp85']:
        diff[k][scen] = (mda8[k][scen].groupby('time.dayofyear').max() - mda8[k]['curr'].groupby('time.dayofyear').max()).mean('dayofyear')
    
fig, ax = plt.subplots(2,2, figsize = (16,10))
diff['sep']['rcp45'].plot.contourf(cmap = 'RdBu_r', levels = 15, center = False, ax = ax[0,0])
diff['sep']['rcp85'].plot.contourf(cmap = 'RdBu_r', levels = 15, center = False, ax = ax[0,1])
diff['oct']['rcp45'].plot.contourf(cmap = 'RdBu_r', levels = 15, center = False, ax = ax[1,0])
diff['oct']['rcp85'].plot.contourf(cmap = 'RdBu_r', levels = 15, center = False, ax = ax[1,1])

#%% Make a map of MDA8 
sept = xr.concat([diff['sep'].rcp45, diff['sep'].rcp85], 
                 pd.Index(['RCP 4.5 (2030) - 2018', 'RCP 8.5 (2030) - 2018'], name = 'scen'))             
octo = xr.concat([diff['oct'].rcp45, diff['oct'].rcp85], 
                 pd.Index(['RCP 4.5 (2030) - 2018', 'RCP 8.5 (2030) - 2018'], name = 'scen'))
diff_all = xr.concat([sept, octo], pd.Index(['Sep', 'Oct'], name = 'month'))
projection = ccrs.PlateCarree()
fname = "01_data/MunRM07.shp"

#ax = plt.subplot(projection=ccrs.PlateCarree())
p = diff_all.plot.contourf(x="lon", y="lat", col="scen", figsize = (10, 5.9),
                           row="month", levels = 20,
                           subplot_kws=dict(projection= projection, facecolor="gray"),
                           transform=ccrs.PlateCarree(),
                           cbar_kwargs = {'label': 'MDA8 ozone mean difference [$\mu$g m$^{-3}$]'}
                      )
for ax in p.axes.flat:
    ax.coastlines()
    ax.set_xticks(np.arange(-49, -44, 1), crs=projection)
    ax.set_yticks(np.arange(-25, -21, 1), crs=projection)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    shape_feature = ShapelyFeature(Reader(fname).geometries(),
                                  ccrs.PlateCarree(), facecolor = 'none', linewidth = 0.5)
    ax.add_feature(shape_feature)

plt.savefig('05_output/wrfchem/fig/map_mda8_diff.pdf', bbox_inches='tight', facecolor='w')
plt.savefig('dissertation/fig/map_mda8_diff.pdf', bbox_inches='tight', facecolor='w')
