#!/usr/bin/env python

from matplotlib import pyplot as plt
from parse_data import parse_csv_data
import math as m
import os
import sys

def dist(a, b):
    xdiff = a[0] - b[0]
    ydiff = a[1] - b[1]
    return m.sqrt(xdiff**2 + ydiff**2)

def average(cones):
    x_total = sum([pt[0] for pt in cones])
    y_total = sum([pt[1] for pt in cones])
    size = len(cones)

    return (x_total / size, y_total / size)

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

    # all the points representing the current cone
    this_cone = [data[0]]

    for i in range(1, len(data)):
        # 250 mm = 25 cm which is approx width of base of cone
        if dist(this_cone[0], data[i]) <= 250:
            # this point is representing the same cone
            this_cone.append(data[i])
        else:
            # new cone! save and start next cone
            cones.append(average(this_cone))
            this_cone = [data[i]]

    cones.append(average(this_cone))
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

        # Plot raw data
        xs = [point[0] for point in frame]
        ys = [point[1] for point in frame]
        plt.scatter(xs, ys, marker='x', color='red')

        filtered = filter_data(frame)

        # Plot filtered, ungrouped points
        xs = [point[0] for point in filtered]
        ys = [point[1] for point in filtered]
        plt.scatter(xs, ys, marker='o', color='black')

        cones = group_cones(filtered)

        # Plot grouped cones
        xs = [point[0] for point in cones]
        ys = [point[1] for point in cones]
        plt.scatter(xs, ys, marker='^', color='blue')

        plt.scatter(0, 0, color='green')

        plt.title(filename)
        plt.show()
