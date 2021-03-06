#-*- coding: iso-8859-1 -*-

# ==================================================
#	import modules
# ==================================================

import sys

# append paths
sys.path.append("/home/kahl/Dokumente/fp/fp/python/")

import evaluation as ev
import evaluation.simpleplot as sp
import latextable as lt

# calc with uncertainties and arrays of uncertainties [[val, std], ...]
import uncertainties as uc
import uncertainties.unumpy as unp

# calc with arrays
import numpy as np

# plot engine
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# for fitting curves
from scipy import optimize

# constants
import scipy.constants as const

# ==================================================
#	settings
# ==================================================


sp.params["text.latex.preamble"] = sp.tex_mathpazo_preamble
plt.rcParams.update(sp.params)



def print_tex(s):
    assert isinstance(s, str)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.text(0.0, 0.5,
            s.replace('\t',' ').replace('\n',' ').replace('%',''),
            color='k', size = 'x-large'
    )
    plt.show()

#=================================================
#  Daten einlesen , T=Temperatur/°C , J=Depolarisationsstrom/A , Jh=Heizstrom
#=================================================


T1,J1,Jh1 = ev.get_data("../messwerte/messwerte1.txt", unpack=True, index=0)
T2,J2,Jh2 = ev.get_data("../messwerte/messwerte2.txt", unpack=True, index=0)

T1=T1+273.15
T2=T2+273.15

#Tabellen
t1 = lt.latextable(
    [T1, J1*1e12],
    "../tex/tabellen/tab10.tex",
    alignment = 'CC',
    form= ['.1f','.2f'],
    split = 3
)

t2 = lt.latextable(
    [T2, J2*1e12],
    "../tex/tabellen/tab20.tex",
    alignment = 'CC',
    form= ['.1f','.2f'],
    split = 3
)


#Heizrate
Z1=[]
Z2=[]

for i in range (0,len(T1)):
	Z1.append(i+1)
for i in range (0,len(T2)):
	Z2.append(i+1)
der1=[]
der2=[]
for i in range (1,len(Z1)-1):
	der1.append( (T1[i+1]-T1[i-1])/2. )
for i in range (1,len(Z2)-1):
	der2.append( (T2[i+1]-T2[i-1])/2. )
figHeiz = plt.figure()
axHeiz = figHeiz.add_subplot(111)

axHeiz.plot(Z1[1:len(T1)-1],der1 , label = "Heizrate 1 in K/min")
axHeiz.plot(Z2[1:len(T2)-1],der2 , label = "Heizrate 2 in K/min")

axHeiz.set_xlabel(r'Zeit/min')
axHeiz.set_ylabel(r'Heizrate/(K/min)')

axHeiz.legend(loc = 'best')
axHeiz = ev.plot_layout(axHeiz)

figHeiz.tight_layout()
figHeiz.savefig('Heizrate.pdf')

der1_uc = ev.get_uncert(der1)
der2_uc = ev.get_uncert(der2)
print der1_uc
print der2_uc


#Exponentialfunktion
def exp(x,A,B,y0):
	return A*np.exp(B*x)+y0

# Geradenfunktion
def G(x, m, b):
    return m*x + b


#plot
#x1 = np.linspace(9, 12.4, 1000)
#x2 = np.linspace(7.5, 12, 1000)
#x3 = np.linspace(7.5, 11.3, 1000)

fig0 = plt.figure()
ax0 = fig0.add_subplot(111)

ax0.plot(T1,J1 , label = r'$b=2$ K/min',marker ='x', linestyle='none')
ax0.plot(T2,J2,label=r'$b=2.5$ K/min', marker='x',linestyle='none')

ax0.set_xlabel(r'Temperatur/K')
ax0.set_ylabel(r'Depolarisationsstrom/A')

ax0.legend(loc = 'best')
ax0 = ev.plot_layout(ax0)

fig0.tight_layout()
fig0.savefig('Temp_Strom_Verlauf0.pdf')

J1=J1[(T1>280)&(T1<310)]
J2=J2[(T2>280)&(T2<320)]
T1=T1[(T1>280)&(T1<310)]
T2=T2[(T2>280)&(T2<320)]

#
Te2=T2[(T2<281)|(T2>315)]
Je2=J2[(T2<281)|(T2>315)]
vale2,cove2=optimize.curve_fit(G,Te2,np.log(Je2))

