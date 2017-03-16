#!/usr/bin/env python

from utility import dist

import math

def predict(left_boundary, right_boundary, speed, steering, dt=.025):
    predict_left = []
    predict_right = []

    mag = -1000 * speed * dt
    translate = [mag * math.cos(math.radians(90 - steering)),
            mag * math.sin(math.radians(90 - steering))]

    for cone in left_boundary:
        predict_left.append([a + b for a, b in zip(cone, translate)])

    for cone in right_boundary:
        predict_right.append([a + b for a, b in zip(cone, translate)])

    return predict_left, predict_right

def update(new_left, new_right, old_left, old_right):
    updated_left = []
    updated_right  = []

    if not old_left or not old_right:
        updated_left = new_left
        updated_right = new_right

    for old_cone in old_left:
        if dist(new_left[0], old_cone) < 100:
            updated_left += new_left
            break
        else:
            updated_left.append(old_cone)

    for old_cone in old_right:
        if dist(new_right[0], old_cone) < 100:
            updated_right += new_right
            break
        else:
            updated_left.append(old_cone)

    return updated_left[-8:], updated_right[-8:]

