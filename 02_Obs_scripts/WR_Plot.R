# Import libraries
library(openair)
library(colorspace)
library(reshape2)
library(tidyverse)

# Import data
data <- read.csv("../01_data/processed/iag_met.csv")
data2 <- read.csv("../01_data/processed/mod/mod_all_scen.csv")
# Time format
# 2018-09-01 00:00:00-03:00
data$date <- as.POSIXct(strptime(data$local_date, format = "%Y-%m-%d %H:%M", tz = "America/Sao_Paulo"))
data2$date <- as.POSIXct(strptime(data2$local_date, format = "%Y-%m-%d %H:%M", tz = "America/Sao_Paulo"))

# ------ #
# Charts #
# ------ #

# Wind Rose Plot Obs and Current

obs <- data.frame('date'=data$date,'ws'=data$ws_obs,'wd'=data$wd_obs)
obs$result <- 'Obs.'
mod <- data.frame('date'=data$date,'ws'=data$ws_mod,'wd'=data$wd_mod)
mod$ws[mod$ws< 0.5] <- 0
mod$result <- 'Mod.'

wind <- rbind2(obs,mod)

cols2 = rainbow_hcl(4)

pdf('../dissertation/fig/WRplot_IAG_sep_oct2018.pdf',width=6,height=4,bg='white')
windRose(wind, ws='ws', wd='wd', type='result',
                angle = 22.5, paddle = F, width=0.5, annotate = T,
                cols=rev(cols2), key = T, border=T, breaks = 6)
dev.off()

# Wind Rose Plot from WRF-Chem model: Current vs RCP

cols2 = rainbow_hcl(4)
stations <- c("Campinas-Taquaral","Carapicuíba","Ibirapuera","Paulínia","Pico do Jaraguá")
wind_dir <- subset(data2,station %in% stations)
windRose(wind_dir,ws="ws",wd='wd', type="type", auto.text=F,angle = 22.5, paddle = F, width=0.5, annotate = F,
         cols=rev(cols2), key = T, border=T, breaks = 5,grid.line = 10, max.freq = 40)

windRose(wind_dir,ws="ws_rcp45",wd='wd_rcp45', type="type", auto.text=F,angle = 22.5, paddle = F, width=0.5, annotate = F,
         cols=rev(cols2), key = T, border=T, breaks = 5,grid.line = 10, max.freq = 40)

windRose(wind_dir,ws="ws_rcp85",wd='wd_rcp85', type="type", auto.text=F,angle = 22.5, paddle = F, width=0.5, annotate = F,
         cols=rev(cols2), key = T, border=T, breaks = 5,grid.line = 10, max.freq = 40)

# Wind Rose Plot Obs and Current

obs2 <- data.frame('date'=data2$date,'ws'=data2$ws,'wd'=data2$wd)
obs2$ws[obs2$ws< 0.5] <- 0
obs2$Scenario <- 'Current'
rcp4.5 <- data.frame('date'=data2$date,'ws'=data2$ws_rcp45,'wd'=data2$wd_rcp45)
rcp4.5$ws[rcp4.5$ws< 0.5] <- 0
rcp4.5$Scenario <- 'RCP 4.5'

rcp8.5 <- data.frame('date'=data2$date,'ws'=data2$ws_rcp85,'wd'=data2$wd_rcp85)
rcp8.5$ws[rcp8.5$ws< 0.5] <- 0
rcp8.5$Scenario <- 'RCP 8.5'

wind2 <- rbind2(obs2,rcp4.5)
wind2 <- rbind2(wind2,rcp8.5)

windRose(wind2, ws='ws', wd='wd', type='Scenario',
         angle = 22.5, paddle = F, width=0.5, annotate = T,
         cols=rev(cols2), key = T, border=T, breaks = 6)
