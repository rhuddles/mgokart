#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import parse_data as pd
import filter_data as fd
import os

files = sorted(os.listdir('data'))

frames = pd.parse_csv_data('data/' + files[5])
cones = fd.get_cones(frames[0])

x = [frame[0] for frame in cones]
y = [frame[1] for frame in cones]

x_plot = np.linspace(-10000, 10000, 20000)

for n in range(1,3):
    # Fits a n degree polynomial to data
    polys = np.polyfit(x, y, n)
    f = np.poly1d(polys)
    plt.subplot(1, 2, n)

    # If above polynomial, its one boundary, otherwise its the other
    for i in range(0,len(y)):
        plt.scatter(x[i], y[i], color='r' if y[i] < f(x[i]) else 'b',
            marker='^');

    # Plot the boundary for visualization purposes
    plt.plot(x_plot, f(x_plot), '--k')

    # Label plots and set axes
    plt.suptitle('Regression Boundary Mapping', fontsize=16)
    plt.ylabel('Degree = %d' % n)
    plt.xlim([-10000, 10000])
    plt.ylim([-10000, 10000])

plt.show()

