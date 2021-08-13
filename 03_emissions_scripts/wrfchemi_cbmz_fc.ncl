;************************************************************************************************************************************
; Pre-processador quimico gerador do arquivo de emissoes veiculares necessario para executar o modelo WRF-Chem com os esquemas       
; CBMZ para a fase gasosa e MOSAIC para aerossois. Ver especies no arquivo registry.chem
; Distribuicao espacial baseada em um modelo de vias (OpenStreetMap - QGIS). Arquivo grade9x9.txt neste exemplo 
; Distribuicao temporal e fracionamento VOC/PM segundo o arquivo emi_wrf_6veic.f90
; Copyleft: LAPAt
;************************************************************************************************************************************
; Lista de arquivos necessarios
; - namelist.emi: lista as variaveis caracteristicas da grade e de uso veicular
; - wrfinput_d01: grade WRF para interpolacao
; - grid3km_113x102.txt: 6 colunas (ponto de grade, longitude, latitude, road_1, road_2, road_3). O numero de filas calcula-se
;   como = n_col*n_fil
;   road_1: SUMlongkm
;   road_2: SUMmainroa
;   road_3: grau_urba
; - voc_split_cbmz-mosaic.txt: arquivo com o split para COVs
; Lista de arquivos que produz
; - wrfchemi_00z_d01_vias: arquivo de emissao das 00 ate 11 h
; - wrfchemi_12z_d01_vias: arquivo de emissao das 12 ate 23 h
; Executar seguidamente depois de ter executado o arquivo real.exe: ncl vehicular_emissions_opera.ncl
;------------------------------------------------------------------------------------------------------------------------------------
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl" 
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"
;------------------------------------------------------------------------------------------------------------------------------------
begin
;------------------------------------------------------------------------------------------------------------------------------------
 fil                          = "namelist_fc.emi"
 path_wrfinput                = systemfunc("grep path_wrfinput "+fil+" | cut -f2 -d'=' | cut -f2 -d' '")  
 wrfinput                     = addfile(path_wrfinput,"r")
