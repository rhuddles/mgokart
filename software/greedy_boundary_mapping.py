from matplotlib import pyplot as plt
from parse_data import parse_csv_data
from data import left_turn_data, right_turn_data, straight_data
from operator import itemgetter

import math
import sys
import random

MAX_SLOPE_ALLOWED = math.pi / 4

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def find_starting_cone(cones):
    print 'sorted by both', sorted(cones, key=lambda point: (point[1], point[0]))
    # Get lower-leftmost cone
    cones.sort(key=lambda point: (point[1], point[0]))
    lower_left = cones[0]
    cones.pop(0)
    print 'starting', lower_left
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
        return sys.maxint

    end_cone = boundary[-1]
    
    rise = end_cone[1] - cone[1]
    run = end_cone[0] - cone[0]
    return sys.maxint if run == 0 else rise / run

# In: List of x,y tuples - [(x, y), ...]
# Out: Two ordered lists x,y tuples - [(x,y), ...], [(x,y), ...]
def create_boundary_lines(frame):
    frame = left_turn_data
    # FOR TESTING
    random.shuffle(frame)

    # Find starting cone
    starting_cone = find_starting_cone(frame)

    # Create boundaries
    left_boundary = [starting_cone]
    right_boundary = []

    current_cone = starting_cone
    current_slope = sys.maxint
    current_boundary = left_boundary

    # Assign each cone to a boundary
    while len(frame):
        # Get closest cone to current
        cone = find_closest_cone(current_cone, frame)

        print 'next cone', frame[cone]
        current_cone = frame[cone]
        frame.pop(cone)

        # Get slope
        slope = get_slope(current_cone, current_boundary)
        print 'slope', slope

        # Check change in slope
        slope_diff = abs(math.atan(slope) - math.atan(current_slope))
        print 'slope diff', slope_diff
        if  slope_diff > MAX_SLOPE_ALLOWED:
            print 'switching boundaries'
            current_boundary = right_boundary

        current_slope = slope
        current_boundary.append(current_cone)
        print 'current boundary', current_boundary


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
    return left_boundary, right_boundary 

if __name__ == '__main__':
    create_boundary_lines([])
    #frames = parse_csv_data('lidar_data.csv')
    #for frame in frames:
    #    lines = create_boundary_lines(frame)
    #    print lines
