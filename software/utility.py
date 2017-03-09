#!/usr/bin/env python

import math as m

def separate_xy(points):
    return ([point[0] for point in points],
            [point[1] for point in points])

def dist(a, b):
    xdiff = a[0] - b[0]
    ydiff = a[1] - b[1]
    return m.sqrt(xdiff**2 + ydiff**2)
