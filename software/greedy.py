#!/usr/bin/env python

from matplotlib import pyplot as plt
from parse_data import parse_csv_data
from data import left_turn_data, right_turn_data, straight_data
from operator import itemgetter
from filter_data import *

import math
import sys
import time

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

def plot_boundaries(left_boundary, right_boundary):
    # Plot left boundary
    left_xs = [point[0] for point in left_boundary]
    left_ys = [point[1] for point in left_boundary]
    plt.scatter(left_xs, left_ys, marker='^', color='green')
    plt.plot(left_xs, left_ys, color='green')

    # Plot right boundary
    right_xs = [point[0] for point in right_boundary]
    right_ys = [point[1] for point in right_boundary]
    plt.scatter(right_xs, right_ys, marker='^', color='yellow')
    plt.plot(right_xs, right_ys, color='yellow')

    plt.show()

# In: List of x,y tuples - [(x, y), ...]
# Out: Two ordered lists x, y tuples - [(x,y), ...], [(x,y), ...]
def create_boundary_lines(frame):
    if not len(frame):
        return [], []

    # Find left boundary starting cone
    starting_cone = find_lower_left_cone(frame)

    # Create boundaries
    left_boundary = create_boundary_line(frame, starting_cone)

    print('##### switched boundaries')
    starting_cone = find_lower_right_cone(frame)

    right_boundary = create_boundary_line(frame, starting_cone)

    return left_boundary, right_boundary

def create_boundary_line(frame, starting_cone):
    boundary = [starting_cone]
    prev_cone = starting_cone
    prev_vector = (0., 1.) # previous slope vector, start assuming vertical

    ignored_cones = []
    # Assign each cone to a boundary
    while len(ignored_cones) < len(frame):
        # Get closest cone to current
        cone = find_closest_cone(prev_cone, frame)
        current_cone = frame[cone]

        # Get slope vector
        current_vector = (current_cone[0] - prev_cone[0],
                        current_cone[1] - prev_cone[1])

        # Check change in angle
        theta = angle_between(prev_vector, current_vector)
        print('current: %s\ttheta: %f' % (str(current_cone), math.degrees(theta)))

        if theta > MAX_ANGLE_ALLOWED or \
                dist(current_cone, prev_cone) > MAX_DISTANCE_ALLOWED:
            print('** ignored')
            ignored_cones.append(current_cone)
            frame.pop(cone)
        else:
            # Add cone to boundary
            boundary.append(current_cone)
            # Save cone and slope vector
            prev_cone = current_cone
            prev_vector = current_vector

            frame.pop(cone)
            # Put ignored cones back into frame
            frame = ignored_cones + frame
            ignored_cones = []

    frame = ignored_cones + frame
    return boundary

if __name__ == '__main__':
    #frames = [straight_data, left_turn_data, right_turn_data]
    frames = parse_csv_data('data/2017_02_19_19_43_24_378_in_slight_left_so_good.csv')
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
