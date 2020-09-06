#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

#
# Mapa all-sky de brillo de fondo de cielo
# a partir de medidas en puntos de la boveda celeste
# usando fotometros SQM.
# version 1.2 julio 2011  jzamorano
# Falta pasar de magnitudes a flujos, interpolar y volver a magnitudes

# Version 1.3 septiembre 2011 JZ     
# Mapa con las coordenadas estilo geografico 
# y no astronomico como si el cielo se proyectara en el suelo para poder compa
# mas facilmente con las fuentes de contaminacion luminica.

import matplotlib
from pylab import *
import numpy as np
from matplotlib.pyplot import show
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

import matplotlib.mlab as ml

from math import pi  
from matplotlib.pyplot import figure, show, rc, grid, savefig

matplotlib.rcParams['text.latex.unicode']=True
matplotlib.rcParams['text.usetex']=False

# David Rodríguez-Estecha Álvarez
# FECHA:	2014/07/26
# Fotometro SQM-LU
# HORA INICIO (UT):   1:20:53  
# HORA FINAL (UT):    2:30:13	
# T (C): 19
# LOCALIZACION:	Parque Nacional de Monfragüe.
# PARAJE:	Aparcamiento cercano a la pequeña población de Villareal de San Carlos.
#               Pedanía perteneciente al municipio de Serradilla y ubicada en el interior del parque.
# LATITUD:	N 39 50 57.74				
# LONGITUD:W 06 01 59.63				
# Altitud: 326 m

# Información general del lugar de observación:
# Lugares de interés:
# Punto de observación situado en las coordenadas indicadas en la tabla adjunta.
# Se trata de una explanada dedicada al aparcamiento de vehículos. 
											
#Acceso:
# Una vez se llega a Villareal de San Carlos por la nacional EX-208,el lugar de observación se encuentra a unos excasos 500 m. 


#MEDIDA EN EL CENIT:			21.30
#	S			W			N			E		
#90  21.30
#75 21.29 21.25 21.27 21.08 21.01 21.20 21.19 21.22 21.23 21.13 21.28 21.27 21.27 21.29 21.41 21.42 21.43 21.13 21.39 21.18
#60 21.21 21.15 21.16 21.14 21.13 20.98 21.21 21.20 21.21 21.14 21.28 21.26 21.26 21.09 21.39 21.39 21.40 21.32 21.35 21.26
#45 21.03 21.08 21.08 21.04 21.06 21.12 21.08 21.13 21.10 21.08 21.21 21.17 21.18 20.93 21.14 21.27 21.25 21.24 21.19 21.18
#30 21.00 20.94 20.86 20.96 20.61 20.99 20.88 20.88 20.91 20.89 20.99 21.05 21.04 20.96 21.03 20.90 21.04 21.07 20.91 21.06
# Datos enviados en enero de 2016:
#15 21.16,20.98,20.43,21.00,21.12,20.84,20.91,20.90,20.63,20.68,20.93,21.10,21.13,20.95,20.93,20.82,20.92,21.02,21.17,21.19

										    
#        S -> W -> N -> E -> S
m15=[21.16,20.98,20.43,21.00,21.12,20.84,20.91,20.90,20.63,20.68,20.93,21.10,21.13,20.95,20.93,20.82,20.92,21.02,21.17,21.19]
m30= [21.00,20.94,20.86,20.96,20.61,20.99,20.88,20.88,20.91,20.89,20.99,21.05,21.04,20.96,21.03,20.90,21.04,21.07,20.91,21.06] 
m45= [21.03,21.08,21.08,21.04,21.06,21.12,21.08,21.13,21.10,21.08,21.21,21.17,21.18,20.93,21.14,21.27,21.25,21.24,21.19,21.18]
m60= [21.21,21.15,21.16,21.14,21.13,20.98,21.21,21.20,21.21,21.14,21.28,21.26,21.26,21.09,21.39,21.39,21.40,21.32,21.35,21.26]
m75= [21.29,21.25,21.27,21.08,21.01,21.20,21.19,21.22,21.23,21.13,21.28,21.27,21.27,21.29,21.41,21.42,21.43,21.13,21.39,21.18]
m75= [21.29,21.25,21.27,21.08,21.01,21.20,21.19,21.22,21.23,21.13,21.28,21.27,21.27,21.29,21.41,21.42,21.43,21.33,21.39,21.18] #modificado
m90= [21.30]


x15 = [0, 18, 36, 54, 72, 90,108,126,144,162,180,198,216,234,252,270,288,306,324,342]
x30 = [0, 18, 36, 54, 72, 90,108,126,144,162,180,198,216,234,252,270,288,306,324,342]
x45 = [0, 18, 36, 54, 72, 90,108,126,144,162,180,198,216,234,252,270,288,306,324,342]
x60 = [0, 18, 36, 54, 72, 90,108,126,144,162,180,198,216,234,252,270,288,306,324,342]
x75 = [0, 18, 36, 54, 72, 90,108,126,144,162,180,198,216,234,252,270,288,306,324,342]
x90 = [180]

xx =  np.linspace(-18,360,22)       # Para interpolar primero en acimuts
print xx                             # en este caso no se interpola porque el muestreo es suficiente

x15 = [-18]    + x15 + [360]         
m15 = [m15[19]]+ m15 + [m15[0]]  
interpolater=interp1d(x15,m15,kind='linear')
mm15=interpolater(xx)

x30 = [-18]    + x30 + [360]         
m30 = [m30[19]]+ m30 + [m30[0]]  
interpolater=interp1d(x30,m30,kind='linear')
mm30=interpolater(xx)

