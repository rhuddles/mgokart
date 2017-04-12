#!/usr/bin/env python

from parse_data import parse_csv_data
from utility import dist, separate_xy, separate_and_flip

import math
import numpy
import os
import sys

try:
    from matplotlib import pyplot as plt
except:
    pass

MIN_RANGE =   500 #  0.5m
MAX_RANGE = 10000 # 10.0m

def average(cones):
	x_total, y_total = separate_xy(cones)
	size = len(cones)

	return (sum(x_total) / size, sum(y_total) / size)

def filter_with_coefs(data, coefs):
    valid = []
    invalid = []
    flipped = separate_and_flip(data)

    for x, y in zip(flipped[0], flipped[1]):
        dist_coefs = [2*coefs[0]**2,
                3*coefs[1]*coefs[0],
                coefs[1]**2 + 2*coefs[2]*coefs[0] - 2*coefs[0]*y + 1,
                coefs[2]*coefs[1] - coefs[1]*y - x]
        x_min_distance = numpy.roots(dist_coefs)
        f = numpy.poly1d(coefs)

        is_valid = False
        for u in x_min_distance:
            if numpy.isreal(u):
                if math.sqrt((u - x)**2 + (f(u) - y)**2) < 1000:
                    is_valid = True
                    break

        if is_valid:
            valid.append([-y, x])
        else:
            invalid.append([-y, x])

    return valid, invalid


def filter_data(data, left_coefs, right_coefs):
    might_be_valid = []
    filtered = []

    for pt in data:
        dist = math.sqrt(pt[0]**2 + pt[1]**2)

        if (dist < MAX_RANGE and dist > MIN_RANGE):
            might_be_valid.append(pt)

    if len(left_coefs) >= 3 and len(right_coefs) >= 3:
        valid, might_be_valid = filter_with_coefs(might_be_valid, right_coefs)
        filtered += valid
        valid, might_be_valid = filter_with_coefs(might_be_valid, left_coefs)
        filtered += valid
    else:
        filtered = might_be_valid

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
