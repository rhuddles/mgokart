#!/usr/bin/env python

from matplotlib import pyplot as plt
from parse_data import parse_csv_data
from data import left_turn_data, right_turn_data, straight_data
from operator import itemgetter

import math
import sys

# The maximum change in slope allowed
MAX_SLOPE_ALLOWED = math.pi / 3 # 60 degrees
VERTICAL_SLOPE = sys.maxint # "Infinity"

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def find_starting_cone(cones):
    # Get lower-leftmost cone
    cones.sort(key=lambda point: (point[1], point[0]))
    lower_left = cones[0]
    cones.pop(0)
    return lower_left

def find_closest_cone(current_cone, cones):
    min_distance = sys.maxint
    for c in range(0, len(cones)):
        dis = dist(current_cone, cones[c])
        if dis < min_distance:
            min_distance = dis
            cone = c
    return cone

def get_slope(cone, boundary):
    if len(boundary) < 2:
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

    # Find starting cone
    starting_cone = find_starting_cone(frame)

    # Create boundaries
    left_boundary = [starting_cone]
    right_boundary = []

    current_cone = starting_cone
    current_boundary = left_boundary
    prev_slope = VERTICAL_SLOPE

    # Assign each cone to a boundary
    while len(frame):
        # Get closest cone to current
        cone = find_closest_cone(current_cone, frame)
        current_cone = frame[cone]
        frame.pop(cone)

        # Get slope
        current_slope = get_slope(current_cone, current_boundary)

        # Check change in slope
        slope_diff = abs(abs(math.atan(current_slope)) - abs(math.atan(prev_slope)))
        if slope_diff > MAX_SLOPE_ALLOWED:
            current_boundary = right_boundary

        # Add cone to boundary
        current_boundary.append(current_cone)
        prev_slope = current_slope

    return left_boundary, right_boundary 

if __name__ == '__main__':
    #frames = parse_csv_data('lidar_data.csv')
    frames = [straight_data, left_turn_data, right_turn_data]
    for frame in frames:
        lines = create_boundary_lines(frame)
        # Uncomment to see boundaries on a scatter plot
        #plot_boundaries(lines[0], lines[1])
        print 'Left Boundary: ', lines[0]
        print 'Right Boundary: ', lines[1]
