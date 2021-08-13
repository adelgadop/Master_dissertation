 #!/bin/bash
 
 #rename 's/_(\d\.)/_0$1/g'  *.nc
 for pol in CO NOx NH3 SO2 NMVOC; do
    for src in INDUSTRY RESIDENTIAL; do
       cdo copy *${pol}*${src}*nc edgar_HTAP_${pol}_emi_${src}_2010.0.1x0.1_year.nc
  done
  done
exit 0