;------------------------------------------------------------------------------------------------------------------------------------
 dx                           = stringtofloat(systemfunc("grep -w dx "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))      
 dy                           = stringtofloat(systemfunc("grep -w dy "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))       
 n_col                        = stringtoint(systemfunc("grep -w nx   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))       
 n_fil                        = stringtoint(systemfunc("grep -w ny   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 n_tim                        = 24      ; 24 horas (1 dia)
 n_lev                        = 1       ; superficie
 n_esp                        = 46      ; especies quimicas principais no mecanismo quimico CBMZ/MOSAIC
 nom_esp                      = (/"E_SO2","E_NO","E_ALD","E_HCHO","E_ORA2","E_NH3","E_HC3","E_HC5" \
                                 ,"E_HC8","E_ETH","E_CO","E_CO2","E_OL2","E_OLT","E_OLI","E_TOL"   \
				 ,"E_XYL","E_KET","E_CSL","E_ISO","E_NO2","E_CH3OH","E_C2H5OH"     \
			         ,"E_PM25I","E_PM25J","E_SO4I","E_SO4J","E_NO3I","E_NO3J","E_ORGI" \
				 ,"E_ORGJ","E_ECI","E_ECJ","E_NAAI","E_NAAJ","E_SO4C","E_NO3C"     \
				 ,"E_ORGC","E_ECC","E_ORGI_A","E_ORGJ_A","E_ORGI_BB","E_ORGJ_BB"   \
				 ,"E_CO_A","E_CO_BB","E_PM_10"/)
;------------------------------------------------------------------------------------------------------------------------------------
 frota                        = stringtofloat(systemfunc("grep -w frota_veicular   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 gasolina                     = stringtofloat(systemfunc("grep -w veic_gasolina    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 etanol                       = stringtofloat(systemfunc("grep -w veic_etanol      "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 flex                         = stringtofloat(systemfunc("grep -w veic_flex        "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 caminhoes                    = stringtofloat(systemfunc("grep -w veic_caminhoes   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 urbanos                      = stringtofloat(systemfunc("grep -w veic_urbanos     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 rodoviarios                  = stringtofloat(systemfunc("grep -w veic_rodoviarios "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 taxis                        = stringtofloat(systemfunc("grep -w veic_taxis       "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 moto_gaso                    = stringtofloat(systemfunc("grep -w veic_moto_gaso   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 moto_flex                    = stringtofloat(systemfunc("grep -w veic_moto_flex   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 gasolina                     = gasolina*frota
 etanol                       = etanol*frota
 flex                         = flex*frota
 caminhoes                    = caminhoes*frota
 urbanos                      = urbanos*frota
 rodoviarios                  = rodoviarios*frota
 taxis                        = taxis*frota
 moto_gaso                    = moto_gaso*frota
 moto_flex                    = moto_flex*frota
 pesados                      = caminhoes+urbanos+rodoviarios
 pl                           = stringtofloat(systemfunc("grep -w frota_ativa "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 frota_final                  = (frota-pesados)*pl+pesados
 fc_co                        = stringtofloat(systemfunc("grep -w fc_co     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_co2                       = stringtofloat(systemfunc("grep -w fc_co2    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_no                        = stringtofloat(systemfunc("grep -w fc_no     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_no2                       = stringtofloat(systemfunc("grep -w fc_no2    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_so2                       = stringtofloat(systemfunc("grep -w fc_so2    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_c2h5oh                    = stringtofloat(systemfunc("grep -w fc_c2h5oh "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_hcho                      = stringtofloat(systemfunc("grep -w fc_hcho   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_ald                       = stringtofloat(systemfunc("grep -w fc_ald    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_pm                        = stringtofloat(systemfunc("grep -w fc_pm     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 fc_voc                       = stringtofloat(systemfunc("grep -w fc_voc    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
;------------------------------------------------------------------------------------------------------------------------------------
 path_map_vias                = systemfunc("grep path_map_vias "+fil+" | cut -f2 -d'=' | cut -f2 -d' '")       
 map_vias                     = asciiread(path_map_vias,(/n_fil*n_col,4/),"float")
; map_ied                      = reshape(map_vias(:,3),(/n_fil,n_col/))
 map_ied                      = new((/n_fil,n_col/),"float")
 do i = 0, n_fil-1 
  map_ied(i,:)                = map_vias(i*n_col:(i+1)*n_col-1,3)
 end do
 sum_ied                      = 0.
 do i = 0, n_col-1
  do j = 0, n_fil-1
   sum_ied                    = sum_ied+map_ied(j,i)
  end do
 end do
 fp                           = frota_final/sum_ied          ; numero de veiculos em cada ponto de grade 
;------------------------------------------------------------------------------------------------------------------------------------
 lon1d                        = map_vias(0:n_col-1,1)
 lat1d                        = new((/n_fil/),float)
 do i = 0, n_fil-1
  lat1d(i)                    = map_vias(n_fil*n_col-n_col*i-1,2)
 end do
;------------------------------------------------------------------------------------------------------------------------------------
 hrsplt_co                    = new(n_tim,float)
 hrsplt_no                    = new(n_tim,float)
 do n = 1, n_tim
  n0 = n - 1
  hrsplt_co(n0)               = stringtofloat(systemfunc("echo `grep -A 1 hrsplt_co "+fil+" | cut -f2 -d'='` | cut -f"+n+" -d','"))
  hrsplt_no(n0)               = stringtofloat(systemfunc("echo `grep -A 1 hrsplt_no "+fil+" | cut -f2 -d'='` | cut -f"+n+" -d','"))
 end do  
;------------------------------------------------------------------------------------------------------------------------------------
 path_voc                     = systemfunc("grep path_voc "+fil+" | cut -f2 -d'=' | cut -f2 -d' '")       
 voc                          = readAsciiTable(path_voc,10,"float",18)
 e_eth                        = new((/n_fil,n_col,n_tim/),float)
 e_hc3                        = new((/n_fil,n_col,n_tim/),float)
 e_hc5                        = new((/n_fil,n_col,n_tim/),float)
 e_hc8                        = new((/n_fil,n_col,n_tim/),float)
 e_ol2                        = new((/n_fil,n_col,n_tim/),float)
 e_olt                        = new((/n_fil,n_col,n_tim/),float)
 e_oli                        = new((/n_fil,n_col,n_tim/),float)
 e_iso                        = new((/n_fil,n_col,n_tim/),float)
 e_tol                        = new((/n_fil,n_col,n_tim/),float)
 e_xyl                        = new((/n_fil,n_col,n_tim/),float)
 e_ket                        = new((/n_fil,n_col,n_tim/),float)
 e_ald                        = new((/n_fil,n_col,n_tim/),float)
 e_hcho                       = new((/n_fil,n_col,n_tim/),float)
 e_ora2                       = new((/n_fil,n_col,n_tim/),float)
 e_nh3                        = new((/n_fil,n_col,n_tim/),float)
 e_csl                        = new((/n_fil,n_col,n_tim/),float)
 e_co                         = new((/n_fil,n_col,n_tim/),float)
 e_co2                        = new((/n_fil,n_col,n_tim/),float)
 e_no                         = new((/n_fil,n_col,n_tim/),float)
 e_no2                        = new((/n_fil,n_col,n_tim/),float)
 e_so2                        = new((/n_fil,n_col,n_tim/),float)
 e_ch3oh                      = new((/n_fil,n_col,n_tim/),float)
 e_c2h5oh                     = new((/n_fil,n_col,n_tim/),float)
 e_pm                         = new((/n_fil,n_col,n_tim/),float)
 e_pm25i                      = new((/n_fil,n_col,n_tim/),float)
 e_pm25j                      = new((/n_fil,n_col,n_tim/),float)
 e_so4i                       = new((/n_fil,n_col,n_tim/),float)
 e_so4j                       = new((/n_fil,n_col,n_tim/),float)
 e_no3i                       = new((/n_fil,n_col,n_tim/),float)
 e_no3j                       = new((/n_fil,n_col,n_tim/),float)
 e_orgi                       = new((/n_fil,n_col,n_tim/),float)
 e_orgj                       = new((/n_fil,n_col,n_tim/),float)
 e_eci                        = new((/n_fil,n_col,n_tim/),float)
 e_ecj                        = new((/n_fil,n_col,n_tim/),float)
 e_naai                       = new((/n_fil,n_col,n_tim/),float)
 e_naaj                       = new((/n_fil,n_col,n_tim/),float)
 e_so4c                       = new((/n_fil,n_col,n_tim/),float)
 e_no3c                       = new((/n_fil,n_col,n_tim/),float)
 e_orgc                       = new((/n_fil,n_col,n_tim/),float)
 e_ecc                        = new((/n_fil,n_col,n_tim/),float)
 e_orgi_a                     = new((/n_fil,n_col,n_tim/),float)           
 e_orgj_a                     = new((/n_fil,n_col,n_tim/),float)
 e_orgi_bb                    = new((/n_fil,n_col,n_tim/),float)
 e_orgj_bb                    = new((/n_fil,n_col,n_tim/),float)
 e_co_a                       = new((/n_fil,n_col,n_tim/),float)
 e_co_bb                      = new((/n_fil,n_col,n_tim/),float)
 e_pm_10                      = new((/n_fil,n_col,n_tim/),float)
;------------------------------------------------------------------------------------------------------------------------------------
 veic1                        = new((/n_fil,n_col/),float)
 veic2                        = new((/n_fil,n_col/),float)
 veic3                        = new((/n_fil,n_col/),float)
 veic4a                       = new((/n_fil,n_col/),float)
 veic4b                       = new((/n_fil,n_col/),float)
 veic4c                       = new((/n_fil,n_col/),float)
 veic5                        = new((/n_fil,n_col/),float)
 veic6a                       = new((/n_fil,n_col/),float)
 veic6b                       = new((/n_fil,n_col/),float)
 veic_co                      = new((/n_fil,n_col/),float)
 veic_co2                     = new((/n_fil,n_col/),float)                 
 veic_nox                     = new((/n_fil,n_col/),float) 
 veic_no                      = new((/n_fil,n_col/),float)
 veic_no2                     = new((/n_fil,n_col/),float)
 veic_so2                     = new((/n_fil,n_col/),float)
 veic_c2h5oh                  = new((/n_fil,n_col/),float)
 veic_hcho                    = new((/n_fil,n_col/),float)
 veic_ald                     = new((/n_fil,n_col/),float)
 veic_voc                     = new((/n_fil,n_col,15/),float)       ; voc_split com 15 especies
 veic_pm                      = new((/n_fil,n_col/),float)
;------------------------------------------------------------------------------------------------------------------------------------
; Intensidad de uso (km/dia)
 kmd_veic123                  = stringtofloat(systemfunc("grep -w kmd_veic123 "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 kmd_veic4a                   = stringtofloat(systemfunc("grep -w kmd_veic4a  "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 kmd_veic4b                   = stringtofloat(systemfunc("grep -w kmd_veic4b  "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 kmd_veic4c                   = stringtofloat(systemfunc("grep -w kmd_veic4c  "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 kmd_veic5                    = stringtofloat(systemfunc("grep -w kmd_veic5   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 kmd_veic6a                   = stringtofloat(systemfunc("grep -w kmd_veic6a  "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 kmd_veic6b                   = stringtofloat(systemfunc("grep -w kmd_veic6b  "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
;------------------------------------------------------------------------------------------------------------------------------------
 n_veic                       = stringtoint(systemfunc("grep n_veic        "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 exa_co                       = new(n_veic,float)
 exa_co2                      = new(n_veic,float)
 exa_nox                      = new(n_veic,float)
 exa_so2                      = new(n_veic,float)
 exa_c2h5oh                   = new(n_veic,float)
 exa_hcho                     = new(n_veic,float)
 exa_ald                      = new(n_veic,float)
 exa_pm                       = new(n_veic,float)
 exa_voc                      = new(n_veic,float)
 vap_voc                      = new(n_veic,float)
 liq_voc                      = new(n_veic,float)
 do n = 1, n_veic
  n0 = n - 1
  exa_co(n0)                  = stringtofloat(systemfunc("grep -w exa_co     "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_co2(n0)                 = stringtofloat(systemfunc("grep -w exa_co2    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_nox(n0)                 = stringtofloat(systemfunc("grep -w exa_nox    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_so2(n0)                 = stringtofloat(systemfunc("grep -w exa_so2    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_c2h5oh(n0)              = stringtofloat(systemfunc("grep -w exa_c2h5oh "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_hcho(n0)                = stringtofloat(systemfunc("grep -w exa_hcho   "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_ald(n0)                 = stringtofloat(systemfunc("grep -w exa_ald    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_pm(n0)                  = stringtofloat(systemfunc("grep -w exa_pm     "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  exa_voc(n0)                 = stringtofloat(systemfunc("grep -w exa_voc    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  vap_voc(n0)                 = stringtofloat(systemfunc("grep -w vap_voc    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
  liq_voc(n0)                 = stringtofloat(systemfunc("grep -w liq_voc    "+fil+" | cut -f2 -d'=' | cut -f"+n+" -d','"))
 end do 
;------------------------------------------------------------------------------------------------------------------------------------
 f_fina_total                 = stringtofloat(systemfunc("grep -w f_fina_total   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_grossa_total               = stringtofloat(systemfunc("grep -w f_grossa_total "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_fina_so4                   = stringtofloat(systemfunc("grep -w f_fina_so4     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_fina_no3                   = stringtofloat(systemfunc("grep -w f_fina_no3     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_fina_org                   = stringtofloat(systemfunc("grep -w f_fina_org     "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_fina_ec                    = stringtofloat(systemfunc("grep -w f_fina_ec      "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_fina_pm25                  = stringtofloat(systemfunc("grep -w f_fina_pm25    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_grossa_so4                 = stringtofloat(systemfunc("grep -w f_grossa_so4   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_grossa_no3                 = stringtofloat(systemfunc("grep -w f_grossa_no3   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_grossa_org                 = stringtofloat(systemfunc("grep -w f_grossa_org   "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 f_grossa_ec                  = stringtofloat(systemfunc("grep -w f_grossa_ec    "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 i_so4                        = stringtofloat(systemfunc("grep -w i_so4          "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 j_so4                        = stringtofloat(systemfunc("grep -w j_so4          "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 i_no3                        = stringtofloat(systemfunc("grep -w i_no3          "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 j_no3                        = stringtofloat(systemfunc("grep -w j_no3          "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 i_org                        = stringtofloat(systemfunc("grep -w i_org          "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 j_org                        = stringtofloat(systemfunc("grep -w j_org          "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 i_ec                         = stringtofloat(systemfunc("grep -w i_ec           "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 j_ec                         = stringtofloat(systemfunc("grep -w j_ec           "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 i_pm25                       = stringtofloat(systemfunc("grep -w i_pm25         "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
 j_pm25                       = stringtofloat(systemfunc("grep -w j_pm25         "+fil+" | cut -f2 -d'=' | cut -f1 -d','"))
;------------------------------------------------------------------------------------------------------------------------------------
 do ihr = 0, n_tim-1
  total_co                    = 0.
  total_co2                   = 0.
  total_nox                   = 0.
  total_so2                   = 0.
  total_c2h5oh                = 0.
  total_hcho                  = 0.
  total_ald                   = 0.
  total_pm                    = 0.
  total_gas_vapors            = 0.
  total_gas_liquid            = 0.
  total_gas_exhaust           = 0.
  total_alc_vapors            = 0.
  total_alc_liquid            = 0.
  total_alc_exhaust           = 0.
  total_die_vapors            = 0.
  total_die_liquid            = 0.
  total_die_exhaust           = 0.
  do j = 0, n_col-1       
   do i = 0, n_fil-1   
;------------------------------------------------------------------------------------------------------------------------------------
; fraccion flota vehicular para 2012                                                              
    veic1(i,j)                = map_ied(i,j)*fp*(gasolina*pl/frota_final)    
    veic2(i,j)                = map_ied(i,j)*fp*(etanol*pl/frota_final)       
    veic3(i,j)                = map_ied(i,j)*fp*(flex*pl/frota_final)         
    veic4a(i,j)               = map_ied(i,j)*fp*(caminhoes/frota_final)         
    veic4b(i,j)               = map_ied(i,j)*fp*(urbanos/frota_final)          
    veic4c(i,j)               = map_ied(i,j)*fp*(rodoviarios/frota_final)     
    veic5(i,j)                = map_ied(i,j)*fp*(taxis*pl/frota_final)        
    veic6a(i,j)               = map_ied(i,j)*fp*(moto_gaso*pl/frota_final)
    veic6b(i,j)               = map_ied(i,j)*fp*(moto_flex*pl/frota_final)
;------------------------------------------------------------------------------------------------------------------------------------
; FE experimento tuneles + Cetesb, 2010 + dados petrobras junho de 2014 para veiculos leves com gasolina e etanol e motos. 
; Fatores dos pesados mantido - cetesb+tuneis
; Fatores de emissao da exaustao - Leila. 
; Incluindo 28-07-2014 motos flex - foi ponderado os flex, considerando 50% das motos flex usando etanol
    veic_co(i,j)              = veic1(i,j)*exa_co(0)*kmd_veic123+veic2(i,j)*exa_co(1)*kmd_veic123           \
                                +veic3(i,j)*exa_co(2)*kmd_veic123+veic4a(i,j)*exa_co(3)*kmd_veic4a          \
		                +veic4b(i,j)*exa_co(4)*kmd_veic4b+veic4c(i,j)*exa_co(5)*kmd_veic4c          \     
                                +veic5(i,j)*exa_co(6)*kmd_veic5+veic6a(i,j)*exa_co(7)*kmd_veic6a            \
		                +veic6b(i,j)*exa_co(8)*kmd_veic6b
    veic_co2(i,j)             = veic1(i,j)*exa_co2(0)*kmd_veic123+veic2(i,j)*exa_co2(1)*kmd_veic123         \
                                +veic3(i,j)*exa_co2(2)*kmd_veic123+veic4a(i,j)*exa_co2(3)*kmd_veic4a        \
		                +veic4b(i,j)*exa_co2(4)*kmd_veic4b+veic4c(i,j)*exa_co2(5)*kmd_veic4c        \     
                                +veic5(i,j)*exa_co2(6)*kmd_veic5+veic6a(i,j)*exa_co2(7)*kmd_veic6a          \
		                +veic6b(i,j)*exa_co2(8)*kmd_veic6b
; Coloquei os fatores de NOx - leila 
    veic_nox(i,j)             = veic1(i,j)*exa_nox(0)*kmd_veic123+veic2(i,j)*exa_nox(1)*kmd_veic123         \
                                +veic3(i,j)*exa_nox(2)*kmd_veic123+veic4a(i,j)*exa_nox(3)*kmd_veic4a        \
                                +veic4b(i,j)*exa_nox(4)*kmd_veic4b+veic4c(i,j)*exa_nox(5)*kmd_veic4c        \ 
                                +veic5(i,j)*exa_nox(6)*kmd_veic5+veic6a(i,j)*exa_nox(7)*kmd_veic6a          \
				+veic6b(i,j)*exa_nox(8)*kmd_veic6b
    veic_no(i,j)              = 0.90*veic_nox(i,j)  
    veic_no2(i,j)             = 0.10*veic_nox(i,j) 
    veic_so2(i,j)             = veic1(i,j)*exa_so2(0)*kmd_veic123+veic2(i,j)*exa_so2(1)*kmd_veic123         \
                                +veic3(i,j)*exa_so2(2)*kmd_veic123+veic4a(i,j)*exa_so2(3)*kmd_veic4a        \
				+veic4b(i,j)*exa_so2(4)*kmd_veic4b+veic4c(i,j)*exa_so2(5)*kmd_veic4c        \ 
                                +veic5(i,j)*exa_so2(6)*kmd_veic5+veic6a(i,j)*exa_so2(7)*kmd_veic6a          \
				+veic6b(i,j)*exa_so2(8)*kmd_veic6b
;------ Leila -- 22-07-2014 ---- inserindo fatores de emiss\E3o de etanol, formal e acetal da exaust\E3o para gasolina e alcool. 
; No voc-split na exaust\E3o estes foram zeradas
    veic_c2h5oh(i,j)          = veic1(i,j)*exa_c2h5oh(0)*kmd_veic123+veic2(i,j)*exa_c2h5oh(1)*kmd_veic123   \
                                +veic3(i,j)*exa_c2h5oh(2)*kmd_veic123+veic4a(i,j)*exa_c2h5oh(3)*kmd_veic4a  \
				+veic4b(i,j)*exa_c2h5oh(4)*kmd_veic4b+veic4c(i,j)*exa_c2h5oh(5)*kmd_veic4c  \
                                +veic5(i,j)*exa_c2h5oh(6)*kmd_veic5+veic6a(i,j)*exa_c2h5oh(7)*kmd_veic6a    \
			        +veic6b(i,j)*exa_c2h5oh(8)*kmd_veic6b
    veic_hcho(i,j)            = veic1(i,j)*exa_hcho(0)*kmd_veic123+veic2(i,j)*exa_hcho(1)*kmd_veic123       \
                                +veic3(i,j)*exa_hcho(2)*kmd_veic123+veic4a(i,j)*exa_hcho(3)*kmd_veic4a      \
		                +veic4b(i,j)*exa_hcho(4)*kmd_veic4b+veic4c(i,j)*exa_hcho(5)*kmd_veic4c      \
                                +veic5(i,j)*exa_hcho(6)*kmd_veic5+veic6a(i,j)*exa_hcho(7)*kmd_veic6a        \
				+veic6b(i,j)*exa_hcho(8)*kmd_veic6b
    veic_ald(i,j)             = veic1(i,j)*exa_ald(0)*kmd_veic123+veic2(i,j)*exa_ald(1)*kmd_veic123         \
                                +veic3(i,j)*exa_ald(2)*kmd_veic123+veic4a(i,j)*exa_ald(3)*kmd_veic4a        \
				+veic4b(i,j)*exa_ald(4)*kmd_veic4b+veic4c(i,j)*exa_ald(5)*kmd_veic4c        \ 
                                +veic5(i,j)*exa_ald(6)*kmd_veic5+veic6a(i,j)*exa_ald(7)*kmd_veic6a          \
				+veic6b(i,j)*exa_ald(8)*kmd_veic6b
;--------------------------------------------------------------------------------------------------------------------------
    veic_pm(i,j)              = veic1(i,j)*exa_pm(0)*kmd_veic123+veic2(i,j)*exa_pm(1)*kmd_veic123           \
                                +veic3(i,j)*exa_pm(2)*kmd_veic123+veic4a(i,j)*exa_pm(3)*kmd_veic4a          \
                                +veic4b(i,j)*exa_pm(4)*kmd_veic4b+veic4c(i,j)*exa_pm(5)*kmd_veic4c          \ 
                                +veic5(i,j)*exa_pm(6)*kmd_veic5+veic6a(i,j)*exa_pm(7)*kmd_veic6a            \
				+veic6b(i,j)*exa_pm(8)*kmd_veic6b
;------------------------------------------------------------------------------------------------------------------------------------
;- VOCs (Cetesb, 2010) -------------------------------------------------------------------------------------------------------------------------------------
;- operacoes de transferencia de combustivel (vapors) -------------------------------------------------------------------------------------------------------------------------------------
    veic_voc_vapors_veic1     = veic1(i,j)*vap_voc(0)*kmd_veic123
    veic_voc_vapors_veic2     = veic2(i,j)*vap_voc(1)*kmd_veic123
    veic_voc_vapors_veic3     = veic3(i,j)*vap_voc(2)*kmd_veic123
; Leila, por que zero para veic3, isso nao vai implicar em zerar a emissao evaporativa de voc dos flex???
; Adicionei fator para veic3 - para SP em 2011 flex 50% usando etanol 
    veic_voc_vapors_veic4a    = veic4a(i,j)*vap_voc(3)*kmd_veic4a
    veic_voc_vapors_veic4b    = veic4b(i,j)*vap_voc(4)*kmd_veic4b
    veic_voc_vapors_veic4c    = veic4c(i,j)*vap_voc(5)*kmd_veic4c
    veic_voc_vapors_veic5     = veic5(i,j)*vap_voc(6)*kmd_veic5
    veic_voc_vapors_veic6a    = veic6a(i,j)*vap_voc(7)*kmd_veic6a
    veic_voc_vapors_veic6b    = veic6b(i,j)*vap_voc(8)*kmd_veic6b
;------------------------------------------------------------------------------------------------------------------------------------
;- carter e evaporativa (liquid)  -------------------------------------------------------------------------------------------------------------------------------------
; Leila --- fonte Cetesb, 2010 ---
    veic_voc_liquid_veic1     = veic1(i,j)*liq_voc(0)*kmd_veic123
    veic_voc_liquid_veic2     = veic2(i,j)*liq_voc(1)*kmd_veic123
    veic_voc_liquid_veic3     = veic3(i,j)*liq_voc(2)*kmd_veic123
; Leila, por que zero para veic3, isso nao vai implicar em zerar a emissao evaporativa de voc dos flex???
; Adicionei fator para veic3 - para SP em 2011 flex 50% usando etanol 
    veic_voc_liquid_veic4a    = veic4a(i,j)*liq_voc(3)*kmd_veic4a
    veic_voc_liquid_veic4b    = veic4b(i,j)*liq_voc(4)*kmd_veic4b
    veic_voc_liquid_veic4c    = veic4c(i,j)*liq_voc(5)*kmd_veic4c
    veic_voc_liquid_veic5     = veic5(i,j)*liq_voc(6)*kmd_veic5
    veic_voc_liquid_veic6a    = veic6a(i,j)*liq_voc(7)*kmd_veic6a
    veic_voc_liquid_veic6b    = veic6b(i,j)*liq_voc(8)*kmd_veic6b
;------------------------------------------------------------------------------------------------------------------------------------
;- tubo de escapamento (exhaust) Leila
; NHMC + E_KET E_CH3OH, retirado split dos demais da exaustao
; usando fator da petrobras de NMHC
;------------------------------------------------------------------------------------------------------------------------------------
    veic_voc_exhaust_veic1    = veic1(i,j)*exa_voc(0)*kmd_veic123
    veic_voc_exhaust_veic2    = veic2(i,j)*exa_voc(1)*kmd_veic123
    veic_voc_exhaust_veic3    = veic3(i,j)*exa_voc(2)*kmd_veic123
    veic_voc_exhaust_veic4a   = veic4a(i,j)*exa_voc(3)*kmd_veic4a
    veic_voc_exhaust_veic4b   = veic4b(i,j)*exa_voc(4)*kmd_veic4b
    veic_voc_exhaust_veic4c   = veic4c(i,j)*exa_voc(5)*kmd_veic4c
    veic_voc_exhaust_veic5    = veic5(i,j)*exa_voc(6)*kmd_veic5
    veic_voc_exhaust_veic6a   = veic6a(i,j)*exa_voc(7)*kmd_veic6a
    veic_voc_exhaust_veic6b   = veic6b(i,j)*exa_voc(8)*kmd_veic6b
;------------------------------------------------------------------------------------------------------------------------------------
    total_co                  = total_co+veic_co(i,j)
    total_co2                 = total_co2+veic_co2(i,j)
    total_nox                 = total_nox+veic_no(i,j)*fc_no+veic_no2(i,j)*fc_no2           ; fator de correcao
    total_so2                 = total_so2+veic_so2(i,j)
    total_c2h5oh              = total_c2h5oh+veic_c2h5oh(i,j)
    total_hcho                = total_hcho+veic_hcho(i,j)
    total_ald                 = total_ald+veic_ald(i,j)
    total_pm                  = total_pm+veic_pm(i,j)
;------------------------------------------------------------------------------------------------------------------------------------
    total_gas_vapors          = total_gas_vapors+veic_voc_vapors_veic1+veic_voc_vapors_veic6a
    total_gas_liquid          = total_gas_liquid+veic_voc_liquid_veic1+veic_voc_liquid_veic6a
    total_gas_exhaust         = total_gas_exhaust+veic_voc_exhaust_veic1+veic_voc_exhaust_veic6a
;------------------------------------------------------------------------------------------------------------------------------------
    total_alc_vapors          = total_alc_vapors+veic_voc_vapors_veic2+veic_voc_vapors_veic3+veic_voc_vapors_veic6b
    total_alc_liquid          = total_alc_liquid+veic_voc_liquid_veic2+veic_voc_liquid_veic3+veic_voc_vapors_veic6b
    total_alc_exhaust         = total_alc_exhaust+veic_voc_exhaust_veic2+veic_voc_exhaust_veic3+veic_voc_vapors_veic6b
;------------------------------------------------------------------------------------------------------------------------------------
    total_die_vapors          = total_die_vapors+veic_voc_vapors_veic4a+veic_voc_vapors_veic4b+veic_voc_vapors_veic4c
    total_die_liquid          = total_die_liquid+veic_voc_liquid_veic4a+veic_voc_liquid_veic4b+veic_voc_liquid_veic4c
    total_die_exhaust         = total_die_exhaust+veic_voc_exhaust_veic4a+veic_voc_exhaust_veic4b \
                                +veic_voc_exhaust_veic4c
;------------------------------------------------------------------------------------------------------------------------------------
    veic_co(i,j)              = veic_co(i,j)/28.                               ;    mol/dia
    veic_co2(i,j)             = veic_co2(i,j)/44.                              ;    mol/dia
    veic_no(i,j)              = veic_no(i,j)/30.                               ;    mol/dia
    veic_no2(i,j)             = veic_no2(i,j)/46.                              ;    mol/dia
    veic_so2(i,j)             = veic_so2(i,j)/64.                              ;    mol/dia
    veic_c2h5oh(i,j)          = veic_c2h5oh(i,j)/46.                           ;    mol/dia
    veic_hcho(i,j)            = veic_hcho(i,j)/30.                             ;    mol/dia
    veic_ald(i,j)             = veic_ald(i,j)/44.                              ;    mol/dia
    veic_pm(i,j)              = veic_pm(i,j)/1.                                ;    g/dia
;------------------------------------------------------------------------------------------------------------------------------------
    veic_co(i,j)              = veic_co(i,j)*hrsplt_co(ihr)/(dx*dy)            ;    mol/km^2/hr
    veic_co2(i,j)             = veic_co2(i,j)*hrsplt_co(ihr)/(dx*dy)           ;    mol/km^2/hr
    veic_no(i,j)              = veic_no(i,j)*hrsplt_no(ihr)/(dx*dy)            ;    mol/km^2/hr 
    veic_no2(i,j)             = veic_no2(i,j)*hrsplt_no(ihr)/(dx*dy)           ;    mol/km^2/hr 
    veic_so2(i,j)             = veic_so2(i,j)*hrsplt_no(ihr)/(dx*dy)           ;    mol/km^2/hr
    veic_c2h5oh(i,j)          = veic_c2h5oh(i,j)*hrsplt_co(ihr)/(dx*dy)        ;    mol/km^2/hr
    veic_hcho(i,j)            = veic_hcho(i,j)*hrsplt_co(ihr)/(dx*dy)          ;    mol/km^2/hr
    veic_ald(i,j)             = veic_ald(i,j)*hrsplt_co(ihr)/(dx*dy)           ;    mol/km^2/hr
    veic_pm(i,j)              = veic_pm(i,j)*hrsplt_no(ihr)/(3600.*dx*dy)      ;    ug/m^2/s        
    do ispec = 0, 14 ; atualizado em 09/11/2015
;- Falta incluir aqui o veic6b e veic6a Leila ---------------------------------------------------------------------------------------
;                                               +veic_voc_exhaust_veic3*voc(ispec,5)           \
; O numero 5 indica a categoria de veiculos movidos a alcool.
; Leila, porque voce esta considerando os flex dentro de esta categoria?
     veic_voc(i,j,ispec)      = (veic_voc_vapors_veic1*voc(ispec,1)                                             \
                                +veic_voc_vapors_veic6a*voc(ispec,1)                                            \
                                +veic_voc_vapors_veic2*voc(ispec,4)                                             \
                                +veic_voc_vapors_veic4a*voc(ispec,7)                                            \
                                +veic_voc_vapors_veic4b*voc(ispec,7)                                            \
                                +veic_voc_vapors_veic4c*voc(ispec,7)                                            \
				+0.5*(veic_voc_vapors_veic3*voc(ispec,1)+veic_voc_vapors_veic6b*voc(ispec,1))   \
				+0.5*(veic_voc_vapors_veic3*voc(ispec,4)+veic_voc_vapors_veic6b*voc(ispec,4))   \
                                +veic_voc_liquid_veic1*voc(ispec,2)                                             \
                                +veic_voc_liquid_veic6a*voc(ispec,2)                                            \      
                                +veic_voc_liquid_veic2*voc(ispec,5)                                             \
                                +veic_voc_liquid_veic4a*voc(ispec,8)                                            \
                                +veic_voc_liquid_veic4b*voc(ispec,8)                                            \
                                +veic_voc_liquid_veic4c*voc(ispec,8)                                            \
				+0.5*(veic_voc_liquid_veic3*voc(ispec,2)+veic_voc_liquid_veic6b*voc(ispec,2))   \
				+0.5*(veic_voc_liquid_veic3*voc(ispec,5)+veic_voc_liquid_veic6b*voc(ispec,5))   \  
                                +veic_voc_exhaust_veic1*voc(ispec,3)                                            \  
                                +veic_voc_exhaust_veic6a*voc(ispec,3)                                           \
                                +veic_voc_exhaust_veic2*voc(ispec,6)                                            \
                                +veic_voc_exhaust_veic4a*voc(ispec,9)                                           \
	                        +veic_voc_exhaust_veic4a*voc(ispec,9)                                           \
			        +veic_voc_exhaust_veic4a*voc(ispec,9)                                           \
				+0.5*(veic_voc_exhaust_veic3*voc(ispec,3)+veic_voc_exhaust_veic6b*voc(ispec,3)) \
				+0.5*(veic_voc_exhaust_veic3*voc(ispec,6)+veic_voc_exhaust_veic6b*voc(ispec,6)) \  		
				)*hrsplt_co(ihr)/(100.*dx*dy)     
    end do
;------------------------------------------------------------------------------------------------------------------------------------
    do ispec = 0, 11
     if(ispec.eq.0)then
      e_eth(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.1)then
      e_hc3(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.2)then
      e_hc5(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.3)then
      e_hc8(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.4)then
      e_ol2(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.5)then
      e_olt(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.6)then
      e_oli(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.7)then
      e_iso(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.8)then
      e_tol(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.9)then
      e_xyl(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.10)then
      e_ket(i,j,ihr)          = veic_voc(i,j,ispec)*fc_voc
     end if
     if(ispec.eq.11)then
      e_ch3oh(i,j,ihr)        = veic_voc(i,j,ispec)*fc_voc
     end if
; Leila verificar se precisa somar aqui veic_ald(i,j). 
; Angel - Leila, eu acho que aqui ja nao precisa considerar o etanol, acetal e formal, dado que linhas acima (onde se faz o
; o calculo dos FE) ja foram considerados individualmente.
    end do
    e_co(i,j,ihr)             = veic_co(i,j)*fc_co
    e_co2(i,j,ihr)            = veic_co2(i,j)*fc_co2
    e_no(i,j,ihr)             = veic_no(i,j)*fc_no
    e_no2(i,j,ihr)            = veic_no2(i,j)*fc_no2
    e_so2(i,j,ihr)            = veic_so2(i,j)*fc_so2
    e_ora2(i,j,ihr)           = 0.
    e_nh3(i,j,ihr)            = e_no(i,j,ihr)*0.034
    e_csl(i,j,ihr)            = 0.
    e_ald(i,j,ihr)            = (veic_ald(i,j)+veic_voc(i,j,14))*fc_ald          ; atualizado em 09/11/2015
    e_hcho(i,j,ihr)           = (veic_hcho(i,j)+veic_voc(i,j,13))*fc_hcho        ; atualizado em 09/11/2015
    e_c2h5oh(i,j,ihr)         = (veic_c2h5oh(i,j)+veic_voc(i,j,12))*fc_c2h5oh    ; atualizado em 09/11/2015
    e_pm(i,j,ihr)             = veic_pm(i,j)*fc_pm
;------------------------------------------------------------------------------------------------------------------------------------ ; nao alterei ainda os valores de particulado com base nos dados da petrobras - Leila
    e_pm25i(i,j,ihr)          = e_pm(i,j,ihr)*f_fina_total*f_fina_pm25*i_pm25
    e_pm25j(i,j,ihr)          = e_pm(i,j,ihr)*f_fina_total*f_fina_pm25*j_pm25
    e_so4i(i,j,ihr)           = e_pm(i,j,ihr)*f_fina_total*f_fina_so4*i_so4
    e_so4j(i,j,ihr)           = e_pm(i,j,ihr)*f_fina_total*f_fina_so4*j_so4
    e_no3i(i,j,ihr)           = e_pm(i,j,ihr)*f_fina_total*f_fina_no3*i_no3
    e_no3j(i,j,ihr)           = e_pm(i,j,ihr)*f_fina_total*f_fina_no3*j_no3
    e_orgi(i,j,ihr)           = e_pm(i,j,ihr)*f_fina_total*f_fina_org*i_org
    e_orgj(i,j,ihr)           = e_pm(i,j,ihr)*f_fina_total*f_fina_org*j_org
    e_eci(i,j,ihr)            = e_pm(i,j,ihr)*f_fina_total*f_fina_ec*i_ec
    e_ecj(i,j,ihr)            = e_pm(i,j,ihr)*f_fina_total*f_fina_ec*j_ec
    e_naai(i,j,ihr)           = 0.
    e_naaj(i,j,ihr)           = 0.
    e_so4c(i,j,ihr)           = e_pm(i,j,ihr)*f_grossa_so4
    e_no3c(i,j,ihr)           = e_pm(i,j,ihr)*f_grossa_no3
    e_orgc(i,j,ihr)           = e_pm(i,j,ihr)*f_grossa_org
    e_ecc(i,j,ihr)            = e_pm(i,j,ihr)*f_grossa_ec
    e_orgi_a(i,j,ihr)         = 0.
    e_orgj_a(i,j,ihr)         = 0.
    e_orgi_bb(i,j,ihr)        = 0.
    e_orgj_bb(i,j,ihr)        = 0.
    e_co_a(i,j,ihr)           = 0.
    e_co_bb(i,j,ihr)          = 0.
    e_pm_10(i,j,ihr)          = e_pm(i,j,ihr)*f_grossa_total
   end do
  end do
  if(ihr.eq.0)then
   total_co                   = total_co*365./10^9*fc_co
   total_co2                  = total_co2*365/10^9*fc_co2
   total_nox                  = total_nox*365./10^9                            ; fc_no e fc_no2 em linha 367
   total_so2                  = total_so2*365./10^9*fc_so2
   total_c2h5oh               = total_c2h5oh*365./10^9*fc_c2h5oh
   total_hcho                 = total_hcho*365./10^9*fc_hcho
   total_ald                  = total_ald*365./10^9*fc_ald
   total_pm                   = total_pm*365./10^9*fc_pm
   total_gas_vapors           = total_gas_vapors*365./10^9*fc_voc
   total_gas_liquid           = total_gas_liquid*365./10^9*fc_voc
   total_gas_exhaust          = total_gas_exhaust*365./10^9*fc_voc
   total_alc_vapors           = total_alc_vapors*365./10^9*fc_voc
   total_alc_liquid           = total_alc_liquid*365./10^9*fc_voc
   total_alc_exhaust          = total_alc_exhaust*365./10^9*fc_voc
   total_die_vapors           = total_die_vapors*365./10^9*fc_voc
   total_die_liquid           = total_die_liquid*365./10^9*fc_voc
   total_die_exhaust          = total_die_exhaust*365./10^9*fc_voc
   total_voc                  = total_gas_vapors+total_gas_liquid+total_gas_exhaust       \
                                +total_alc_vapors+total_alc_liquid+total_alc_exhaust      \
                                +total_die_vapors+total_die_liquid+total_die_exhaust      \
	                        +total_c2h5oh+total_hcho+total_ald
   print("emissao total em 1000tn/yr")
   print("CO: "+total_co+", CO2: "+total_co2+", NOx: "+total_nox+", SO2: "+total_so2+", PM: "+total_pm)
   print("ALD: "+total_ald+", HCHO: "+total_hcho+", C2H5OH: "+total_c2h5oh)
   print("VOC gas. vapors: "+total_gas_vapors)
   print("VOC gas. liquid: "+total_gas_liquid)
   print("VOC gas. exhaust: "+total_gas_exhaust)
   print("VOC alc. vapors: "+total_alc_vapors)
   print("VOC alc. liquid: "+total_alc_liquid)
   print("VOC alc. exhaust: "+total_alc_exhaust)
   print("VOC die. vapors: "+total_die_vapors)
   print("VOC die. liquid: "+total_die_liquid)
   print("VOC die. exhaust: "+total_die_exhaust)
   print("total VOC : "+total_voc)
  end if
 end do
;------------------------------------------------------------------------------------------------------------------------------------
 espe                         = (/e_so2,e_no,e_ald,e_hcho,e_ora2,e_nh3,e_hc3,e_hc5,e_hc8,e_eth,e_co,e_co2 \ 
                                 ,e_ol2,e_olt,e_oli,e_tol,e_xyl,e_ket,e_csl,e_iso,e_no2,e_ch3oh,e_c2h5oh  \
                                 ,e_pm25i,e_pm25j,e_so4i,e_so4j,e_no3i,e_no3j,e_orgi,e_orgj,e_eci,e_ecj   \
                                 ,e_naai,e_naaj,e_so4c,e_no3c,e_orgc,e_ecc,e_orgi_a,e_orgj_a,e_orgi_bb    \
				 ,e_orgj_bb,e_co_a,e_co_bb,e_pm_10/)				 
;------------------------------------------------------------------------------------------------------------------------------------
 XLAT                         = wrf_user_getvar(wrfinput,"XLAT",-1)
 XLONG                        = wrf_user_getvar(wrfinput,"XLONG",-1)
;------------------------------------------------------------------------------------------------------------------------------------
 Time                         = -1                  
 DateStrLen                   = 19
 Times_string                 = new((/n_tim/2/),"string")
 dSizes                       = getfiledimsizes(wrfinput)
 west_east                    = dSizes(2)
 south_north                  = dSizes(3)
 emissions_zdim               = n_lev
 emiss                        = new((/n_tim/2,n_lev,n_fil,n_col/),"float")
;------------------------------------------------------------------------------------------------------------------------------------
 do chemi = 0, 1
  if(chemi.eq.0)
   wrfchemi                   = "wrfchemi_00z_d01_proj.nc"
  else
   wrfchemi                   = "wrfchemi_12z_d01_proj.nc"
  end if
  system("/bin/rm -f "+wrfchemi)                
  f                           = addfile(wrfchemi,"c")
  setfileoption(f,"DefineMode",True)               
  fAtt                        = True
  att_wrfinput                = getvaratts(wrfinput)
  if(.not.all(ismissing(att_wrfinput)))then    
   do att = 0, dimsizes(att_wrfinput)-1             
    if(att_wrfinput(att).ne."TITLE")then           
     fAtt@$att_wrfinput(att)$ = wrfinput@$att_wrfinput(att)$
    else                            
     fAtt@$att_wrfinput(att)$ = "OUTPUT FROM MLV EMISSIONS PREPROCESSOR"
    end if                                         
   end do                                          
  end if        
;------------------------------------------------------------------------------------------------------------------------------------
  t                           = 0
  do h = chemi*n_tim/2, (chemi+1)*n_tim/2-1
  if(h.lt.10)then
   Times_string(t)            = "2011-11-10_0"+h+":00:00"
  else
   Times_string(t)            = "2011-11-10_"+h+":00:00"
  end if
  t                           = t+1
  end do 
  Times_character             = stringtocharacter(Times_string)
  Times                       = new((/n_tim/2,DateStrLen/),typeof(Times_character))
  Times(:,:)                  = Times_character(:,0:DateStrLen-1)
  delete(Times@_FillValue)                                         
;------------------------------------------------------------------------------------------------------------------------------------
  fileattdef(f,fAtt)                                     
  dimNames                    = (/"Time","DateStrLen","west_east","south_north","emissions_zdim"/)
  dimSizes                    = (/Time,DateStrLen,west_east,south_north,emissions_zdim/)
  dimUnlim                    = (/True,False,False,False,False/)
  filedimdef(f,dimNames,dimSizes,dimUnlim)    
  filevardef(f,"Times","character",(/"Time","DateStrLen"/))
;------------------------------------------------------------------------------------------------------------------------------------
  do esp = 0, n_esp-1
   t                          = 0                              
   do tim = chemi*n_tim/2, (chemi+1)*n_tim/2-1
    do i = 0, n_col-1                        
     do j = 0, n_fil-1                       
      emiss(t,0,j,i)          = espe(esp,n_fil-1-j,i,tim)
     end do                                      
    end do                                         
    t                         = t+1
   end do                                        
   emiss_wrf                  = rgrid2rcm(lat1d,lon1d,emiss,XLAT(0,:,:),XLONG(0,:,:),1)
   emiss_wrf!0                = "Time"
   emiss_wrf!1                = "emissions_zdim"
   emiss_wrf!2                = "south_north"
   emiss_wrf!3                = "west_east"
   emiss_wrf@_FillValue       = 0
   delete(emiss_wrf@_FillValue)                  
   emiss_wrf@coordinates      = "XLONG XLAT"
   emiss_wrf@stagger          = ""
   if(esp.lt.23)then                              
    emiss_wrf@units           = "mol km^-2 hr^-1"
   else                                         
    emiss_wrf@units           = "ug/m3 m/s"
   end if                                             
   emiss_wrf@description      = "EMISSIONS"
   emiss_wrf@MemoryOrder      = "XYZ"
   emiss_wrf@FieldType        = 104
;------------------------------------------------------------------------------------------------------------------------------------
   filevardef(f,nom_esp(esp),typeof(emiss_wrf),getvardims(emiss_wrf))
   f->$nom_esp(esp)$          = emiss_wrf
;------------------------------------------------------------------------------------------------------------------------------------
  end do                                      
  f->Times                    = Times
 end do
 system("/bin/mv -f wrfchemi_00z_d01_proj.nc wrfchemi_00z_d01_veic")
 system("/bin/mv -f wrfchemi_12z_d01_proj.nc wrfchemi_12z_d01_veic")
 print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
 print("!            Successful completion of mlv.ncl.           !")
 print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
end