x45 = [-18]    + x45 + [360]           
m45 = [m45[11]]+ m45 + [m45[0]]   
interpolater=interp1d(x45,m45,kind='linear')
mm45=interpolater(xx)

x60 = [-18]    + x60 + [360]           
m60 = [m60[11]]+ m60 + [m60[0]]   
interpolater=interp1d(x60,m60,kind='linear')
mm60=interpolater(xx)

x75 = [-18]    + x75 + [360]           
m75 = [m75[11]]+ m75 + [m75[0]]   
interpolater=interp1d(x75,m75,kind='linear')
mm75=interpolater(xx)

x90 = [-18,0, 18, 36, 54, 72, 90,108,126,144,162,180,198,216,234,252,270,288,306,324,342,360]
m90=[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]
interpolater=interp1d(x90,m90,kind='linear')
mm90=interpolater(xx)

# Grafica al estilo horizontal
plt.plot(x15,m15,'bo')
plt.plot(xx,mm15,'k')
plt.plot(x30,m30,'bo')
plt.plot(xx,mm30,'k')
plt.plot(x45,m45,'bo')
plt.plot(xx,mm45,'k')
plt.plot(x60,m60,'bo')
plt.plot(xx,mm60,'k')
plt.plot(x75,m75,'bo')
plt.plot(xx,mm75,'k')
plt.plot(x90,m90,'bo')
plt.plot(xx,mm90,'k')

#plt.show()

y = [90., 75., 60., 45., 30., 15.]  
m=[mm90, mm75, mm60, mm45, mm30, mm15]

# Grafica horizontal en contornos
CS=contourf(xx,y,m,cmap=plt.cm.gist_yarg)
CS2=contour(CS,levels=CS.levels[::1], colors='w',origin='upper',hold='on')
cbar=colorbar(CS)
cbar.ax.set_ylabel('mag/arcsec2')
cbar.add_lines(CS2)

#show()

xn = np.linspace(0,360,25) 
yn=  np.linspace(15,90,12)
Xn,Yn = np.meshgrid(xn,yn)

#print Yn

todom = m15 + m30 + m45 + m60 + m75 + m90
todox = x15 + x30 + x45 + x60 + x75 + x90
todoy = [15] * 22 + [30] * 22 + [45] * 22 + [60] * 22 + [75] * 22 + [90] * 22


assert len(todom) == len(todox) == len(todoy)

mm = ml.griddata(todox, todoy, todom,Xn,Yn,interp='linear')

# Polar figure

rc('grid', color='#316931', linewidth=1, linestyle='-')
rc('xtick', labelsize=15)
rc('ytick', labelsize=15)

# force square figure and square axes looks better for polar, IMO
width, height = matplotlib.rcParams['figure.figsize']
size = min(width, height)
size = 6

# make a square figure
fig = figure(figsize=(size, size))
#ax = fig.add_axes([0.1, 0.1, 0.8, 0.7], polar=True, axisbg='#d5de9c')
ax = fig.add_axes([0.03, 0.15, 0.95, 0.72], polar=True, axisbg='#d5de9c')

#r = np.arange(0, 4.0, 0.01)
#theta = 2*np.pi*r
##ax.set_rmax(0.5)
grid(True)

ring_angles = [ (x+0.000001) * (np.pi/180.) for x in range(0,100,15)]
ring_labels = [ str(x) for x in range(0,100,15)]
ring_labels.reverse()
lines,labels = rgrids(ring_angles,ring_labels)

angles,labels = thetagrids( range(360,0,-45), ( 'E', 'SE', 'S', 'SW', 'W','NW', 'N', 'NE') )
#ax.text(1.6,1.5, "Monfrague", fontsize=18, horizontalalignment='center')

label = u"Monfragüe"
ax.text(1.6,1.6, label, fontsize=18, horizontalalignment='center')
ax.text(5.36,1.8, "2014-07-26", fontsize=14, horizontalalignment='center')
ax.text(4.1,1.8, "mag/arcsec$^2$", fontsize=14, horizontalalignment='center')

Xn = (np.pi * (Xn) / 180.)  
Xn = (2* np.pi) - Xn - (np.pi /2.) 
Yn = (90.-Yn) *np.pi/180.

# LATITUD:	N 39 50 57.74				
# LONGITUD:W 06 01 59.63
LAT= "39 50 57.7 N"
LONG="06 01 59.6 W"                                                   
ax.text(1.05,1.55,LAT, fontsize=14, horizontalalignment='left')
ax.text(1.00,1.43,LONG, fontsize=14, horizontalalignment='left')



## niveles = arange(19.4,21.6,0.2)
niveles = arange(19.4,21.8,0.1)
niveles = arange(18.2,21.8,0.1)
##niveles = arange(18.4,21.1,0.1)
CS = contourf(Xn,Yn,mm,20,cmap=get_cmap('YlGnBu'),levels=niveles) 

print "Minimum=", np.min(mm)
print "Maximum=", np.max(mm)

CS2=contour(CS,levels=[19.0,20.0,20.7,20.9,21.1,21.2,21.3,21.4,21.5], colors='w',origin='upper',hold='on')
plt.clabel(CS2,fmt = '%2.1f',fontsize=15)

cbaxes = fig.add_axes([0.1, 0.05,0.80,0.04]) 
cbar=colorbar(CS,orientation='horizontal',cax=cbaxes)
#cbar.ax.set_ylabel('mag/arcsec2')
#cbar.add_lines(CS2)

savefig("dummy.png")
show()
