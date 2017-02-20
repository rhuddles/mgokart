#!/usr/bin/env python

import math as m

def filter_data(data):
    filtered = []

    for pt in data:
        dist = m.sqrt(pt[0]**2 + pt[1]**2)

        # These numbers are super arbitrary right now
        # 30 mm for minumum distance from lidar spec
        # 10000 mm for 10 m cause why not
        if (dist < 10000 and dist > 30):
            filtered.append(pt)

    return filtered

def group_cones(data):
    cones = []

    for i in range(1, len(data)-1):
        xdiff = data[i][0] - data[i-1][0]
        ydiff = data[i][1] - data[i-1][1]
        dist = m.sqrt(xdiff**2 + ydiff**2)

        # 250 mm = 25 cm which is approx width of base of cone
        if (dist > 250):
            cones.append(data[i])

    return cones

def get_cones(data):
    filtered = filter_data(data)
    cones = group_cones(filtered)
    return cones

