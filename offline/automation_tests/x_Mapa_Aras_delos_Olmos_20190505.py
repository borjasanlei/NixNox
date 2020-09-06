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


mpl.rcParams['text.latex.unicode']=True
mpl.rcParams['text.usetex']=False

from math import pi  
from matplotlib.pyplot import figure, show, rc, grid, savefig
mpl.rcParams['text.latex.unicode']=True
mpl.rcParams['text.usetex']=False

# Observadores: Pablo Rosillo Rodes, Ana Belén González Rodríguez, Raquel # Escrich Rincón y Daniel Pérez del Rey
# FECHA	5 de mayo de 2019	
# Fotómetro: Departament d'Astronomia i Astrofísica - UV
# LUGAR:	Aras de los Olmos	
# Localización:   Centro Astronómico del Alto Túria 
# Paraje:   
# 39°57'04.3" N     39.951194, -1.110694
# 01°06'38.5" W
# Altitud 1100 m  
# UTC inicio 01h00m   
# UTC final  01h15m 
# T = 4ºC  
# Comentarios 
# No medí la humedad relativa del aire. Parque eólico próximo que se nota 
# en azimut alrededor de 210-240 NE. Mucho viento con aire frío.
# 
#	
#        Sur       Oeste      Norte        Este
#ACIMUT-> 0 30  60  90 120 150 180 210 240 270 300 330
m20 = [21.09,21.17,21.14,21.26,21.24,21.30,21.23,20.81,20.40,20.81,20.88,21.01] 
m40 = [21.36,21.37,21.49,21.43,21.50,21.46,21.46,21.08,20.97,21.04,21.21,21.38] 
m60 = [21.55,21.58,21.61,21.65,21.63,21.65,21.64,21.49,21.35,21.36,21.68,21.57] 
m80 = [21.65,21.67,21.68,21.68,21.68,21.66,21.65,21.64,21.60,21.65,21.69,21.65] 
m90 = [21.67]

x20 = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
x40 = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
x60 = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
x80 = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
x90 = [180]

xx =  np.linspace(-30,360,27)       # Para interpolar primero en acimuts

x20 = [-30]    + x20 + [360]         
m20 = [m20[11]]+ m20 + [m20[0]]  
interpolater=interp1d(x20,m20,kind='linear')
mm20=interpolater(xx)

x40 = [-30]    + x40 + [360]           
m40 = [m40[11]]+ m40 + [m40[0]]   
interpolater=interp1d(x40,m40,kind='linear')
mm40=interpolater(xx)

x60 = [-30]    + x60 + [360]           
m60 = [m60[11]]+ m60 + [m60[0]]   
interpolater=interp1d(x60,m60,kind='linear')
mm60=interpolater(xx)

x80 = [-30]    + x80 + [360]           
m80 = [m80[11]]+ m80 + [m80[0]]   
interpolater=interp1d(x60,m60,kind='linear')
mm80=interpolater(xx)

x90=[-30,0,30,60,90,120,150,180,210,240,270,300,330,360]
m90=[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]+[m90[0]]

interpolater=interp1d(x90,m90,kind='linear')
mm90=interpolater(xx)

# Grafica al estilo horizontal
plt.plot(x20,m20,'bo')
plt.plot(xx,mm20,'k')
plt.plot(x40,m40,'bo')
plt.plot(xx,mm40,'k')
plt.plot(x60,m60,'bo')
plt.plot(xx,mm60,'k')
plt.plot(x80,m80,'bo')
plt.plot(xx,mm80,'k')
plt.plot(x90,m90,'bo')
plt.plot(xx,mm90,'k')

#plt.show()

y = [90., 80., 60., 40., 20.]  
m=[mm90, mm80, mm60, mm40, mm20]

# Grafica horizontal en contornos
CS=contourf(xx,y,m,cmap=plt.cm.gist_yarg)
CS2=contour(CS,levels=CS.levels[::1], colors='w',origin='upper',hold='on')
cbar=colorbar(CS)
cbar.ax.set_ylabel('mag/arcsec2')
cbar.add_lines(CS2)

#show()

xn = np.linspace(0,360,25) 
yn=  np.linspace(20,90,12)
Xn,Yn = np.meshgrid(xn,yn)

#print Yn

todom = m20 + m40 + m60 + m80 + m90
todox = x20 + x40 + x60 + x80 + x90
todoy = [20] * 14 + [40] * 14 + [60] * 14 + [80] * 14 + [90] * 14


assert len(todom) == len(todox) == len(todoy)

mm = ml.griddata(todox, todoy, todom,Xn,Yn,interp="linear")

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
ax = fig.add_axes([0.03, 0.15, 0.95, 0.72], polar=True) #, axisbg='#d5de9c')

#r = np.arange(0, 4.0, 0.01)
#theta = 2*np.pi*r
##ax.set_rmax(0.5)
grid(True)

ring_angles = [ (x+0.000001) * (np.pi/180.) for x in range(0,100,15)]
ring_labels = [ str(x) for x in range(0,100,15)]
ring_labels.reverse()
lines,labels = rgrids(ring_angles,ring_labels)

angles,labels = thetagrids( range(360,0,-45), ( 'E', 'SE', 'S', 'SW', 'W','NW', 'N', 'NE') )
# ax.set_title(" ", fontsize=14)


label = u"Aras de los Olmos (CAAT)"
ax.text(1.6,1.5, label, fontsize=18, horizontalalignment='center')
ax.text(5.36,1.7, "2019-05-05", fontsize=14, horizontalalignment='center')
ax.text(4.1,1.7, "mag/arcsec$^2$", fontsize=14, horizontalalignment='center')

# 39°57'04.3" N 
# 01°06'38.5" W
LAT= "39 57 04.3 N"
LONG="01 06 38.5 W"                                                   
ax.text(1.05,1.55,LAT, fontsize=14, horizontalalignment='left')
ax.text(1.00,1.43,LONG, fontsize=14, horizontalalignment='left')


Xn = (np.pi * (Xn) / 180.)  
Xn = (2* np.pi) - Xn - (np.pi /2.) 
Yn = (90.-Yn) *np.pi/180.


#niveles = arange(19.4,21.6,0.2)
#niveles = arange(19.4,21.8,0.1)
niveles = arange(18.2,21.8,0.1)
#niveles = arange(16.0,19.,0.1)
#niveles = arange(15.0,20.,0.1)

CS = contourf(Xn,Yn,mm,20,cmap=get_cmap('YlGnBu'),levels=niveles) 

print "Minimum=", np.min(mm)
print "Maximum=", np.max(mm)

#CS2=contour(CS,levels=[19.0,20.6,20.8,21.0,21.2,21.3], colors='w',origin='upper',hold='on')
CS2=contour(CS,levels=[20.2,20.4,20.6,20.8,21.0,21.2,21.4,21.6,21.7], colors='w',origin='upper',hold='on')
plt.clabel(CS2,fmt = '%2.1f',fontsize=15)

cbaxes = fig.add_axes([0.1, 0.05,0.80,0.04]) 
cbar=colorbar(CS,orientation='horizontal',cax=cbaxes)
savefig("NixNox_Aras_delos_Olmos_20190505.png",transparent='true')
savefig("NixNox_Aras_delos_Olmos_20190505_w.png",transparent='false')

#savefig("dummy.png")
#show()

