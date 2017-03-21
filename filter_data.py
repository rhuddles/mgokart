#!/usr/bin/env python

from matplotlib import pyplot as plt
from parse_data import parse_csv_data
from utility import dist, separate_xy
import math as m
import os
import sys

def average(cones):
	x_total, y_total = separate_xy(cones)
	size = len(cones)

	return (sum(x_total) / size, sum(y_total) / size)

def filter_data(data, left_polys, right_polys):
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

def get_cones(data, left_polys, right_polys):
    filtered = filter_data(data, left_polys, right_polys)
    cones = group_cones(filtered)
    return cones

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['lidar_data/' + path for path in sorted(os.listdir('lidar_data'))]

    for filename in files:
        # Filter the LIDAR capture specified
        frame = parse_csv_data(filename)[0]

        # Plot raw data
        xs, ys = separate_xy(frame)
        red = plt.scatter(xs, ys, marker='x', color='red')

        cones = get_cones(frame)

        # Plot grouped cones
        xs, ys = separate_xy(cones)
        blue = plt.scatter(xs, ys, marker='^', color='blue')

        green = plt.scatter(0, 0, color='green')

        # Make plot look nice for report
        plt.axis('equal')

        plt.xlabel('Distance in millimeters')
        plt.ylabel('Distance in millimeters')

        plt.legend(
            (red, blue, green),
            ('Filtered Data Point', 'Detected Cone', 'Vehicle Position'),
            loc='upper left'
        )

        plt.title('Distance and Clustering Filtering')
        plt.show()
