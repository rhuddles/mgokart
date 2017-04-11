#!/usr/bin/env python

import math
import numpy
import os

def separate_xy(points):
    return ([point[0] for point in points],
            [point[1] for point in points])

def flip_xy(x, y):
    return (y, [-a for a in x])

def separate_and_flip(points):
    return flip_xy(*separate_xy(points))

def dist(a, b):
    xdiff = a[0] - b[0]
    ydiff = a[1] - b[1]
    return math.sqrt(xdiff**2 + ydiff**2)

def angle_between(u, v):
    # cos(theta) = (u dot v) / (||u|| * ||v||)
    num = u[0] * v[0] + u[1] * v[1]
    den = dist((0, 0), u) * dist((0, 0), v)
    # limit the value passed to acos to [-1.0, 1.0]
    ah = max(-1.0, min(1.0, num / den))
    return math.acos(ah)

def regression(boundary, degree=2):
    xs, ys = separate_and_flip(boundary)
    return numpy.polyfit(xs, ys, degree)


# For Validation
def create_annotate_filename(filename, number):
    basename = os.path.basename(filename)
    base, _ = basename.split('.')
    save_file = '{}_{}'.format(base, str(number))
    return os.path.join('lidar_data', 'annotated', save_file)
