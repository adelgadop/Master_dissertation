# Emissions
We need to feed data about vehicles for two domain areas into the `namelist_fc.emi` to run `wrfchemi_cbmz_fc.ncl`.

CETESB published a report called "Emissões Veiculares no Estado de São Paulo 2018" (CETESB 2019). This report contents information about `use intensity`, `emission factors by type of vehicle`, `number of vehicles`. Also, on the web page of [DENATRAN](https://www.gov.br/infraestrutura/pt-br/assuntos/transito/conteudo-denatran/frota-de-veiculos-2018) there is a specific information about the number of vehicles for each UF (states of Brazil) that it was downloaded for all months in 2018. So, based on the modeling domain, the number of vehicles is summed to used after in the `wrfchemi_cbmz_fc.ncl` through the `namelist_fc.emi`:

```
&caracteristicas_frota            
 n_veic           = 9,            ! NUMERO DE TIPOS DE VEICULO
 frota_veicular   = xxxxxxxxx,    ! FROTA TOTAL EXISTENTE PARA O PERIODO ANALISADO
 veic_gasolina    = x.xxxxxxx,    ! FRACAO VEICULOS MOVIDOS A GASOLINA (VEIC 1)
 veic_etanol      = x.xxxxxxx,    ! FRACAO VEICULOS MOVIDOS A ETANOL (VEIC 2)
 veic_flex        = x.xxxxxxx,    ! FRACAO VEICULOS MOVIDOS A FLEX (VEIC 3)
 veic_caminhoes   = x.xxxxxxx,    ! FRACAO CAMINHOES (DIESEL - VEIC 4A)
 veic_urbanos     = x.xxxxxxx,    ! FRACAO ONIBUS URBANO (DIESEL - VEIC 4B)
 veic_rodoviarios = x.xxxxxxx,    ! FRACAO ONIBUS RODOVIARIO (DIESEL - VEIC 4C)
 veic_taxis       = x.xxxxxxx,    ! FRACAO TAXIS (GAS - VEIC 5)
 veic_moto_gaso   = x.xxxxxxx,    ! FRACAO MOTOS MOVIDOS A GASOLINA (VEIC 6A)
 veic_moto_flex   = x.xxxxxxx,    ! FRACAO MOTOS FLEX (VEIC 6B)
 frota_ativa      = 1,            ! FRACAO FROTA ATIVA (1=100%)
/

! Fatores de emissao baseados em Perez-Martinez et al. (2014) e Andrade et al. (2015)
&fator_emissao    ! VEIC 1,  VEIC 2,  VEIC 3,  VEIC4A,  VEIC4B,  VEIC4C,  VEIC 5,  VEIC6A,  VEIC6B
 exa_co           = 5.8000,  12.000,  5.8000,  3.6000,  3.6000,  3.6000,  0.0000,  9.1500,  9.0200,
 exa_co2          = 219.00,  219.00,  219.00,  1422.0,  1422.0,  1422.0,  0.0000,  0.0000,  0.0000,
 exa_nox          = 0.3000,  1.1200,  0.3000,  9.2000,  9.2000,  9.2000,  0.0000,  0.1320,  0.1290,
 exa_so2          = 0.0290,  0.0140,  0.0210,  0.6100,  0.6100,  0.6100,  0.0000,  0.0097,  0.0093,
 exa_c2h5oh       = 0.5080,  0.2500,  0.5080,  0.6100,  0.6100,  0.6100,  0.0000,  0.0790,  0.3050,
 exa_hcho         = 0.0089,  0.0110,  0.0098,  0.6100,  0.6100,  0.6100,  0.0000,  0.0152,  0.0155,
 exa_ald          = 0.0140,  0.0300,  0.0220,  0.6100,  0.6100,  0.6100,  0.0000,  0.0164,  0.0188,
 exa_pm           = 0.0200,  0.0200,  0.0200,  0.2770,  0.2770,  0.2770,  0.0000,  0.0500,  0.0500,
 exa_voc          = 0.4250,  1.3000,  0.4340,  2.0500,  2.0500,  2.0500,  0.0000,  1.0800,  1.0800,
 vap_voc          = 0.2300,  0.2500,  0.2400,  0.0000,  0.0000,  0.0000,  0.0000,  0.0000,  0.0000,
 liq_voc          = 2.0000,  1.5000,  1.7500,  0.0000,  0.0000,  0.0000,  0.0000,  1.2000,  1.2000,
/
 
&intensidade_uso                  ! ano 2018
 kmd_veic123      = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 1, 2 E 3
 kmd_veic4a       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 4A
 kmd_veic4b       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 4B
 kmd_veic4c       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 4C
 kmd_veic5        = 0.,           ! QUILOMETRAGEM DIARIA - VEICULOS 5
 kmd_veic6a       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 6A
 kmd_veic6b       = xx.xx,        ! QUILOMETRAGEM DIARIA - VEICULOS 6B
/
```

The model domain area covers different "UF" or states:

|UF code |	Federation Unit | UF|
|----------|------------------------ |---|
31	|Minas Gerais |	MG
32	|Espírito Santo |	ES
33	|Rio de Janeiro |	RJ
35	|São Paulo	|SP
41 | Paraná	|PR
42 | Santa Catarina|	SC
43 | Rio Grande do Su| RS
50|Mato Grosso do Sul|MS
52 | Goiás| GO

So, our objetive is to obtain results about `caracteristicas_frota`, and `intensidade_uso`. The information collected is in the Excel File `DATA_EF.xlsx`.

## Fleet Characteristics
Based on `vehCET`, fleet fractions were calculated. So, for now we have information about the fraction by vehicle type:

```
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
```

For this first task, we need to finalize with the calculation of `frota_veicular` (total fleet). To do this, we need to calculate the number of vehicles inside our domain area, approximately:

Domain | Point        | Longitude (º) | Latitude (º)
-------| ------------ |-------------- | ------------
D01    | South-west   | -53.53        |  -27.70
.       | North-east   | -39.69        |  -19.30
D02    | South-west   | -49.01        |  -25.05
.       | North-east   | -44.36        |  -21.64


The equivalent category from DENATRAM to LAPAt is understandable as following:

DENATRAN category | Category for Emissions Analysis
------------------| -----------------| 
AUTOMOVEL | Passenger Car (PC)
BONDE | -
CAMINHAO | Heavy Truck (HT)
CAMINHAO TRATOR | Light Truck (LT)
| Semi Light Truck (SLT)
|Medium Truck (MT)
| Semi Heavy Truck (SHT)
CAMINHONETE | Passenger Car (PC)
CAMIONETA | Passenger Car (PC)
CHASSI PLATAF | -
CICLOMOTOR | Motorcycle (MC)
MICRO-ONIBUS | Small Urban Bus (SUB)
MOTOCICLETA | Motorcycle (MC)
MOTONETA | Motorcycle (MC)
ONIBUS | Urban Bus (UB)
| Urban Bus Articulated (UBA)
QUADRICICLO | -
REBOQUE | -
SEMI-REBOQUE | -
SIDE-CAR | -
OUTROS | -
TRATOR ESTEI | Considered as Truck
TRATOR RODAS | Considered as Truck
TRICICLO | -
UTILITARIO | Light Commercial Vehicles (LCV)

### Emissions Calculation for the Modeling Domain based on Top-Down aproach
Emissions showed in `emCET` represents only for São Paulo state. We are going to calculate equivalent emissions for our modeling domain, based on number of vehicles

Total pollutant emissions (units in kt/year) from vehicles of São Paulo state (E$_{SP}$) compared with Model Domain. Based on these results, we can calculate representative total emissions (E$_{MD}$) of the modeling domain. To do this, we use a Top-Down approximation:

E_SP (kt)  -> 28~223~364 

E_d01 (kt)  -> xxxxx veh

E_d02 (kt)  -> xxxxx veh
