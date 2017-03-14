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

def predict_next_pos(speed, dt):
    return np.array([speed * dt, 0])

def get_closest_point_on_curve(path, off_curve_pt, min_x=0, max_x=5000):
    xs = np.linspace(min_x, max_x, max_x + min_x)
    curve_pts = [(x, path(x)) for x in xs]

    return min(curve_pts, key=lambda pt: dist(off_curve_pt, pt))

def get_waypoint(path, speed):
    # in 3 seconds we want to be back on path
    off_path_pt = [speed * 3, 0]

    # get closest point on curve to the chosen off path point
    on_path_pt = get_closest_point_on_curve(path, off_path_pt)
    return on_path_pt

def get_steering_command(path, speed, dt):
    next_pos = predict_next_pos(speed, dt)

    # choose waypoint along path that we eventually want to get to
    waypoint = get_waypoint(path, speed)

    # TODO needs a sign
    return angle_between((1, 0), waypoint)


    return angle_between((1, 0), chosen_pt)

def flip_xy(x, y):
    return (y, [-a for a in x])

def separate_and_flip(points):
    return flip_xy(*separate_xy(points))

def boundaries_to_steering(left, right, speed=1000, dt=0.3):
    # Fit left line
    left_xs, left_ys = separate_and_flip(left)
    left_coefs = np.polyfit(left_xs, left_ys, 2)

    # Fit right line
    right_xs, right_ys = separate_and_flip(right)
    right_coefs = np.polyfit(right_xs, right_ys, 2)

    # Calculate center line
    path_coefs = np.add(left_coefs, right_coefs) / 2
    path = np.poly1d(path_coefs)

    # make a decision for once in your life gavin
    next_pos = predict_next_pos(speed, dt)
    x = math.degrees(get_steering_command(path, speed, dt))
    print x
    return x

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

            # TODO make nice
            # Fit left line
            left_xs, left_ys = separate_and_flip(left_boundary)
            left_coefs = np.polyfit(left_xs, left_ys, 2)

            # Fit right line
            right_xs, right_ys = separate_and_flip(right_boundary)
            right_coefs = np.polyfit(right_xs, right_ys, 2)

            # Calculate center line
            path_coefs = np.add(left_coefs, right_coefs) / 2
            path = np.poly1d(path_coefs)

            # make a decision for once in your life gavin
            speed = 1000
            dt = 0.3
            next_pos = predict_next_pos(speed, dt)
            angle = get_steering_command(path, speed, dt)
            print('Gotta turn %f degrees in some direction' % math.degrees(angle))

            # plot just everything
            #print(filename)
            blue = plt.scatter(cone_xs, cone_ys, color='blue', marker='^')
            orange, = plt.plot(left_xs, left_ys, color='orange')
            red, = plt.plot(right_xs, right_ys, color='red')

            dashed, = plot_line(left_coefs, min(left_xs), max(left_xs), '--k')
            plot_line(right_coefs, min(right_xs), max(right_xs), '--k')
            black, = plot_line(path_coefs, min(left_xs + right_xs),
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
