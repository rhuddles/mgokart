#!/usr/bin/env python

from parse_data import parse_csv_data
from filter_data import get_cones
from greedy_boundary_mapping import angle_between
from utility import dist, separate_xy
from functools import partial

import sys
import math
import matplotlib.pyplot as plt

# Max thresholds between cones for defining a finish line
ANGLE_THRESHOLD = math.radians(15)
DIST_THRESHOLD = 500 # Half meter

# Finish Line constraints
#   Two groups
#   Line containing all is 'perpendicular' to our heading (vertical?)
#   Groups ~4m apart

def vector_between(a, b):
    return (b[0] - a[0], b[1] - a[1])

def get_finish_line_groups(cones):
    groups = []

    i = 2
    while i < len(cones):
        pt1 = cones[i-2]
        pt2 = cones[i-1]
        pt3 = cones[i]

        vec1 = vector_between(pt1, pt2)
        vec2 = vector_between(pt2, pt3)

        theta = angle_between(vec1, vec2)
        dist1 = dist(pt1, pt2)
        dist2 = dist(pt2, pt3)

        print pt1, pt2, pt3, theta, dist1, dist2

        if theta < ANGLE_THRESHOLD and dist1 < DIST_THRESHOLD \
                and dist2 < DIST_THRESHOLD:
            groups.append((pt1, pt2, pt3))
            i += 3
        else:
            i += 1

    return groups

def get_boundary_cone(group):
    # Return the cone closest to us
    dist_from_origin = partial(dist, (0,0))
    return min(group, key=dist_from_origin)

def remove_outside_cones(group, cones):
    group = list(group)
    boundary_cone = get_boundary_cone(group)
    group.remove(boundary_cone)

    for outside_cone in group:
        cones.remove(outside_cone)

# In: A list of cones
# Out: True if we have passed the finish line; modifies cones by removing extra
#       cones from finish line groups
def detect_finish_line(cones):
    finish_line_groups = get_finish_line_groups(cones)

    # TODO: This should examine the groups and apply the constraints above
    #       to check if this really is the finish line.
    #       If this is a finish line it should check we passed it and
    #       return true
    for group in finish_line_groups:
        remove_outside_cones(group, cones)

    return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    for filename in files:
        data = parse_csv_data(filename, 200)

        for frame in data:
            cones = get_cones(frame)

            cone_xs, cone_ys = separate_xy(cones)
            blue = plt.scatter(cone_xs, cone_ys, marker='^', color='blue')

            finish_line_groups = get_finish_line_groups(cones)

            magenta = None
            for group in finish_line_groups:
                # Plot a group of cones that looks like a finish line grouping
                group_xs, group_ys = separate_xy(group)
                magenta = plt.scatter(group_xs, group_ys, marker='^', color='magenta')

                # Highlight cone that is on the boundary
                boundary_cone = get_boundary_cone(group)
                black = plt.Circle(boundary_cone, 200, color='k', fill=False)
                plt.gca().add_artist(black)

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
