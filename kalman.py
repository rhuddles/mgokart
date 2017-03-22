#!/usr/bin/env python

from utility import dist

import math

LEFT_CONFS = []
RIGHT_CONFS = []

def predict(left_boundary, right_boundary, speed, steering, dt=.025):
    global LEFT_CONFS, RIGHT_CONFS
    predict_left = []
    predict_right = []

    mag = -1000 * speed * dt
    translate = [mag * math.cos(math.radians(90 - steering)),
            mag * math.sin(math.radians(90 - steering))]

    LEFT_CONFS.extend([0] * (len(left_boundary) - len(LEFT_CONFS)))
    RIGHT_CONFS.extend([0] * (len(right_boundary) - len(RIGHT_CONFS)))

    i = 0
    for cone in left_boundary:
        predict_left.append([a + b for a, b in zip(cone, translate)])
        LEFT_CONFS[i] = 1
        i += 1

    i = 0
    for cone in right_boundary:
        predict_right.append([a + b for a, b in zip(cone, translate)])
        RIGHT_CONFS[i] = 1
        i += 1

    return predict_left, predict_right

def update(new_left, new_right, old_left, old_right):
    global LEFT_CONFS, RIGHT_CONFS
    updated_left = []
    updated_right  = []

    if not old_left or not old_right:
        updated_left = new_left
        updated_right = new_right

    i = 0
    for old_cone in old_left:
        if dist(new_left[0], old_cone) < 500:
            updated_left += new_left
            LEFT_CONFS[i:] = [0]*len(LEFT_CONFS[i:])
            break
        else:
            updated_left.append(old_cone)
            i += 1

    i = 0
    for old_cone in old_right:
        if dist(new_right[0], old_cone) < 500:
            updated_right += new_right
            RIGHT_CONFS[i:] = [0]*len(RIGHT_CONFS[i:])
            break
        else:
            updated_right.append(old_cone)
            i += 1

    print 'LEFT_CONFS ', LEFT_CONFS
    print 'RIGHT_CONFS ', RIGHT_CONFS

    if sum(LEFT_CONFS) > 2:
        LEFT_CONFS = LEFT_CONFS[1:]
        updated_left = updated_left[1:]
    if sum(RIGHT_CONFS) > 2:
        RIGHT_CONFS = RIGHT_CONFS[1:]
        updated_right = updated_right[1:]

    return updated_left, updated_right

