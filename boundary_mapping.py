#!/usr/bin/env python

from parse_data import parse_csv_data
from operator import itemgetter
from filter_data import *

import math
import sys
import time

try:
    from matplotlib import pyplot as plt
except:
    pass

# The maximum change in slope allowed
MAX_ANGLE_ALLOWED = math.radians(45)
MAX_DISTANCE_ALLOWED = 5500 # 5.5 meters
VERTICAL_SLOPE = sys.maxint # "Infinity"

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def angle_between(u, v):
    # cos(theta) = (u dot v) / (||u|| * ||v||)
    num = u[0] * v[0] + u[1] * v[1]
    den = dist((0, 0), u) * dist((0, 0), v)
    return math.acos(num / den)

def find_lower_left_cone(cones):
    # Get lower-leftmost cone
    lower_left = cones[-1]
    cones.pop(-1)
    return lower_left

def find_lower_right_cone(cones):
    # Get lower-rightmost cone
    lower_right = cones[0]
    cones.pop(0)
    return lower_right

def find_closest_cone(current_cone, cones):
    min_distance = sys.maxint
    if not len(cones):
        return -1
    for c in range(0, len(cones)):
        dis = dist(current_cone, cones[c])
        if dis < min_distance:
            min_distance = dis
            cone = c
    return cone

def get_slope(cone, boundary):
    if len(boundary) < 1:
        return VERTICAL_SLOPE

    end_cone = boundary[-1]

    rise = end_cone[1] - cone[1]
    run = end_cone[0] - cone[0]
    return VERTICAL_SLOPE if run == 0 else rise / run

def plot_boundaries(cones, left_boundary, right_boundary):
    # Plot cones
    blue = plt.scatter([cone[0] for cone in cones], [cone[1] for cone in cones], color='blue', marker='^', label='Detected Cone')

    # Plot left boundary
    left_xs = [point[0] for point in left_boundary]
    left_ys = [point[1] for point in left_boundary]
    orange, = plt.plot(left_xs, left_ys, color='orange', label='Left Boundary')

    # Plot right boundary
    right_xs = [point[0] for point in right_boundary]
    right_ys = [point[1] for point in right_boundary]
    red, = plt.plot(right_xs, right_ys, color='red', label='Right Boundary')

    green = plt.scatter(0, 0, color='green', label='Vehicle Position')

    # Make plot look nice for report
    plt.xlabel('Distance in millimeters')
    plt.ylabel('Distance in millimeters')

    #plt.legend(
    #    (orange, red, blue, green),
    #    ('Left Boundary', 'Right Boundary', 'Detected Cone', 'Vehicle Position'),
    #    loc='upper left'
    #)

    plt.axis('equal')
    # plt.title('Greedy Boundary Mapping')
    # plt.show()
    return plt


def create_boundary_lines(cones, verbose = False):

    start_left = find_lower_left_cone(cones)
    start_right = find_lower_right_cone(cones)

    left_bound = [start_left]
    right_bound = [start_right]


    while len(cones):

        skip_boundary = False

        # Left boundary next cone
        cone = find_closest_cone(left_bound[-1], cones)
        if cone < 0:
            break

        # Print distances
        if verbose:
            print "Testing Cone at " + str(cones[cone]) + " for left boundary"
            print "Left: " + str(dist(cones[cone], left_bound[-1]))
            print "Right: " + str(dist(cones[cone], right_bound[-1]))

        # Get change in slope
        if len(left_bound) > 1:
            current_vector = (cones[cone][0] - left_bound[-1][0], cones[cone][1] - left_bound[-1][1])
            prev_vector = (left_bound[-1][0] - left_bound[-2][0], left_bound[-1][1] - left_bound[-2][1])
            theta = angle_between(prev_vector,current_vector)
        else: theta = 0

        # Get Distance to next cone
        dist_left = dist(cones[cone], left_bound[-1])
        dist_right = dist(cones[cone], right_bound[-1])

        # Test cone
        if dist_right < dist_left or dist_left > MAX_DISTANCE_ALLOWED or theta > MAX_ANGLE_ALLOWED:
            skip_boundary = True
            if verbose:
                print "Left side skipped"
        else:
            if verbose:
                print "Adding cone to left bound"
            left_bound.append(cones[cone])
            cones.pop(cone)

        # Right boundary next cone
        cone = find_closest_cone(right_bound[-1], cones)
        if cone < 0:
            break

        # Print distances
        if verbose:
            print "Testing Cone at " + str(cones[cone]) + " for right boundary"
            print "Left: " + str(dist(cones[cone], left_bound[-1]))
            print "Right: " + str(dist(cones[cone], right_bound[-1]))

        # Get change in slope
        if len(right_bound) > 1:
            current_vector = (cones[cone][0] - right_bound[-1][0], cones[cone][1] - right_bound[-1][1])
            prev_vector = (right_bound[-1][0] - right_bound[-2][0], right_bound[-1][1] - right_bound[-2][1])
            theta = angle_between(prev_vector,current_vector)
        else: theta = 0

        # Get Distance to next cone
        dist_left = dist(cones[cone], left_bound[-1])
        dist_right = dist(cones[cone], right_bound[-1])

        # Test cone
        if dist_left < dist_right or dist_right > MAX_DISTANCE_ALLOWED or theta > MAX_ANGLE_ALLOWED:
            if verbose:
                print "Right side finished"
            if skip_boundary:
                break
        else:
            if verbose:
                print "Adding cone to right bound"
            right_bound.append(cones[cone])
            cones.pop(cone)

    return left_bound, right_bound



if __name__ == '__main__':
    #frames = [straight_data, left_turn_data, right_turn_data]
    frames = parse_csv_data('lidar_data/2017_02_19_19_51_09_729_sharp_right.csv')
    start = time.time()
    frame = filter_data(frames[0])
    cones = get_cones(frame)
    plt.scatter([cone[0] for cone in cones], [cone[1] for cone in cones], color='b')
    print('CONES', cones)
    frames = [cones]
    for frame in frames:
        lines = create_boundary_lines(frame)
        print('Boundary mapping took %f seconds' % (time.time() - start))
        # Uncomment to see boundaries on a scatter plot
        plot_boundaries(lines[0], lines[1])
        print 'Left Boundary: ', lines[0]
        print 'Right Boundary: ', lines[1]
