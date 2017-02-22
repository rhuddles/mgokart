#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import math as m
import parse_data as pd
import filter_data as fd
import greedy as g
import os

filename = 'data/2017_02_19_19_51_09_729_sharp_right.csv'
frames = pd.parse_csv_data(filename)
cones = fd.get_cones(frames[0])

plt.scatter([pt[0] for pt in cones], [pt[1] for pt in cones], color='b', marker='^')

boundaries = g.create_boundary_lines(cones)

left_xs = [point[0] for point in boundaries[0]]
left_ys = [point[1] for point in boundaries[0]]
plt.plot(left_xs, left_ys, color='orange')

right_xs = [point[0] for point in boundaries[1]]
right_ys = [point[1] for point in boundaries[1]]
plt.plot(right_xs, right_ys, color='red')

x_plot = np.linspace(-10000, 10000, 2)

vecx = np.mean([boundaries[0][len(boundaries[0])-1][0], boundaries[1][len(boundaries[1])-1][0]])
vecy = np.mean([boundaries[0][len(boundaries[0])-1][1], boundaries[1][len(boundaries[1])-1][1]])

print m.degrees(m.atan(vecx/vecy))
nl = np.polyfit([0, vecx], [0, vecy], 1)
f = np.poly1d(nl)

plt.plot(x_plot, f(x_plot), 'k')
plt.scatter(0, 0, color='g')

plt.xlim([-6000, 8000])
plt.ylim([-4000, 8000])
plt.show()

