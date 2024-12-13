#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:37:30 2024

@author: shazib
"""

# -*- coding: utf-8 -*-

# import libraries

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def mm2inch(*tupl):                              # change mm to inch   ,Tuples are used to store multiple items in a single variable.
    inch = 25.4
    if isinstance(tupl[0], tuple):               # check if the first item in the tuple is a tuple
        return tuple(i/inch for i in tupl[0])    # if it is a tuple, return a tuple with the values converted to inches
    else:
        return tuple(i/inch for i in tupl)    # if it is not a tuple, return a tuple with the values converted to inches
def mm2point(mm):                          # change mm to point (lenght used in typography)
    return mm/(25.4/72)                      # 1 inch = 72 points
font = {'family' : 'Arial',                    # run command parameters
         'weight' : 'normal',
         'size'   : 8}
mpl.rc('font', **font)                      # **font is used to pass the dictionary as keyword arguments
mpl.rcParams['axes.linewidth'] = mm2point(0.2)         # set the line width of the axes
mpl.rcParams['ytick.major.width'] = mm2point(0.2)       # set the width of the major ticks on the y-axis
mpl.rcParams['xtick.major.width'] = mm2point(0.2)       # set the width of the major ticks on the x-axis
#--Plot Set-Up ----------------------------------------------------------------
def load_data(file, vars, start, end, delim, naval):     # function to load data
    res = pd.read_csv(file,parse_dates=[1],index_col=1,delimiter=delim,na_values=naval)[vars]  # read the data from the file
    res = res.loc[start : end].asfreq(freq='D')         # select the data from the start to the end date and set the frequency to daily
    return res
#End of load_data--------------------------------------------------------------
##########################-MAIN-###############################################
#Meta information for Oberstdorf weather station
station, region, altitude, latitude, longitude = 'Hohenpeißenberg','Bayern ', 977, 47.8009, 11.108   # station name, region, altitude, latitude, longitude
#get data for Oberstdorf weather station
#ftp://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/
src = 'D:\education\BTU\landsurface\github project\Walter-Lieth-climate-diagram\produkt_klima_tag_17810101_20191231_02290.txt'        # path to the data file
src_data_OB=src
vars_OB=[' RSK',' TNK',' TXK']                  # RSK  rainfall sums daily  # TNK daily minimum temperature in 2m # TXK daily maximum temperature in 2m 
delim_OB=';'                                    # delimiter
naval_OB=-999                                   # missing values
start_OB='2000-01-01'                           # start date
end_OB='2019-12-31'                             # end date
data_OB = load_data(src_data_OB, vars_OB, start_OB, end_OB, delim_OB, naval_OB)     # load the data
vars_OB_rename = {' RSK': 'Precip',' TNK':'Tmin',' TXK':'Tmax'}                     # rename variables
data_OB.rename(columns=vars_OB_rename, inplace=True)                                # rename columns
data_OB.info()                                                                      # get information about the data
#Make nenecessary calculations
data_OB_monthly = data_OB[['Tmin','Tmax']].resample('M').mean() # calculate monthly means
data_OB_monthly['Precip'] = data_OB['Precip'].resample('M').sum() # calculate monthly sum
data_OB_climatology=data_OB_monthly.groupby(data_OB_monthly.index.month).mean().round(1) #monthly grouping
data_OB_climatology['abs_Tmax']=data_OB_monthly['Tmax'].groupby(data_OB_monthly.index.month).max().round(1)   #max temperature
data_OB_climatology['abs_Tmin']=data_OB_monthly['Tmin'].groupby(data_OB_monthly.index.month).min().round(1)   #min temperature
data_OB_climatology['Tmean']=(data_OB_climatology['Tmin']+data_OB_climatology['Tmax'])/2                      #mean temperature
#calculate scalar values for Walter-lieth diagram without day counts
abs_Tmin = data_OB_climatology['abs_Tmin'].min() # h,s 
Tmin = data_OB_climatology['Tmin'].min()         # i,t
abs_Tmax = data_OB_climatology['abs_Tmax'].max() # k
Tmax = data_OB_climatology['Tmax'].max()         # j
annual_Precip = data_OB_climatology['Precip'].sum() # d
annual_Tmean = data_OB_climatology['Tmean'].mean() # c
#------------------------------------------------------------------------------
# plotting a climate diagram after Walter-lieth without day counts
# a-d, f-k, m-q from the lecture slides
for_plotDF = data_OB_climatology.copy() # not needed
# scaling Precip to Temp, ratio 2/1 for Precip <= 100 mm and 20/1 for > 100
for_plotDF.loc[(for_plotDF['Precip'] <= 100), ['Precip']] = for_plotDF['Precip']/2              # scaling Precip to Temp, ratio 2/1 for Precip <= 100 mm
for_plotDF.loc[(for_plotDF['Precip'] > 100), ['Precip']] = 50.+(for_plotDF['Precip']-100)*0.05  # scaling Precip to Temp, ratio 20/1 for > 100
# let's start plotting
fig, temp = plt.subplots(1, figsize=(mm2inch(120.0,120.0)))
precip=temp.twinx()#using two y-axis for temp (left) und for precip (right)
temp.set_ylim([-5,60])#same limits for both y axis
precip.set_ylim([-5,60])  #set y-ticks and labels
temp.set_yticks([-5,0,10,20,30,40,50]) #set y-ticks and labels
plt.setp(temp.get_yticklabels()[5:7], visible=False)   #hide last two labels
precip.set_yticks([0,10,20,30,40,50,60])           #set y-ticks and labels
precip.set_yticklabels([0,20,40,60,80,100,300])   
temp.set_ylabel('°C', labelpad=0, rotation=0.0, ha='left', va='center')   # set the label for the y-axis
temp.yaxis.set_label_coords(-0.06,0.845)
precip.set_ylabel('mm', labelpad=0, rotation=0.0, ha='right', va='center')
precip.yaxis.set_label_coords(1.08,0.92)
temp.set_xticks(for_plotDF.index)
mon = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')  #set month names
temp.set_xticklabels(mon)
#plot data
temp.plot(for_plotDF.index.values,for_plotDF['Tmean'], color='red')
precip.plot(for_plotDF.index.values,for_plotDF['Precip'], color='blue',)# drawstyle="steps-mid")
#for humid
temp.fill_between(for_plotDF.index,for_plotDF['Tmean'],for_plotDF['Precip'],where=(for_plotDF['Precip'] > for_plotDF['Tmean']),edgecolor='blue', hatch='||', facecolor='none',linewidth=0.0,)# step='mid')
#for dry
temp.fill_between(for_plotDF.index,for_plotDF['Tmean'],for_plotDF['Precip'],where=(for_plotDF['Precip'] <= for_plotDF['Tmean']),edgecolor='red', hatch='.', facecolor='none',linewidth=0.0,)# step='mid')
#for wet
precip.fill_between(for_plotDF.index,for_plotDF['Precip'],50.0,where=(for_plotDF['Precip']> 50.0),facecolor='blue')# step='mid')
##line at 50° temp / 100 mm precip
##axh = temp.axhline(50,c='black', lw=1.0)
#deleting top spine and shrinking left spine
precip.spines['top'].set_visible(False)   # delete the top spine
temp.spines['top'].set_visible(False)     # delete the top spine
temp.spines['left'].set_bounds(-5, 50)    # set the bounds for the left spine
precip.spines['left'].set_bounds(-5, 50)  # set the bounds for the left spine

precip.margins(x=0,y=0)             # set the margins to 0
temp.margins(x=0,y=0)               # set the margins to 0
#Plotting all the text
fig.text(0.01, 0.95, (station+' ('+str(altitude)+'m)'),transform=fig.transFigure, fontsize=11)
fig.text(0.01, 0.87, ('Lat:'+'{:03.2f}'.format(latitude)+' Lon:'+'{:03.2f}'.format(longitude)+'\n2000-2019'),transform=fig.transFigure, fontsize=9)
fig.text(0.51, 0.87, ('Average Temperature: '+'{:03.1f}°C'.format(annual_Tmean)+'\nAnnual Precipitation: '+'{:03.0f}mm'.format(annual_Precip)),transform=fig.transFigure, fontsize=9)
fig.text(0.105, 0.68, ('{:03.1f}'.format(abs_Tmax)+'\n'+'{:03.1f}'.format(Tmax)),transform=fig.transFigure, fontsize=9,weight='bold', ha='right')
fig.text(0.105, 0.22, ('{:03.1f}'.format(Tmin)+'\n'+'{:03.1f}'.format(abs_Tmin)),transform=fig.transFigure, fontsize=9,weight='bold', ha='right')

plt.show()