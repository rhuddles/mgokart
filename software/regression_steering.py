#!/usr/bin/env python

from parse_data import *
from filter_data import *
from greedy_boundary_mapping import *
from utility import separate_xy

import matplotlib.pyplot as plt
import numpy as np

def plot_line(coefs, min_x, max_x, style='-k'):
    f = np.poly1d(coefs)
    x = np.linspace(min_x, max_x, 20000)
    return plt.plot(x, f(x), style)

filename = 'data/grass_sharp_right.csv'
frame = parse_csv_data(filename)[0]
cones = get_cones(frame)

# Plot cones
cone_xs, cone_ys = separate_xy(cones)
blue = plt.scatter(cone_xs, cone_ys, color='blue', marker='^')

left_boundary, right_boundary = create_boundary_lines(cones)

# Plot left boundary
left_xs, left_ys = separate_xy(left_boundary)
orange, = plt.plot(left_xs, left_ys, color='orange')

# Plot right boundary
right_xs, right_ys = separate_xy(right_boundary)
red, = plt.plot(right_xs, right_ys, color='red')

# Fit left line
left_coefs = np.polyfit(left_xs, left_ys, 2)
dashed, = plot_line(left_coefs, min(left_xs), max(left_xs), '--k')

# Fit right line
right_coefs = np.polyfit(right_xs, right_ys, 2)
plot_line(right_coefs, min(right_xs), max(right_xs), '--k')

# Calculate center line
avg_coefs = np.add(left_coefs, right_coefs) / 2
#black, = plot_line(avg_coefs, min(left_xs + right_xs), max(left_xs + right_xs))
black, = plot_line(avg_coefs, 0, max(left_xs + right_xs))

def predict_next_pos(speed, heading, dt):
    vel = np.array([math.cos(heading), math.sin(heading)])
    vel *= speed

    return vel * dt

next_pos = predict_next_pos(1000, 0, 0.3)

green = plt.scatter(0, 0, color='green')
#cyan = plt.scatter(next_pos[0], next_pos[1], color='cyan')

# Make plot look nice for report
plt.xlabel('Distance in millimeters')
plt.ylabel('Distance in millimeters')

plt.legend(
    (orange, red, dashed, black, blue, green),
    ('Left Boundary', 'Right Boundary', 'Regression Line', 'Trend Line', 'Detected Cone', 'Vehicle Position'),
    loc='upper left'
)

plt.axis('equal')
plt.axis([-6000, 10000, -5000, 10000])
plt.title('Regression Steering')
plt.show()
