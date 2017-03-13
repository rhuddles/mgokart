#!/usr/bin/env python

from parse_data import *
from filter_data import *
from greedy_boundary_mapping import *
from utility import separate_xy

import matplotlib.pyplot as plt
import numpy as np
import time

def plot_line(coefs, min_x, max_x, style='-k'):
    f = np.poly1d(coefs)
    x = np.linspace(min_x, max_x, 20000)
    return plt.plot(x, f(x), style)

def predict_next_pos(speed, heading, dt):
    vel = np.array([math.cos(heading), math.sin(heading)])
    vel *= speed

    return vel * dt

def get_next_steering_angle(path_coefs, next_pos):
    path_xs = np.linspace(-5000, 5000, 10000)
    path = np.poly1d(path_coefs)

    path_pts = [(x, path(x)) for x in path_xs]

    chosen_pt = min(path_pts, key=lambda pt: dist(next_pos, pt))
    plt.scatter(chosen_pt[0], chosen_pt[1], color='red', marker='x')

    return angle_between((1, 0), chosen_pt)

def flip_xy(x, y):
    return (y, [-a for a in x])

def separate_and_flip(points):
    return flip_xy(*separate_xy(points))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    plt.ion()

    for filename in files:
        data = parse_csv_data(filename, fov=200)

        for frame in data:
            cones = get_cones(frame)
            cone_xs, cone_ys = separate_and_flip(cones)

            # Separate into boundaries
            left_boundary, right_boundary = create_boundary_lines(cones)

            # Fit left line
            left_xs, left_ys = separate_and_flip(left_boundary)
            left_coefs = np.polyfit(left_xs, left_ys, 2)

            # Fit right line
            right_xs, right_ys = separate_and_flip(right_boundary)
            right_coefs = np.polyfit(right_xs, right_ys, 2)

            # Calculate center line
            avg_coefs = np.add(left_coefs, right_coefs) / 2

            # make a decision for once in your life gavin
            next_pos = predict_next_pos(1000, 0, 0.3)
            angle = get_next_steering_angle(avg_coefs, next_pos)
            print('Gotta turn %f degrees in some direction' % math.degrees(angle))

            # plot just everything
            print(filename)
            blue = plt.scatter(cone_xs, cone_ys, color='blue', marker='^')
            orange, = plt.plot(left_xs, left_ys, color='orange')
            red, = plt.plot(right_xs, right_ys, color='red')

            dashed, = plot_line(left_coefs, min(left_xs), max(left_xs), '--k')
            plot_line(right_coefs, min(right_xs), max(right_xs), '--k')
            black, = plot_line(avg_coefs, min(left_xs + right_xs),
                    max(left_xs + right_xs))

            green = plt.scatter(0, 0, color='green')
            cyan = plt.scatter(next_pos[0], next_pos[1], color='cyan')

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
            plt.draw()
            plt.pause(0.00001)
            plt.gcf().clear()
