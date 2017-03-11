#!/usr/bin/env python

from filter_data import get_cones
from greedy_boundary_mapping import create_boundary_lines
from parse_data import parse_csv_data
from utility import separate_xy
from matplotlib import pyplot as plt
import numpy as np

import os
import sys
import math

def make_plots(cones, left_boundary, right_boundary,
        left_endpt, right_endpt, vecx, vecy):

    # Plot cones
    cone_xs, cone_ys = separate_xy(cones)
    blue = plt.scatter(cone_xs, cone_ys, color='blue', marker='^')

    # Plot left boundary
    left_xs, left_ys = separate_xy(left_boundary)
    orange, = plt.plot(left_xs, left_ys, color='orange')

    # Plot right boundary
    right_xs, right_ys = separate_xy(right_boundary)
    red, = plt.plot(right_xs, right_ys, color='red')

    # Plot vectors
    dashed, = plt.plot([0, left_endpt[0]], [0, left_endpt[1]], '--k')
    plt.plot([0, right_endpt[0]], [0, right_endpt[1]], '--k')

    # Plot boundary endpoints
    end = plt.scatter(left_endpt[0], left_endpt[1], color='k', marker='^')
    plt.scatter(right_endpt[0], right_endpt[1], color='k', marker='^')

    # Plot trend line
    black, = plt.plot([0, vecx], [0, vecy], 'k')
    green = plt.scatter(0, 0, color='green')

    # Make plot look nice for report
    plt.xlabel('Distance in millimeters')
    plt.ylabel('Distance in millimeters')

    plt.legend(
        (orange, red, dashed, black, end, blue, green),
        ('Left Boundary', 'Right Boundary', 'Regression Line', 'Trend Line', 'Boundary Endpoint', 'Detected Cone', 'Vehicle Position'),
        loc='upper left'
    )

    plt.axis('equal')
    plt.xlim([-6000, 8000])
    plt.ylim([-4000, 8000])
    plt.title('Predictive Speed')
    plt.show()

def get_vec(left_boundary, right_boundary):
    left_endpt = np.array([left_boundary[-1][0], left_boundary[-1][1]])
    right_endpt = np.array([right_boundary[-1][0], right_boundary[-1][1]])

    vecx = np.mean([left_endpt[0], right_endpt[0]])
    vecy = np.mean([left_endpt[1], right_endpt[1]])

    return vecx, vecy, left_endpt, right_endpt

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    for filename in files:
        frame = parse_csv_data(filename)[0]
        cones = get_cones(frame)
        left_boundary, right_boundary = create_boundary_lines(cones)
        vec = get_vec(left_boundary, right_boundary)

        make_plots(cones, left_boundary, right_boundary, vec[2], vec[3], vec[0], vec[1])
