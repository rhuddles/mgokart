#! /usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import parse_data as pd
from data import left_turn_data as data


frames = pd.parse_csv_data('lidar_data.csv')

x = [frame[0] for frame in frames[10]]
y = [frame[1] for frame in frames[10]]

for degree in range(1,5):
    polys = np.polyfit(x, y, degree)
    f = np.poly1d(polys)
    plt.subplot(2, 2, degree)
    for i in range(0,len(y)):
        plt.scatter(x[i], y[i],  color='red' if y[i] < f(x[i]) else 'blue');
    plt.ylabel('Degree = %d' % degree)


plt.show()
