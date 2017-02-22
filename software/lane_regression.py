#!/usr/bin/env python

from parse_data import *
from filter_data import *
from greedy import *

import matplotlib.pyplot as plt
import numpy as np

filename = 'data/lot_6_right.csv'
frames = parse_csv_data(filename)
cones = get_cones(frames[0])

left_boundary, right_boundary = create_boundary_lines(cones)

def separate_xy(points):
    return ([point[1] for point in points],
            [-point[0] for point in points])

# plot left boundary
left_xs, left_ys = separate_xy(left_boundary)
plt.scatter(left_xs, left_ys, color='orange', marker='^')
plt.plot(left_xs, left_ys, color='orange')

# plot right boundary
right_xs, right_ys = separate_xy(right_boundary)
plt.scatter(right_xs, right_ys, color='red', marker='^')
plt.plot(right_xs, right_ys, color='red')

def plot_line(coefs, min_x, max_x):
    f = np.poly1d(coefs)
    x = np.linspace(min_x, max_x, 20000)
    plt.plot(x, f(x), '--k')

# fit left line
left_coefs = np.polyfit(left_xs, left_ys, 2)
plot_line(left_coefs, min(left_xs), max(left_xs))

# fit right line
right_coefs = np.polyfit(right_xs, right_ys, 2)
plot_line(right_coefs, min(right_xs), max(right_xs))

# calculate center line
avg_coefs = np.add(left_coefs, right_coefs) / 2
plot_line(avg_coefs, min(left_xs + right_xs), max(left_xs + right_xs))

def predict_next_pos(speed, heading, dt):
    vel = np.array([math.cos(heading), math.sin(heading)])
    vel *= speed

    return vel * dt

next_pos = predict_next_pos(1000, 0, 0.3)

plt.scatter(0, 0, color='g')
plt.scatter(next_pos[0], next_pos[1], color='r')

plt.show()
