#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 21:57:30 2020

@author: mgavidia
"""


import xarray as xr
import pandas as pd


htap_total = xr.open_dataset('./EDGAR_HTAP_emi_CO_2010.0.1x0.1.nc')


def htap_by_source_to_anthro_emiss(htap_src_file, htap_total):
    '''
    Add variables and dimensions required to run anthro_emiss
    with edgar_HTAP_<POL>_emi_<SOURCE>_2010_<MONTH>.0.1x0.1.nc

    Parameters
    ----------
    htap_file : str
        edgar_htap filename or complete path.
    month : int
        Month number.
    date : int
        start date in yyyymmdd.

    Returns
    -------
    create a netcdf ready to feed anthro_emiss.

    '''
    htap_src = xr.open_dataset(htap_src_file)
    var_name = list(htap_src.data_vars)[0]
    htap_src = htap_src.rename({var_name:'emis_tot'})
    htap_src['time'] = htap_total.time.values
    htap_src['date'] = xr.DataArray(htap_total.date.values,
                                       dims=['time'])
    htap_src['datesec'] = xr.DataArray(htap_total.datesec.values,
                                          dims=['time'])
    htap_src.to_netcdf(htap_src_file.replace('year.nc', 'AE.nc'))


def file_name_emiss(path, pol, source, ident=''):
    '''
    Create emission file name 

    Parameters
    ----------
    path : str
        folder where edgar_htap emissions are.
    esp : str
        pollutant name.
    source : str
        type or source.
    year : int
        year.
    month : int
        month.

    Returns
    -------
    file_name : str
        full path of emission.

    '''
    file_name = (path + 'edgar_HTAP_' + pol +
                 '_emi_' + source.upper() + 
                 '_2010.0.1x0.1' + ident + 
                 '.nc')
    return file_name

# Path where _year file is
# in /scr2/mgavidia/wrf_utils/EDGAR-HTAP/htap_data/source
PATH = '/scr2/alejandro/WRF/DATA/util/EDGAR-HTAP/industry/' #'/scr2/mgavidia/wrf_utils/EDGAR-HTAP/htap_data/sources'
#PATH = '/scr2/mgavidia/wrf_utils/EDGAR-HTAP/htap_data/transport/ordered/'
SOURCE = 'INDUSTRY'
#SOURCE = 'TRANSPORT'
POL =['CO', 'SO2', 'NOx', 'NMVOC', 'NH3']


htap_files = []
for pol in POL:
    htap_files.append(file_name_emiss(PATH, pol, SOURCE, '_year'))
    
for file in htap_files:
    htap_by_source_to_anthro_emiss(file, htap_total)
    
    
# Splitting vocs

voc_frac = pd.read_csv('./voc_frac_round.csv')
    
nmvoc = xr.open_dataset(file_name_emiss(PATH, 'NMVOC', SOURCE, '_AE'))


voc_dic = {}

for emi, frac in zip(voc_frac.voc, voc_frac.frac_round):
    voc_dic[emi[2:]] = nmvoc.emis_tot * frac



def voc_dataarray_to_dataset(da, nmvoc):
    ds = xr.Dataset()
    ds['emis_tot'] = da
    
    for key, value in nmvoc.attrs.items():
        ds.attrs[key] = value
    for k, v in nmvoc.emis_tot.attrs.items():
        ds.emis_tot.attrs[k] = v
    
    ds['date'] = xr.DataArray(nmvoc.date.values,
                                       dims=['time'])
    ds['datesec'] = xr.DataArray(nmvoc.datesec.values,
                                          dims=['time'])
    return ds



voc_dic_ds ={}
for voc in list(voc_dic):
    voc_dic_ds[voc] = voc_dataarray_to_dataset(voc_dic[voc], nmvoc)
    

for voc in list(voc_dic_ds):
    voc_dic_ds[voc].to_netcdf(file_name_emiss(PATH, voc, SOURCE, '_AE'))
