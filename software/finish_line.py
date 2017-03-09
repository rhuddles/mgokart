#!/usr/bin/env python

from parse_data import parse_csv_data
from filter_data import get_cones
from greedy_boundary_mapping import angle_between
from utility import separate_xy, dist

import sys
import math
import matplotlib.pyplot as plt

# Max thresholds between cones for defining a finish line
ANGLE_THRESHOLD = math.radians(15)
DIST_THRESHOLD = 500

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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    for filename in files:
        frame = parse_csv_data(filename)[0]
        cones = get_cones(frame)

        cone_xs, cone_ys = separate_xy(cones)
        blue = plt.scatter(cone_xs, cone_ys, marker='^', color='blue')

        finish_line_groups = get_finish_line_groups(cones)
        print finish_line_groups

        magenta = None
        for group in finish_line_groups:
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
        plt.show()
