#!/usr/bin/env python

from parse_data import parse_csv_data
from filter_data import get_cones
from boundary_mapping import angle_between
from utility import dist, separate_xy
from functools import partial

import itertools
import sys
import math

try:
    import matplotlib.pyplot as plt
except:
    pass

# Max thresholds between cones for defining a finish line
ANGLE_THRESHOLD = math.radians(30)
DIST_THRESHOLD = 500 # Half meter

# Finish Line constraints
#   Two groups
#   Line containing all is 'perpendicular' to our heading (vertical?)
#   Groups ~4m apart

def vector_between(a, b):
    return (b[0] - a[0], b[1] - a[1])

def order_cone_group(cones):
    best_order = None
    best_error = None

    for order in itertools.permutations(cones):
        error = dist(order[0], order[1]) + dist(order[1], order[2])
        if not best_order or error < best_error:
            best_order = order
            best_error = error

    return best_order

def get_finish_line_groups(cones, verbose=False):
    groups = []

    for group in itertools.combinations(cones, 3):
        pt1, pt2, pt3 = order_cone_group(group)

        vec1 = vector_between(pt1, pt2)
        vec2 = vector_between(pt2, pt3)

        theta = angle_between(vec1, vec2)
        dist1 = dist(pt1, pt2)
        dist2 = dist(pt2, pt3)

        if verbose:
            print pt1, pt2, pt3, theta, dist1, dist2

        if theta < ANGLE_THRESHOLD and dist1 < DIST_THRESHOLD \
                and dist2 < DIST_THRESHOLD:
            groups.append([pt1, pt2, pt3])

    return groups

def remove_outside_cones(group, cones):
    outer_cone = max(group[0], group[2], key=lambda p: dist((0,0), p))

    # catch exceptions in case of double removal
    try:
        # remove middle cone
        cones.remove(group[1])
        # remove outer cone
        cones.remove(outer_cone)
    except ValueError:
        pass

# In: A list of cones
# Out: True if we have passed the finish line; modifies cones by removing extra
#       cones from finish line groups
def detect_finish_line(cones):
    count_lap = False
    finish_line_groups = get_finish_line_groups(cones)
    # TODO: This should examine the groups and apply the constraints above
    #       to check if this really is the finish line.
    #       If this is a finish line it should check we passed it and
    #       return true
    for group in finish_line_groups:
        remove_outside_cones(group, cones)

    if len(finish_line_groups) == 2:
        if finish_line_groups[0][0][1] <= 0:
            try:
                if detect_finish_line.last_finish_line[0][0][1] > 0:
                    count_lap = True
            except AttributeError:
                pass

    detect_finish_line.last_finish_line = finish_line_groups

    # TODO: this eventually needs to be (left, right), easier with short term memory
    return finish_line_groups, count_lap

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['lidar_data/' + path for path in sorted(os.listdir('lidar_data'))]

    for filename in files:
        data = parse_csv_data(filename, 200)

        for frame in data:
            cones = get_cones(frame, [], [])

            cone_xs, cone_ys = separate_xy(cones)
            blue = plt.scatter(cone_xs, cone_ys, marker='^', color='blue')

            finish_line_groups = get_finish_line_groups(cones)

            magenta = None
            for group in finish_line_groups:
                # Plot a group of cones that looks like a finish line grouping
                group_xs, group_ys = separate_xy(group)
                magenta = plt.scatter(group_xs, group_ys, marker='^', color='magenta')

            green = plt.scatter(0, 0, color='green')

            # Make plot look nice for report
            plt.xlabel('Distance in millimeters')
            plt.ylabel('Distance in millimeters')

            plt.legend(
                (magenta, blue, green),
                ('Finish Line Cone', 'Detected Cone', 'Vehicle Position'),
                loc='upper left'
            )

            plt.axis('equal')
            plt.title('Finish Line Detection')
            plt.draw()
            plt.pause(0.00001)
            plt.gcf().clear()