Te1=T1[(T1<285)|(T1>305)]
Je1=J1[(T1<285)|(T1>305)]
vale1,cove1=optimize.curve_fit(G,Te1,np.log(Je1))


#Korrigiere Messwerte um den Untergrund
MIN1=0
MIN2=0
for i in range (0,len(T1)):
	if (J1[i]-np.exp(vale1[0]*(T1[i])+vale1[1])<MIN1):
		MIN1=J1[i]-np.exp(vale1[0]*(T1[i])+vale1[1])

for i in range (0,len(T2)):
	if (J2[i]-np.exp(vale2[0]*(T2[i])+vale2[1])<MIN2):
		MIN2=J2[i]-np.exp(vale2[0]*(T2[i])+vale2[1])
MIN1+=-1e-20
MIN2+=-1e-20



#

#--PLOT-----------------------------------
fig1a = plt.figure()
ax1a = fig1a.add_subplot(111)

ax1a.plot(T1,J1 , label = r'$b=2$ K/min', marker='x')
ax1a.plot(T1,np.exp(vale1[0]*(T1)+vale1[1])+MIN1,label="Untergrund")

ax1a.set_xlabel(r'Temperatur/K')
ax1a.set_ylabel(r'Depolarisationsstrom/A')

ax1a.legend(loc = 'best')
ax1a = ev.plot_layout(ax1a)

fig1a.tight_layout()
fig1a.savefig('Temp_Strom_Verlaufa.pdf')

fig1b = plt.figure()
ax1b = fig1b.add_subplot(111)

ax1b.plot(T2,J2 , label = r'$b=2.5$ K/min', marker='x')
ax1b.plot(T2,np.exp(vale2[0]*(T2)+vale2[1])+MIN2,label="Untergrund")

ax1b.set_xlabel(r'Temperatur/K')
ax1b.set_ylabel(r'Depolarisationsstrom/A')

ax1b.legend(loc = 'best')
ax1b = ev.plot_layout(ax1b)

fig1b.tight_layout()
fig1b.savefig('Temp_Strom_Verlaufb.pdf')


#Korrigieren
for i in range (0,len(T1)):
	J1[i]=J1[i]-np.exp(vale1[0]*(T1[i])+vale1[1])-MIN1

for i in range (0,len(T2)):
	J2[i]=J2[i]-np.exp(vale2[0]*(T2[i])+vale2[1])-MIN2


fig1c = plt.figure()
ax1c = fig1c.add_subplot(111)

ax1c.plot(T1,J1 , label = r'$b=2$ K/min')
ax1c.plot(T2,J2 , label = r'$b=2.5$ K/min')

ax1c.set_xlabel(r'Temperatur/K')
ax1c.set_ylabel(r'Depolarisationsstrom/A')

ax1c.legend(loc = 'best')
ax1c = ev.plot_layout(ax1c)

fig1c.tight_layout()
fig1c.savefig('Temp_Strom_Verlaufc.pdf')

#----------------------------------------

#Es soll ln(J) linear zu 1/T sein

# linerare Ausgleichrechnung

a1=2
b1=6

a2=1
b2=6

val1, cov1 = optimize.curve_fit(G, 1./T1[a1:b1], np.log(J1[a1:b1]))
std1 = ev.get_std(cov1)

val2, cov2 = optimize.curve_fit(G, 1./T2[a2:b2], np.log(J2[a2:b2]))
std2 = ev.get_std(cov2)



#
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)

ax2.plot(1./T1[a1:b1], np.log(J1[a1:b1]), linestyle = 'none', marker = '+', label = 'Messwerte')
ax2.plot(1./np.insert(T1[b1:],0,T1[:a1]), np.log(np.insert(J1[b1:],0,J1[:a1])), linestyle = 'none', marker = 'd', label = 'Messwerte (nicht in der Regression)')
ax2.plot(1./T1[0:10], G(1./T1[0:10], val1[0], val1[1]), label="Fit")

ax2.set_xlabel(r'$1/T$')
ax2.set_ylabel(r'$\ln(\{J \})$')

ax2.legend(loc = 'best')
ax2 = ev.plot_layout(ax2)

fig2.tight_layout()
fig2.savefig('G1.pdf')

#
fig3 = plt.figure()
ax3 = fig3.add_subplot(111)

