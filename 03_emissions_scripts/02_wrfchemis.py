#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 11:47:15 2021

@author: adelgado
"""

# import necessary libraries

import numpy as np
import xarray as xr
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm
import seaborn as sns

#%% Import NetCDF files -------------------------------------------------------
# Anthropogenic emissions for September 2018

# First domain
i_d01 = ['wrfchemi_00z_d01_ind' , 'wrfchemi_12z_d01_ind' ]
v_d01 = ['wrfchemi_00z_d01_veic', 'wrfchemi_12z_d01_veic']
r_d01 = ['wrfchemi_00z_d01_res' , 'wrfchemi_12z_d01_res' ]
t_d01 = ['wrfchemi_00z_d01_total.nc','wrfchemi_12z_d01_total.nc']

# Second domain
i_d02 = ['wrfchemi_00z_d02_ind' , 'wrfchemi_12z_d02_ind' ]
v_d02 = ['wrfchemi_00z_d02_veic', 'wrfchemi_12z_d02_veic']
r_d02 = ['wrfchemi_00z_d02_res' , 'wrfchemi_12z_d02_res' ]
t_d02 = ['wrfchemi_00z_d02_total.nc','wrfchemi_12z_d02_total.nc']

bio   = ['wrfbiochemi_d01','wrfbiochemi_d02']

def readnc(path = '../data/wrfchemis/exp10/', file= i_d01[0]):
    fnc = path+file
    print('Reading ', fnc)
    ncfile = xr.open_dataset(fnc)
    return ncfile

# D01
ind_00z_d01 = readnc(file=i_d01[0])
ind_12z_d01 = readnc(file=i_d01[1])
vei_00z_d01 = readnc(file=v_d01[0])
vei_12z_d01 = readnc(file=v_d01[1])
res_00z_d01 = readnc(file=r_d01[0])
res_12z_d01 = readnc(file=r_d01[1])
tot_00z_d01 = readnc(file=t_d01[0])
tot_12z_d01 = readnc(file=t_d01[1])

# D02
ind_00z_d02 = readnc(file=i_d02[0])
ind_12z_d02 = readnc(file=i_d02[1])
vei_00z_d02 = readnc(file=v_d02[0])
vei_12z_d02 = readnc(file=v_d02[1])
res_00z_d02 = readnc(file=r_d02[0])
res_12z_d02 = readnc(file=r_d02[1])
tot_00z_d02 = readnc(file=t_d02[0])
tot_12z_d02 = readnc(file=t_d02[1])

bio_d01     = readnc(file=bio[0])
bio_d02     = readnc(file=bio[1])

print(ind_00z_d01.dims)
print(res_00z_d01.dims)

print(ind_12z_d02.dims)
print(res_12z_d02.dims)

# %% Biogenic emissions output from MEGAN2 ------------------------------------
var    = ['MSEBIO_ISOP','PFTP_BT','PFTP_NT','PFTP_SB',
          'PFTP_HB','MLAI','MTSA','MSWDOWN']
label  = ['mol km$^{-2}$ hr$^{-1}$','[%]','[%]','[%]','[%]',
          '','[k]','[W m$^{-2}$]']
titles = ['Amount of isoprene','Broad leaf','Needle leaf',
          'Shrubs','Herbaceous biota','Monthly LAI',
         'Monthly air temp.','Monthly download short wave rad.']

fig = plt.figure(figsize=(2*4,4*2.5))
fig.subplots_adjust(hspace=0.25, wspace=0.25)
for i in range(1,9):
    if i < 6:
        ax = fig.add_subplot(4,2,i)
        bio = bio_d01[var[i-1]].isel(Time=0)
        plt.imshow(bio, cmap='viridis')
        plt.colorbar(label=label[i-1]).ax.tick_params(labelsize=9)
        plt.gca().invert_yaxis()
        plt.title(titles[i-1], fontsize=8)
    elif i == 6:
        ax = fig.add_subplot(4,2,i)
        bio_d01[var[i-1]].isel(Time=0)[8].plot(ax=ax,cmap='viridis',
                                               cbar_kwargs={'label': label[i-1]})
        ax.set_title(titles[i-1], fontsize=8)
        ax.set_ylabel('')
        ax.set_xlabel('')
    else:
        ax = fig.add_subplot(4,2,i)
        bio_d01[var[i-1]].isel(Time=0)[8].plot(ax=ax,cmap='RdBu_r',
                                               cbar_kwargs={'label': label[i-1]})
        ax.set_title(titles[i-1], fontsize=8)
        ax.set_ylabel('')
        ax.set_xlabel('')
#plt.colorbar(label=label[i-1]).ax.tick_params(labelsize=9)
fig.savefig('dissertation/fig/biogenic_d01.pdf',bbox_inches='tight')

# %% Anthrropogenic emissions Exp 10 with fc_nox = 0.8 only for road transport ----




ind_d01 = xr.concat([ind_00z_d01, ind_12z_d01], dim="Time")
ind_d02 = xr.concat([ind_00z_d02, ind_12z_d02], dim="Time")
res_d01 = xr.concat([res_00z_d01, res_12z_d01], dim="Time")
res_d02 = xr.concat([res_00z_d02, res_12z_d02], dim="Time")
vei_d01 = xr.concat([vei_00z_d01, vei_12z_d01], dim="Time")
vei_d02 = xr.concat([vei_00z_d02, vei_12z_d02], dim="Time")
tot_d01 = xr.concat([tot_00z_d01, tot_12z_d01], dim="Time")
tot_d02 = xr.concat([tot_00z_d02, tot_12z_d02], dim="Time")

anthro     = {'ind_d01':ind_d01,  'res_d01':res_d01,
              'road_d01':vei_d01, 'total_d01':tot_d01,
              'ind_d02':ind_d02,  'res_d02':res_d02,
              'road_d02':vei_d02, 'total_d02':tot_d02}

keys       = ['ind','res','road','total']
dom        = '_d02'     
hour       = 18 # 15 horas local time in Brazil
max_e      = 150 # mol km^-2 hr^-1
max_res    = 10  # mol km^-2 hr^-1
pol_label  = 'NO'
pol        = 'E_'+pol_label
Cmap       = 'YlGnBu_r'#'YlGnBu_r','jet','summer','RdYlBu_r','bwr','cividis','plasma','inferno','hot','Spectral_r' viridis
titles     = ['Industry (ind), 2010','Residential (res), 2010',
              'Road Trans. (road), Sep. 2018', 'ind+res+road = Total']

# Figure
fig = plt.figure(figsize=(10,6))
fig.subplots_adjust(hspace=0.35, wspace=0.25)
for i in range(1,5):
    if i == 2:
        ax = fig.add_subplot(2,2,i)
        anthro[keys[i-1]+dom][pol].isel(Time=hour).plot(ax=ax,
                                                        #vmax=max_res,
                                                        cmap=Cmap,
                                                        alpha=1,
                                                        cbar_kwargs={'label': pol_label+' [mol km$^{-2}$ h$^{-1}$]'})
        ax.set_title(titles[i-1]+' (LT: '+str(hour-3)+' h)', fontsize=10,loc='center', fontweight='bold')
        ax.set_ylabel('south-north', fontsize = 8)
        ax.set_xlabel('west-east', fontsize = 8)
    else:
        ax = fig.add_subplot(2,2,i)
        anthro[keys[i-1]+dom][pol].isel(Time=hour).plot(ax=ax,
                                                        #vmax=max_e,
                                                        cmap=Cmap,
                                                        alpha=1,
                                                        cbar_kwargs={'label': pol_label+' [mol km$^{-2}$ h$^{-1}$]'})
        ax.set_title(titles[i-1]+' (LT: '+str(hour-3)+' h)', fontsize=10, loc='center', fontweight='bold')
        ax.set_ylabel('south-north', fontsize = 8)
        ax.set_xlabel('west-east', fontsize = 8)

fig.savefig('dissertation/fig/'+pol+'_emi'+dom+'.pdf', bbox_inches='tight', facecolor='w')

#%% Emissions in kt -----------------------------------------------------------

# Functions

def mol_kton(emi_file = anthro, sector = 'road',
             domain='d01',km2 = 15*15, pol = 'NO'):
    """
    Return wrfchemi emissions per hour to kt per year.
    
    Parameters:
    -----------
    emi_file = dict with xarray dataset corresponding to wrfchemis
    sector   = emission inventory sector
               str
    domain   = str
    km2      = cel area in km2
               integer
    pol      = pollutant
               str
    Returns:
    --------
    emission in kt/year
    """
    
    mol_w = {'CO':28,'NO':30,'NO2':46,'SO2':64,'NH3':17,'ISO':68.12,'ETH':30.07,
             'HC3':42.66,'HC5':60,'HC8':96,'XYL':104,'OL2':28.05,'OLT':56,'OLI':56,
             'TOL':92,'HCHO':30.09,'ALD':44.05,'KET':58.08,'CH3OH':70.09,'C2H5OH':46}
    res = (emi_file[sector+'_'+domain]['E_'+pol]*km2).sum().values*365*mol_w[pol]/10**9
    
    return res

def kton_all(emi_file = anthro, keys = ['ind','res','road','total'],domain='d01', km2=15*15):
    """
    Return DataFrame for all pollutants consider in wrfchemi for CBMZ.
    Parameters:
    -----------
    emi_file = dict with xarray dataset corresponding to wrfchemis
    keys     = sectors of emission inventory
               list of str
    domain   = modelling domain, i.e., 'd01'
               str
    km2      = cel area or spatial resolution in km^2
               number
    
    Returns:
    --------
    emi    = Emissions file as pandas DataFrame in units of kt per year.
    """
    
    emi  = {}
    polls = ['CO','NO', 'NO2','SO2','NH3','ISO','ETH','HC3','HC5','HC8',
             'XYL','OL2','OLT','OLI','TOL','HCHO','ALD','KET','CH3OH','C2H5OH']
    for p in polls:
        emi[p] = {i:mol_kton(emi_file = emi_file, sector = i,domain=domain,km2 = km2, pol = p)\
                  .round(2) for i in keys}
    emi = pd.DataFrame.from_dict(emi)
    emi['NOx']=emi.NO+emi.NO2
    emi = emi.T
    return emi

# End functions

emi = {'d01': kton_all(keys = ['road','ind','res'], domain='d01', km2= 15*15),
       'd02': kton_all(keys = ['road','ind','res'], domain='d02', km2= 3*3)}

emi = pd.concat([emi['d01'], emi['d02']], 
                axis=1,keys=['d01', 'd02']).T.iloc[:,[0,1,2,-1]+list(range(3,20))].T
print(emi)

#%% Only for the d02 modeling domain
emi_d02 = emi['d02'].reset_index().rename(columns={'index': 'ID'})
pol = ['Carbon monoxide', 'Nitrogen oxide', 'Nitrogen dioxide', 
       'Nitrogen oxides', 'Sulfur dioxide', 'Ammonia', 'Isoprene', 
       'Ethane', 'Propane', 'Alkanes (k$_{OH}$ 0.5 - 1)', 
       'Alkanes (k$_{OH}$ 1 - 2)', 'Xylenes', 'Alkenes (internal)',
       'Alkenes (terminal)', 'Alkenes (primary)', 'Toluene', 
       'Formaldehyde', 'Aldehydes', 'Ketones', 'Methanol', 'Ethanol']

emi_d02.loc[emi_d02.ID == 'NO2', 'ID'] = 'NO$_2$'
emi_d02.loc[emi_d02.ID == 'NOx', 'ID'] = 'NO$_x$'
emi_d02.loc[emi_d02.ID == 'SO2', 'ID'] = 'SO$_2$'
emi_d02.loc[emi_d02.ID == 'NH3', 'ID'] = 'NH$_3$'
emi_d02.loc[emi_d02.ID == 'CH3OH', 'ID'] = 'CH$_3$OH'
emi_d02.loc[emi_d02.ID == 'C2H5OH', 'ID'] = 'C$_2$H$_5$OH'

emi_d02.loc[:, 'Name'] = pol
emi_d02 = emi_d02[['Name', 'ID', 'road', 'ind', 'res']].set_index('Name')
print(emi_d02)

print(emi_d02
      .rename(columns={'road':'Road',
                              'ind': 'Industrial',
                              'res': 'Residential'})
      .to_latex(label='tab: emi_d02',
                caption = 'Emission rates (kt/year) for the second modeling domain'))

#%% Figure of emission rates for both domain ----------------------------------
Cmap = 'Accent' #Paired, Paired_r, Pastel1, Pastel1_r, Pastel2, Pastel2_r
fig, ax = plt.subplots(2, figsize=(10,6),sharex=True, sharey=False,
                       gridspec_kw={'hspace':0.2,'wspace':0},
                       subplot_kw={'yscale':'log',
                                   'ylabel':'kt year$^{-1}$',
                                   'xlabel':'Species'})
kwarg = {'edgecolor':'k','width':0.85}
emi['d01'].iloc[0:,:].plot(kind='bar',stacked=False,ax=ax[0], legend=False, title='Domain 1',**kwarg)
emi['d02'].iloc[0:,:].plot(kind='bar',stacked=False,ax=ax[1], legend=True,  title='Domain 2',**kwarg)

ax[1].legend(['Road (LAPAt 2018)','Industry (EDGAR 2010)','Residential (EDGAR 2010)'], fontsize=9, ncol = 3)
ax[0].text(-2, 10000, '(a)', fontsize=20)

fig.savefig('dissertation/fig/emi_kt.pdf', bbox_inches='tight', facecolor='w');

#%% Figure of temporal variation by anthropogenic sector ----------------------

fig, ax = plt.subplots(2, sharex=True, gridspec_kw={'hspace':0.2,'wspace':0})
kwarg={'linewidth':3,'marker':'.'}
pol = 'NO'
mol_w = 28
(vei_d01['E_'+pol].sum(axis=1).sum(axis=1).sum(axis=1)*15*15*mol_w/10**6).plot(ax=ax[0],label='Road',**kwarg)
(ind_d01['E_'+pol].sum(axis=1).sum(axis=1).sum(axis=1)*15*15*mol_w/10**6).plot(ax=ax[0],label='Ind.',**kwarg)
(res_d01['E_'+pol].sum(axis=1).sum(axis=1).sum(axis=1)*15*15*mol_w/10**6).plot(ax=ax[0],label='Res.',**kwarg)
(vei_d02['E_'+pol].sum(axis=1).sum(axis=1).sum(axis=1)*3*3*mol_w/10**6).plot(ax=ax[1],**kwarg)
(ind_d02['E_'+pol].sum(axis=1).sum(axis=1).sum(axis=1)*3*3*mol_w/10**6).plot(ax=ax[1],**kwarg)
(res_d02['E_'+pol].sum(axis=1).sum(axis=1).sum(axis=1)*3*3*mol_w/10**6).plot(ax=ax[1],**kwarg)

ax[0].set_ylabel(pol+' [kt h$^{-1}$]')
ax[1].set_ylabel(pol+' [kt h$^{-1}$]')
ax[0].set_xlabel('')
ax[0].legend(fontsize=8)
ax[0].set_title('Domain 1',loc='left', fontsize=8)
ax[1].set_title('Domain 2',loc='left', fontsize=8)
ax[0].text(-4, 100, '(b)', fontsize=13)
fig.savefig('dissertation/fig/emi_'+pol+'_time_kt.pdf',bbox_inches='tight', facecolor='w')


















