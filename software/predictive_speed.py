#!/usr/bin/env python

from filter_data import get_cones
from finish_line import detect_finish_line
from greedy_boundary_mapping import create_boundary_lines
from parse_data import parse_csv_data
from utility import separate_xy, angle_between
from matplotlib import pyplot as plt
import numpy as np

import os
import sys
import math

# Vertical vector
VERTICAL = (0, 1)

# Speed range in m/s
MIN_SPEED = 0.45 # 1 mph
MAX_SPEED = 2.24 # 5 mph

MAX_ANGLE = math.pi / 2 # For proportion

def make_plots(cones, outside_cones, left_boundary, right_boundary, vec,
    left_endpt, right_endpt):

    # Plot cones
    cone_xs, cone_ys = separate_xy(cones)
    blue = plt.scatter(cone_xs, cone_ys, color='blue', marker='^')

    # Plot outside cones
    outside_cone_xs, outside_cone_ys = separate_xy(outside_cones)
    cyan = plt.scatter(outside_cone_xs, outside_cone_ys, color='cyan', marker='^')

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
    black, = plt.plot([0, vec[0]], [0, vec[1]], 'k')
    vert, = plt.plot([0, 0], [5000 * coord for coord in VERTICAL], '--g')

    green = plt.scatter(0, 0, color='green')

    # Make plot look nice for report
    plt.xlabel('Distance in millimeters')
    plt.ylabel('Distance in millimeters')

    plt.legend(
        (orange, red, dashed, black, end, blue, cyan, green),
        ('Left Boundary', 'Right Boundary', 'Endpoint Vector', 'Trend Line', 'Boundary Endpoint', 'Detected Cone', 'Outside Cone', 'Vehicle Position'),
        loc='upper left'
    )

    plt.axis('equal')
    plt.xlim([-6000, 8000])
    plt.ylim([-4000, 8000])
    plt.title('Predictive Speed')
    plt.pause(0.00001)
    plt.gcf().clear()

def get_endpts(left_boundary, right_boundary):
    left_endpt = np.array([left_boundary[-1][0], left_boundary[-1][1]])
    right_endpt = np.array([right_boundary[-1][0], right_boundary[-1][1]])

    return left_endpt, right_endpt

def get_vec(left_endpt, right_endpt):
    vecx = np.mean([left_endpt[0], right_endpt[0]])
    vecy = np.mean([left_endpt[1], right_endpt[1]])

    return vecx, vecy

# In: Two lists of ordered points representing boundaries
# Out: Speed
def get_next_speed(left_boundary, right_boundary):
    # Find average vector of endpoints
    endpts = get_endpts(left_boundary, right_boundary)
    vec = get_vec(*endpts)

    # Find angle between average vector and vertical
    angle = angle_between(VERTICAL, vec)
    angle = angle if angle < MAX_ANGLE else MAX_ANGLE
    print('Angle from vertical: {} degrees'.format(math.degrees(angle)))

    proportion = (MAX_ANGLE - angle) / MAX_ANGLE
    print('Proportion: {}'.format(proportion))

    speed = MAX_SPEED * proportion
    return speed if speed > MIN_SPEED else MIN_SPEED

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    for filename in files:
        data = parse_csv_data(filename, 200)

        for frame in data:
            cones = get_cones(frame)
            cones_for_plot = list(cones)
            detect_finish_line(cones)
            outside_cones = set(cones_for_plot) - set(cones)

            left_boundary, right_boundary = create_boundary_lines(cones)

            speed = get_next_speed(left_boundary, right_boundary)
            print('Speed chosen: {} m/s'.format(speed))

            # For plot
            endpts = get_endpts(left_boundary, right_boundary)
            vec = get_vec(*endpts)
            make_plots(cones_for_plot, outside_cones, left_boundary, right_boundary, vec, *endpts)