ax3.plot(1./T2[a2:b2], np.log(J2[a2:b2]), linestyle = 'none', marker = '+', label = 'Messwerte')
ax3.plot(1./np.insert(T2[b2:],0,T2[:a2]), np.log(np.insert(J2[b2:],0,J2[:a2])), linestyle = 'none', marker = 'd', label = 'Messwerte (nicht in der Regression)')
ax3.plot(1./T2[0:10], G(1./T2[0:10], val2[0], val2[1]), label="Fit")

ax3.set_xlabel(r'$1/T$')
ax3.set_ylabel(r'$\ln(\{J \})$')

ax3.legend(loc = 'best')
ax3 = ev.plot_layout(ax3)

fig3.tight_layout()
fig3.savefig('G2.pdf')

# Damit m=W/k
W1=-val1[0]*const.k
W2=-val2[0]*const.k
DW1=std1[0]*const.k
DW2=std2[0]*const.k
print "Erster Wert W1+-DW1 = " + str(W1) + "+/-" + str(DW1)
print "Zweiter Wert W2-DW2 = " + str(W2) + "+/-" + str(DW2)


# über den gesamten Verlauf:
#da jeder Stromwert für 2K bzw 2.5K steht, kann das Integral als
# 2*\sum_{n=n_0}^{n_max} J[n] geschrieben werden
def integral1(n0):
	i=0.
	for n in range(n0,len(J1)):
		i=i+2.*J1[n]
	i=i/J1[n0]
	return i
def integral2(n0):
	i=0.
	for n in range(n0,len(J2)):
		i=i+2.5*J2[n]
	i=i/J2[n0]
	return i

I1=[]
I2=[]
for n0 in range (0,len(J1)):
	I1.append(integral1(n0))
for n0 in range (0,len(J2)):
	I2.append(integral2(n0))
#Trage 1/T gegen ln(i) auf , d.h. 1/T[m]:np.log(integral(m)) für m in range (0,len(T))

#Ausgleichsrechnung durch die ersten 20 Messwerte:
A1=2
B1=15
A2=2
B2=15

valS1, covS1 = optimize.curve_fit(G, 1./T1[A1:B1], np.log(I1[A1:B1]))
stdS1 = ev.get_std(covS1)

valS2, covS2 = optimize.curve_fit(G, 1./T2[A2:B2], np.log(I2[A2:B2]))
stdS2 = ev.get_std(covS2)

#
fig4 = plt.figure()
ax4 = fig4.add_subplot(111)

Tx=np.insert(T1[B1:],0,T1[:A1])
Ix=np.insert(I1[B1:],0,I1[:A1])
ax4.plot(1./Tx, np.log(Ix), linestyle = 'none', marker = 'd', label = 'Messwerte (nicht in der Regression)')
ax4.plot(1./T1[A1:B1], np.log(I1[A1:B1]), linestyle = 'none', marker = '+', label = 'Messwerte')
ax4.plot(1./T1, G(1./T1, valS1[0], valS1[1]), label="Fit")

ax4.set_xlabel(r'$1/T$')
ax4.set_ylabel(r'$\ln(S1(T))$')

ax4.legend(loc = 'best')
ax4 = ev.plot_layout(ax4)

fig4.tight_layout()
fig4.savefig('S1.pdf')

#
fig5 = plt.figure()
ax5 = fig5.add_subplot(111)

Txx=np.insert(T2[B2:],0,T2[:A2])
Ixx=np.insert(I2[B2:],0,I2[:A2])
ax5.plot(1./Txx, np.log(Ixx), linestyle = 'none', marker = 'd', label = 'Messwerte (nicht in der Regression)')
ax5.plot(1./T2[A2:B2], np.log(I2[A2:B2]), linestyle = 'none', marker = '+', label = 'Messwerte')
ax5.plot(1./T2, G(1./T2, valS2[0], valS2[1]), label="Fit")

ax5.set_xlabel(r'$1/T$')
ax5.set_ylabel(r'$\ln(S2(T))$')

ax5.legend(loc = 'best')
ax5 = ev.plot_layout(ax5)

fig5.tight_layout()
fig5.savefig('S2.pdf')

# Damit m=W/k
WS1=valS1[0]*const.k
WS2=valS2[0]*const.k
DWS1=stdS1[0]*const.k
DWS2=stdS2[0]*const.k
print "Erster Wert WS1+-DWS1 = " + str(WS1) + "+/-" + str(DWS1)
print "Zweiter Wert WS2-DWS2 = " + str(WS2) + "+/-" + str(DWS2)

