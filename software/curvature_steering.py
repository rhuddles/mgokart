#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import math as m
import parse_data as pd
import filter_data as fd
import greedy as g
import os

files = sorted(os.listdir('data'))

filename = 'data/' + files[5]
print(filename)
frames = pd.parse_csv_data(filename)
cones = fd.get_cones(frames[0])
plt.scatter([pt[0] for pt in cones], [pt[1] for pt in cones], color='k')

boundaries = g.create_boundary_lines(cones)

x_plot = np.linspace(-10000, 10000, 2)

vecx = np.mean([boundaries[0][len(boundaries[0])-1][0], boundaries[1][len(boundaries[1])-1][0]])
vecy = np.mean([boundaries[0][len(boundaries[0])-1][1], boundaries[1][len(boundaries[1])-1][1]])

print m.degrees(m.atan(vecx/vecy))
nl = np.polyfit([0, vecx], [0, vecy], 1)
f = np.poly1d(nl)
plt.plot(x_plot, f(x_plot), 'r')

plt.xlim([-10000, 10000])
plt.ylim([-10000, 10000])
plt.show()

