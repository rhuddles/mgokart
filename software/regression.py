#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import parse_data as pd
import filter_data as fd
import os

files = sorted(os.listdir('data'))

frames = pd.parse_csv_data('data/' + files[8])

filtered_frame = fd.filter_data(frames[0])
cones = fd.get_cones(filtered_frame)

print len(cones)

#Rotate image 90 degrees to deal with infinite slope on straightaways
x = [frame[1] for frame in cones]
y = [-frame[0] for frame in cones]

x_plot = np.linspace(-10000, 10000, 50000)

for degree in range(1,5):
    polys = np.polyfit(x, y, degree)
    f = np.poly1d(polys)
    plt.subplot(2, 2, degree)
    for i in range(0,len(y)):
        plt.scatter(x[i], y[i],  color='red' if y[i] < f(x[i]) else 'blue',
            marker='^');
        plt.plot(x_plot, f(x_plot), color='black')
    plt.ylabel('Degree = %d' % degree)
    plt.xlim([-10000, 10000])
    plt.ylim([-10000, 10000])

plt.show()
