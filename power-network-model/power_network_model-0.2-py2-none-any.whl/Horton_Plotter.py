"""
Nice program to plot the Horton ouput file

"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.patheffects as path_effects

################################################################################
# READ IN DATA
#-------------------------------------------------------------------------------
# Substations
filename = "Data/Horton_Model_Output.txt"
f = open(filename, 'r')
data = f.readlines()
f.close()

a, b, c, d, e, f, z = np.loadtxt(filename, usecols = (0, 1, 2, 3, 4, 5, 8), unpack = True)

nnodes = 40
nconnects = len(a) - nnodes

site_name = [x.split("\t")[-1] for x in data[:nnodes]]

sitenum = a[0:nnodes]
geolat = b[0:nnodes]
geolon = c[0:nnodes]
voltages = f[0:nnodes]

colors = [[[1., 0., 0., 1.], [0., 0., 1., 1.]][[500, 345].index(x)] for x in voltages]

#-------------------------------------------------------------------------------
# Connections
nodefrom = a[nnodes:]
nodeto = b[nnodes:]

latsfrom = [geolat[list(sitenum).index(x)] for x in nodefrom]
lonsfrom = [geolon[list(sitenum).index(x)] for x in nodefrom]

latsto = [geolat[list(sitenum).index(x)] for x in nodeto]
lonsto = [geolon[list(sitenum).index(x)] for x in nodeto]

lineresist = c[nnodes:]

connections = np.ones(len(latsfrom))

t_cnn = sorted(list(set(list(nodefrom) + list(nodeto))))

colors2 = []
for i in z[nnodes:]:
    if np.isnan(i):
        colors2.append([1., 1., 1., 1.])
    else:
        colors2.append([[1., 0., 0., 1.], [0., 0., 1., 1.]][[500, 345].index(i)])
################################################################################
# Plot 1 - Initial Selection

clf()

fig = plt.figure(1)
ax = plt.subplot(111)

water = "CadetBlue"
land = "AliceBlue"

ww = 'white'
bb = 'black'

m = Basemap(projection = 'merc', llcrnrlat= 32.5, urcrnrlat= 35.0, llcrnrlon=-87.5, urcrnrlon=-80.0, resolution='l',area_thresh=100)

m.drawcoastlines(color = 'k', linewidth = 2)
m.drawparallels(np.arange(0,360,0.5) ,labels=[1, 0, 0, 0], color = 'k', fontsize =24)
m.drawmeridians(np.arange(0,360,1),labels=[0,0,0,1], color = 'k', fontsize =24)
m.drawcountries(linewidth = 2)
m.drawmapboundary(fill_color=water)
m.fillcontinents(color=land,lake_color=water)

xxx, yyy = m(geolon, geolat)
coll = ax.scatter(xxx, yyy, color=colors, picker = 2, s=200, zorder = 100)

ref_points = []

for index, value in enumerate(nodefrom):
    
    a = [lonsfrom[index], lonsto[index]]
    b = [latsfrom[index], latsto[index]]
    xxx, yyy = m(a, b)

    plot(xxx, yyy, c = colors2[index], linestyle = "-", zorder = 100)

    ref_points.append(xxx + yyy)
    
    fig.canvas.draw()


title("Horton Model", fontsize = 24)

plt.show()

################################################################################
################################################################################

