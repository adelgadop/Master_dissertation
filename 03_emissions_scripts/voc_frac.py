#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 18:09:14 2020

@author: mgavidia
"""


import xarray as xr
import pandas as pd

wrf00z = xr.open_dataset('./wrfchemi_00z_d01_veic_15km')
wrf12z = xr.open_dataset('./wrfchemi_12z_d01_veic_15km')

wrf = xr.concat([wrf00z, wrf12z], dim='Time')  


vocs = ['E_ETH', 'E_HC3', 'E_HC5', 'E_HC8', 'E_OL2',
        'E_OLT', 'E_OLI', 'E_ISO', 'E_TOL', 'E_XYL',
        'E_KET', 'E_CH3OH', 'E_C2H5OH', 'E_HCHO',
        'E_ALD']

voc_dic= {}

for voc in vocs:
    voc_dic[voc] = wrf[voc].sum().values
    
voc_df = pd.DataFrame.from_dict(voc_dic, orient='index', columns=['tot'])

VOC_TOT = voc_df.tot.sum()
voc_df['frac'] = voc_df.tot / VOC_TOT
voc_df['frac_round'] = voc_df.frac.round(2)
voc_df['per'] = voc_df.frac * 100

voc_df.to_csv('voc_frac.csv', sep=',', index_label='voc')
voc_df.to_csv('voc_frac_round.csv', sep=',', index_label='voc',
              columns=['frac_round'])
