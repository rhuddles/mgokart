#!/usr/bin/env python

from data import left_turn_data, right_turn_data, straight_data
from filter_data import get_cones
from matplotlib import pyplot as plt
from operator import itemgetter
from parse_data import parse_csv_data
from utility import dist

import math
import sys
import time

# The maximum change in slope allowed
MAX_ANGLE_ALLOWED = math.radians(50)
MAX_DISTANCE_ALLOWED = 5500 # 5.5 meters
VERTICAL_SLOPE = sys.maxint # "Infinity"

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

def plot_boundaries(cones, left_boundary, right_boundary):
    # Plot cones
    blue = plt.scatter([cone[0] for cone in cones], [cone[1] for cone in cones], color='blue', marker='^')

    # Plot left boundary
    left_xs = [point[0] for point in left_boundary]
    left_ys = [point[1] for point in left_boundary]
    orange, = plt.plot(left_xs, left_ys, color='orange')

    # Plot right boundary
    right_xs = [point[0] for point in right_boundary]
    right_ys = [point[1] for point in right_boundary]
    red, = plt.plot(right_xs, right_ys, color='red')

    green = plt.scatter(0, 0, color='green')

    # Make plot look nice for report
    plt.xlabel('Distance in millimeters')
    plt.ylabel('Distance in millimeters')

    plt.legend(
        (orange, red, blue, green),
        ('Left Boundary', 'Right Boundary', 'Detected Cone', 'Vehicle Position'),
        loc='upper left'
    )

    plt.axis('equal')
    plt.title('Greedy Boundary Mapping')
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
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    for filename in files:
        frame = parse_csv_data(filename)[0]
        cones = get_cones(frame)
        cones_for_plot = list(cones)

        start = time.time()
        lines = create_boundary_lines(cones)
        print('Boundary mapping took %f seconds' % (time.time() - start))

        # Uncomment to see boundaries on a scatter plot
        plot_boundaries(cones_for_plot, lines[0], lines[1])
        print 'Left Boundary: ', lines[0]
        print 'Right Boundary: ', lines[1]
