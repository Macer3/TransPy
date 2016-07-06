# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import matplotlib as mpl
import numpy as np
# mpl.use('Qt5Agg')
from matplotlib import pyplot as plt
# mpl.matplotlib_fname()
# mpl.rcParams['backend']= 'Qt5Agg'
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.fill_between([1,2,3], [2,3,4], [3,5,4.5], where=None, interpolate=False, step=None)
line = ax.plot([1,2,3],color='r',linestyle='dashed', marker='o',fillstyle='left')
mpl.rcParams['lines.antialiased']=False
mpl.rcParams['patch.antialiased']=False
x = np.random.rand(0,10000)
y = np.random.rand(0,10000)
plt.plot(x,x)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects as path_effects
import matplotlib.transforms as transforms

fig = plt.figure()
ax=fig.add_subplot(111)

xx = np.random.rand(1,10000)
lines=ax.scatter(xx,xx,'ro')

x = np.arange(0., 2., 0.01)
y = np.sin(2*np.pi*x)
line, = ax.plot(x, y, lw=3, color='blue')

# shift the object over 2 points, and down 2 points
dx, dy = 2/72., -2/72.
offset = transforms.ScaledTranslation(dx, dy,
  fig.dpi_scale_trans)
shadow_transform = ax.transData + offset

# now plot the same data with our offset transform;
# use the zorder to make sure we are below the line
ax.plot(x, y, lw=3, color='gray',
  transform=shadow_transform,
  zorder=0.5*line.get_zorder())



t = ax.text(0.02, 0.5, 'Hatch shadow', fontsize=75, weight=1000, va='center')
t.set_path_effects([path_effects.PathPatchEffect(offset=(4, -4), hatch='xxxx',
                                                  facecolor='gray'),
                    path_effects.PathPatchEffect(edgecolor='white', linewidth=1.1,
                                                 facecolor='black')])
plt.show()

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

fig=plt.figure()
ax = fig.add_axes([0,0,1,1])
line = ax.plot([0,2,3])
line[0].set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'),
                       path_effects.Normal()])

text = plt.text(0.5, 0.5, 'Hello DIR effects world!',
                path_effects=[path_effects.withSimplePatchShadow()])

plt.plot([0, 3, 2, 5], linewidth=5, color='blue',
         path_effects=[path_effects.SimpleLineShadow(),
                       path_effects.Normal()])
plt.show()