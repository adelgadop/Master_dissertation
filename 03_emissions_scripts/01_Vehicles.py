#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 17:24:50 2021

@author: adelgado
"""

# Import necessary libraries

import pandas as pd
import numpy as np
import matplotlib as mp
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap as bm # not used for now
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geobr # information about municipalities shapefile
from shapely.geometry import box
import geopandas as gpd
from shapely.geometry import Polygon
import unicodedata

#%% Import the data --------------------------------------------------------------
df = pd.ExcelFile('01_data/DATA_EF.xlsx')
print(df.sheet_names)

vehCET = df.parse('VehCETESB2018')
Cat = pd.DataFrame([['PC_G','PC_E', 'PC_F','LCV_G','LCV_E','LCV_F','LCV_D',
                    'LT','SLT','MT','SHT','HT','SUB','UB','UBA','MC_G','MC_F']]).T

vehCET['Cat'] = Cat
print(vehCET.iloc[:,:-1].to_latex(caption='Vehicular fleet by type and fuel',
                                  label = 'tab:fleet', 
                                  longtable = True,
                                  index=False))

print(f"Veh/year for São Paulo state (CETESB): {vehCET['Veh/year'].sum()}")

#%% Emissions ratio (year 2018) for São Paulo in (t), according to CETESB (2019).

emCET = df.parse('EmCETESB2018',skiprows=1, index_col=None, na_values=['nd'])
print(emCET)

fleet_age = df.parse('fleet_age',skiprows=0, index_col=None, na_values=['nd'])
print(fleet_age.head())

#%% Use intensity has information about km/year by vehicle type
use = df.parse('Use intensity',skiprows=2, index_col=None, na_values=['nd'])
print(use.head())

#%% Denatran information, this data contents many details about numer of vehicles by month
# September
veh_sep18 = df.parse('DenatranSet2018', skiprows=0, index_col=None, na_values=['nd'])
veh_oct18 = df.parse('DenatranOct2018', skiprows=0, index_col=None, na_values=['nd'])
print(f"Sep. 2018: {veh_sep18}\n Oct. 2018: {veh_oct18}")

#%% Use intensity (kmd) by vehicle type -------------------------------------------
'''
We need to calculate this information:
    
&intensidade_uso                  ! ano 2018
 kmd_veic123      = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 1, 2 E 3
 kmd_veic4a       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 4A
 kmd_veic4b       = xxx.xx,       ! QUILOMETRAGEM DIARIA - VEICULOS 4B
 kmd_veic4c       = xxx.x,       ! QUILOMETRAGEM DIARIA - VEICULOS 4C
 kmd_veic5        = 0.,           ! QUILOMETRAGEM DIARIA - VEICULOS 5
 kmd_veic6a       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 6A
 kmd_veic6b       = xx.xx,         ! QUILOMETRAGEM DIARIA - VEICULOS 6B
/
'''

# Veic123
use_veic123 = ['PC gasoline','PC ethanol','PC flex-fuel','LCV gasoline',
               'LCV ethanol','LCV flex-fuel']
n_fleet123  = ['PC_G',  'PC_E',  'PC_FG', 'PC_FE', 
               'LCV_G', 'LCV_E', 'LCV_FG','LCV_FE']

def use_int(use_list= use_veic123,fleet_list= n_fleet123):
    use_veic = use[['Year']]
    use_veic['kmd'] = use[use_list].mean(axis=1)/365
    use_veic['n_veic'] = fleet_age[fleet_list].sum(axis=1)
    kmd_veic = (use_veic['kmd']*use_veic['n_veic']).sum()/use_veic['n_veic'].sum()
    return kmd_veic

# Veic 4a
use_veic4a = ['LCV Diesel','SLT - Diesel','LT - Diesel', 'MT - Diesel','SHT - Diesel', 'HT - Diesel']
n_fleet4a  = ['LCV_D', 'SLT', 'LT', 'MT', 'SHT', 'HT']

# Veic 4b
use_veic4b = ['UB - Diesel', 'SUB - Diesel']
n_fleet4b  = ['UB', 'SUB']

# Veic 4c
use_veic4c = ['UBA - Diesel']
n_fleet4c  = ['UBA']

# Veic 6a
use_veic6a = ['MC']
n_fleet6a  = ['MC_150_G', 'MC_150_500_G', 'MC_500_G']

# Veic 6b
use_veic6b = ['MC']
n_fleet6b  = ['MC_150_FG', 'MC_150_500_FG','MC_500_FG', 'MC_150_FE', 'MC_150_500_FE', 'MC_500_FE']

print("kmd_veic123 = ",use_int(use_list= use_veic123,fleet_list= n_fleet123).round(2))
print("kmd_veic4a = ",use_int(use_list= use_veic4a,fleet_list= n_fleet4a).round(2))
print("kmd_veic4b = ",use_int(use_list= use_veic4b,fleet_list= n_fleet4b).round(2))
print("kmd_veic4c = ",use_int(use_list= use_veic4c,fleet_list= n_fleet4c).round(2))
print("kmd_veic6a = ",use_int(use_list= use_veic6a,fleet_list= n_fleet6a).round(2))
print("kmd_veic6b = ",use_int(use_list= use_veic6b,fleet_list= n_fleet6b).round(2))


#%% Fleet characteristics ---------------------------------------------------------
'''
Based on `vehCET`, fleet fractions by type:
'''
fraction = vehCET.groupby('ID').sum()/vehCET['Veh/year'].sum()
print(fraction)

'''
&caracteristicas_frota           
 n_veic           = 9,           ! NUMERO DE TIPOS DE VEICULO
 frota_veicular   = xxxxxxxx,    ! FROTA TOTAL EXISTENTE PARA O PERIODO ANALISADO
 veic_gasolina    = 0.208972,    ! FRACAO VEICULOS MOVIDOS A GASOLINA (VEIC 1)
 veic_etanol      = 0.014630,    ! FRACAO VEICULOS MOVIDOS A ETANOL (VEIC 2)
 veic_flex        = 0.547739,    ! FRACAO VEICULOS MOVIDOS A FLEX (VEIC 3)
 veic_caminhoes   = 0.056697,    ! FRACAO CAMINHOES (DIESEL - VEIC 4A)
 veic_urbanos     = 0.005071,    ! FRACAO ONIBUS URBANO (DIESEL - VEIC 4B)
 veic_rodoviarios = 0.001850,    ! FRACAO ONIBUS RODOVIARIO (DIESEL - VEIC 4C)
 veic_taxis       = 0.000000,    ! FRACAO TAXIS (GAS - VEIC 5)
 veic_moto_gaso   = 0.119445,    ! FRACAO MOTOS MOVIDOS A GASOLINA (VEIC 6A)
 veic_moto_flex   = 0.045596,    ! FRACAO MOTOS FLEX (VEIC 6B)
 frota_ativa      = 1,           ! FRACAO FROTA ATIVA (1=100%)
/
'''

#%% Vehicle fleet by modeling domain area -----------------------------------------

# Functions
def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    return str(text)
    
def total_veh_domain(lon1, lat1, lon2, lat2, year, UF, veh_sep18):
    '''
    Parameters
    ----------
    lon1 : float number
        longitude 1 of the south-west.
    lat1 : float number
        latitude 1 of the south-west
    lon2 : float number
        longitude 2 of the north-east.
    lat2 : float number
        latitude 2 of the north-east.
    year : integer
        year analized.
    UF : string list
        Unidades Federais de Brasil
    veh : Pandas DataFrame
        Number of vehicle types by UF and municipality.

    Returns
    -------
    Number of vehicles inside the modeling domain area 

    '''
    mun = geobr.read_municipality(code_muni='all', year=2018)
    polygon = Polygon([(lon1, lat1), (lon1, lat2), (lon2, lat2), (lon2, lat1), (lon1, lat1)])

    munDomain = gpd.clip(mun, polygon) ## This is very important
    munDomain = munDomain.sort_values(by='abbrev_state')
    munnames = list(munDomain.name_muni.values)
    munNAMES = [x.upper() for x in munnames]
    munNAMES = [strip_accents(x) for x in munNAMES]
    munDomain['MUNICIPIO'] = munNAMES


    UF = ['MG', 'ES', 'RJ', 'SP', 'PR', 'SC', 'RS', 'MS', 'GO']
    vehUF = veh_sep18[veh_sep18.UF.isin(UF)]
    vehs = ['AUTOMOVEL', 'CAMINHAO'    , 'CAMINHAO TRATOR', 'CAMINHONETE', 'CAMIONETA', 
            'CICLOMOTOR', 'MICRO-ONIBUS', 'MOTOCICLETA'    , 'MOTONETA'   , 'ONIBUS'   ,
            'TRATOR ESTEI', 'TRATOR RODAS', 'UTILITARIO']

    vehUF = vehUF.filter(['UF','MUNICIPIO']+vehs)
    vehUF['TOTAL'] = vehUF.sum(axis = 1)

    vehMunDom1 = vehUF[vehUF.MUNICIPIO.isin(munNAMES)]
    return vehMunDom1, vehUF

# --------

UF = ['MG', 'ES', 'RJ', 'SP', 'PR', 'SC', 'RS', 'MS', 'GO']

#%% September and October 2018
# September
# ---------
# Domain 01
vehMun_d01, VehUF_d01_sep18 = total_veh_domain(-53.53, -27.70, -39.69, -19.30, 2018, UF, veh_sep18)
veic_sep18_d01 = vehMun_d01['TOTAL'].sum().round(0)

# Domain 02
vehMun_d02, VehUF_d02_sep18 = total_veh_domain(-49.01, -25.05, -44.36, -21.64, 2018, UF, veh_sep18)
veic_sep18_d02 = vehMun_d02['TOTAL'].sum().round(0)

# October
# ---------
# Domain 01
vehMun_d01, VehUF_d01_oct18 = total_veh_domain(-53.53, -27.70, -39.69, -19.30, 2018, UF, veh_oct18)
veic_oct18_d01 = vehMun_d01['TOTAL'].sum().round(0)

# Domain 02
vehMun_d02, VehUF_d02_oct18 = total_veh_domain(-49.01, -25.05, -44.36, -21.64, 2018, UF, veh_oct18)
veic_oct18_d02 = vehMun_d02['TOTAL'].sum().round(0)

total_vehicles = pd.DataFrame(
    {'Sep 2018':{'d01': veic_sep18_d01, 'd02': veic_sep18_d02},
     'Oct 2018':{'d01': veic_oct18_d01, 'd02': veic_oct18_d02} }
    )

print(total_vehicles)
total_vehicles.to_csv("04_output/emissions/Total_veh_domain.csv")

#%% Figures ------------------------------------------------------------------------

lon1 = -53.53; lat1 = -27.70; lon2 = -39.69; lat2 = -19.30  # Domain 01

plt.figure(figsize=(16, 12))
ax1 = plt.subplot(1, 2, 1, projection=ccrs.PlateCarree())

ax1.set_extent([lon1-1, lon2+1, lat1-1, lat2+1], crs=ccrs.PlateCarree())

# Put a background image on for nice sea rendering.
ax1.stock_img()

# Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none')

ax1.add_feature(cfeature.LAND)
ax1.add_feature(cfeature.COASTLINE)
ax1.add_feature(states_provinces, edgecolor='black')
mun = geobr.read_municipality(code_muni='all', year=2018)
mun.plot(facecolor="none",alpha=1, edgecolor='gray', ax=ax1)
polygon = Polygon([(lon1, lat1), (lon1, lat2), (lon2, lat2), (lon2, lat1), (lon1, lat1)])
poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=mun.crs)
poly_gdf.boundary.plot(ax=ax1, color="red")

munDomain = gpd.clip(mun, polygon) ## This is very important
munDomain = munDomain.sort_values(by='abbrev_state')

ax2 = plt.subplot(1, 2, 2, projection=ccrs.PlateCarree())
munDomain.plot(ax=ax2, color="purple", alpha = 0.5)
munDomain.boundary.plot(ax=ax2)
poly_gdf.boundary.plot(ax=ax2, color="red")
ax2.set_title("Clipped", fontsize=20)
plt.savefig('04_output/emissions/clip.png', bbox_inches='tight', facecolor='w' )

#%% Temporal distribution from Andrade et al. (2015)
co = [0.019, 0.012, 0.008, 0.004, 0.003, 0.003, 0.006, 0.017, 0.047, 0.074, 0.072, 0.064,
      0.055, 0.052, 0.051, 0.048, 0.052, 0.057, 0.068, 0.087, 0.085, 0.057, 0.035, 0.024]
no = [0.019, 0.015, 0.012, 0.010, 0.008, 0.009, 0.015, 0.030, 0.048, 0.053, 0.051, 0.061,
      0.064, 0.064, 0.061, 0.060, 0.060, 0.065, 0.065, 0.066, 0.056, 0.044, 0.035, 0.027]

hours = list(range(21,24)) +list(range(21))
hours = [str(h) for h in hours]
fig, ax = plt.subplots()
temp_dist = pd.DataFrame({'LDV':co, 'HDV':no, 'Local Time':hours}).set_index('Local Time')
temp_dist.plot(figsize=(4,2.5), ax=ax, style=['-d','-sr'])
ax.set_ylabel('Fraction of emission per hour')
ax.set_xlabel('Local Time (hours)')
ax.xaxis.set_major_locator(mp.ticker.FixedLocator(range(24))) 
plt.savefig('dissertation/fig/Temp_distr.pdf', bbox_inches='tight', facecolor='w')

# %% Emissions calculation for the modeling domain using Top-Down aproach -----------
V_SP   = pd.DataFrame({'Sep 2018':VehUF_d01_sep18.loc[VehUF_d01_sep18.UF == 'SP', 'TOTAL'].sum(),
                       'Oct 2018':VehUF_d01_oct18.loc[VehUF_d01_oct18.UF == 'SP', 'TOTAL'].sum()},
                      index=['SP'])

pol = ['CO','NOx','SO2','MP','COV']
E_SP = emCET[pol].sum()/1000


emi = pd.DataFrame({'São Paulo State':E_SP,
                    'D01 Sep 2018':(E_SP*total_vehicles.loc['d01','Sep 2018']/V_SP.loc['SP','Sep 2018']).round(3),
                    'D01 Oct 2018':(E_SP*total_vehicles.loc['d01','Oct 2018']/V_SP.loc['SP','Oct 2018']).round(3),
                    'D02 Sep 2018':(E_SP*total_vehicles.loc['d02','Sep 2018']/V_SP.loc['SP','Sep 2018']).round(3),
                    'D02 Oct 2018':(E_SP*total_vehicles.loc['d02','Oct 2018']/V_SP.loc['SP','Oct 2018']).round(3)}
                          )

print(emi)

#%% VOC fraction Figure
voc_frac = pd.read_csv("01_data/voc_frac.csv")
voc_frac.set_index('voc', inplace=True)

fig, ax = plt.subplots(figsize=(6,2))
voc_frac.plot(kind='bar',y='per', ax=ax, edgecolor='k',
              ylabel='Percentage [%]', rot=90, legend=False)
ax.set_xlabel('VOC species')
fig.savefig("dissertation/fig/voc_frac.pdf", bbox_inches='tight', facecolor='w')