#Noch tau bestimmen (mit WS1,2 weil angeblich genauer)
Tmax1=T1[J1>=max(J1)]
Tmax2=T2[J2>=max(J2)]
taumax1=const.k*Tmax1*Tmax1/(WS1*2.)
taumax2=const.k*Tmax2*Tmax2/(WS2*2.5)
Dtaumax1=taumax1* DWS1/WS1
Dtaumax2=taumax2* DWS2/WS2
print "Relaxationszeit am Maximum tau(Tm) = " + str(taumax1) + "+/-" + str(Dtaumax1)
print "Relaxationszeit am Maximum tau(Tm) = " + str(taumax2) + "+/-" + str(Dtaumax2)
#und tau0
tau01=taumax1*np.exp(-WS1/(const.k*Tmax1))
tau02=taumax2*np.exp(-WS2/(const.k*Tmax2))
Dtau01=np.sqrt( (np.exp(-WS1/(const.k*Tmax1))*Dtaumax1)**2 + (taumax1*np.exp(-WS1/(const.k*Tmax1))*DWS1/(const.k*Tmax1) )**2 )
Dtau02=np.sqrt( (np.exp(-WS2/(const.k*Tmax2))*Dtaumax2)**2 + (taumax2*np.exp(-WS2/(const.k*Tmax2))*DWS2/(const.k*Tmax2) )**2 )
print "tau0 = " + str(tau01) + "+/-" + str(Dtau01)
print "tau0 = " + str(tau02) + "+/-" + str(Dtau02)





print "Gerade 1 ="+str(val1[0])+" +- "+str(std1[0])+" x + "+str(val1[1])+" +- "+str(std1[1])
print "Gerade 2 ="+str(val2[0])+" +- "+str(std2[0])+" x + "+str(val2[1])+" +- "+str(std2[1])
print "Gerade S1="+str(valS1[0])+" +- "+str(stdS1[0])+" x + "+str(valS1[1])+" +- "+str(stdS1[1])
print "Gerade S2="+str(valS2[0])+" +- "+str(stdS2[0])+" x + "+str(valS2[1])+" +- "+str(stdS2[1])
#Texzeug===============================================
# latex-Gleichung der linearen Regression
#G1 = ev.equation_linReg(
#        val1,
#        std1,
#        unit=["", ""],
#        funcname="G_{1}(x)"
#)
#ev.write('/home/dominik/Dokumente/fp/fp/versuche/dipolrelaxation/tex/gleichungen/G1' ,G1 )

#G2= ev.equation_linReg(
#        val2,
#        std2,
#        unit=["", ""],
#        funcname="G_{2}(x)"
#)
#ev.write('/home/dominik/Dokumente/fp/fp/versuche/dipolrelaxation/tex/gleichungen/G2' ,G2 )

#GS1 = ev.equation_linReg(
#        valS1,
#        stdS1,
#        unit=["", ""],
#        funcname="GS_{1}(x)"
#)
#ev.write('/home/dominik/Dokumente/fp/fp/versuche/dipolrelaxation/tex/gleichungen/GS1' ,GS1 #)

#GS2= ev.equation_linReg(
#        valS2,
#        stdS2,
#        unit=["", ""],
#        funcname="GS_{2}(x)"
#)
#ev.write('/home/dominik/Dokumente/fp/fp/versuche/dipolrelaxation/tex/gleichungen/GS2' ,GS2 )


# LateX-Tabelle erzeugen
t1 = lt.latextable(
    [T1, J1*1e12],
    "../tex/tabellen/tab1.tex",
    alignment = 'CC',
    form= ['.1f','.2f'],
    split = 3
)

t2 = lt.latextable(
    [T2, J2*1e12],
    "../tex/tabellen/tab2.tex",
    alignment = 'CC',
    form= ['.1f','.2f'],
    split = 3
)

t3 = lt.latextable(
    [T1, I1],
    "../tex/tabellen/tab3.tex",
    alignment = 'CC',
    form= ['.1f','.2f'],
    split = 3
)
ev.write('Integrale1' ,t3 )

t4 = lt.latextable(
    [T2, I2],
    "../tex/tabellen/tab4.tex",
    alignment = 'CC',
    form= ['.1f','.2f'],
    split = 3
)
ev.write('Integrale2' ,t4 )
