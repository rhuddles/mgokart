#!/usr/bin/env python

from matplotlib import pyplot as plt
from parse_data import parse_csv_data
import math as m
import os
import sys

def filter_data(data):
    filtered = []

    for pt in data:
        dist = m.sqrt(pt[0]**2 + pt[1]**2)

        # These numbers are super arbitrary right now
        # 30 mm for minumum distance from lidar spec
        # 10000 mm for 10 m cause why not
        if (dist < 10000 and dist > 30):
            filtered.append(pt)

    return filtered

def group_cones(data):
    cones = []

    for i in range(1, len(data)-1):
        xdiff = data[i][0] - data[i-1][0]
        ydiff = data[i][1] - data[i-1][1]
        dist = m.sqrt(xdiff**2 + ydiff**2)

        # 250 mm = 25 cm which is approx width of base of cone
        if (dist > 250):
            cones.append(data[i])

    return cones

def get_cones(data):
    filtered = filter_data(data)
    cones = group_cones(filtered)
    return cones

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    for filename in files:
        # Filter the LIDAR capture specified
        frame = parse_csv_data(filename)[0]
        cones = get_cones(frame)

        # Plot raw data
        xs = [point[0] for point in frame]
        ys = [point[1] for point in frame]
        plt.scatter(xs, ys, marker='x', color='red')

        # Plot filtered data
        xs = [point[0] for point in cones]
        ys = [point[1] for point in cones]
        plt.scatter(xs, ys, marker='^', color='blue')

        plt.scatter(0, 0, color='green')

        plt.title(filename)
        plt.show()
