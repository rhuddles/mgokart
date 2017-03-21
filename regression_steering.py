#!/usr/bin/env python

from parse_data import *
from filter_data import *
from finish_line import detect_finish_line
from greedy_boundary_mapping import *
from utility import *

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
    xs = np.linspace(min_x, max_x, abs(max_x) + abs(min_x))
    curve_pts = [(x, path(x)) for x in xs]

    return min(curve_pts, key=lambda pt: dist(off_curve_pt, pt))

def get_waypoint(path, speed):
    # in 3 seconds we want to be back on path
    off_path_pt = [speed * 3, 0]

    # get closest point on curve to the chosen off path point
    on_path_pt = get_closest_point_on_curve(path, off_path_pt)
    return on_path_pt

def dist_from_center(path):
    pos = [0., 0.]
    center = get_closest_point_on_curve(path, pos, min_x=-5000, max_x=5000)
    return dist(pos, center)

def get_steering_command(path, speed, dt, plot=False):
    # tune distance of this point, further = less steep turning
    next_pos = predict_next_pos(speed, dt * 7)

    # vector from vehicle state to reference state
    error = get_closest_point_on_curve(path, next_pos, min_x=-5000, max_x=5000)

    # coefficient of quadratic path
    A = error[1] / error[0]**2

    # plot quadratic path
    if plot:
        xs = np.linspace(0, 2000, 2000)
        ys = [A * (x**2) for x in xs]
        plt.plot(xs, ys, 'b')

    # calculate desired vehicle speed and angular velocity
    new_speed = math.sqrt(speed**2 * (1 + (4 * A**2 * (speed * dt))))
    w = (2 * A * speed**3) / (new_speed**2)

    # yea sure
    wheelbase = 942

    # steering angle = (angular velocity * wheelbase) / velocity
    theta = (w * wheelbase) / speed

    # we say positive angles are clockwise rotations
    theta *= -1

    return math.degrees(theta)

def boundaries_to_steering(left, right, speed=1000, dt=0.3):
    # Fit left line
    left_coefs = regression(left)

    # Fit right line
    right_coefs = regression(right)

    # Calculate center line
    path_coefs = np.add(left_coefs, right_coefs) / 2
    path = np.poly1d(path_coefs)

    # make a decision for once in your life gavin
    return get_steering_command(path, speed, dt)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['lidar_data/' + path for path in sorted(os.listdir('lidar_data'))]

    plt.ion()

    for filename in files:
        print(filename)

        data = parse_csv_data(filename, fov=200)[300:]

        for frame in data:
            cones = get_cones(frame)
            detect_finish_line(cones)
            cone_xs, cone_ys = separate_and_flip(cones)

            # Separate into boundaries
            left_boundary, right_boundary = create_boundary_lines(cones)

            # TODO make nice
            # Fit left line
            left_coefs = regression(left_boundary)

            # Fit right line
            right_coefs = regression(right_boundary)

            # Calculate center line
            path_coefs = np.add(left_coefs, right_coefs) / 2
            path = np.poly1d(path_coefs)

            # yea sure
            speed = 1000
            dt = 0.3

            # make a decision for once in your life gavin
            angle = get_steering_command(path, speed, dt, plot=True)
            print('Turn %f degrees' % angle)

            # plot just everything
            left_xs, left_ys = separate_and_flip(left_boundary)
            right_xs, right_ys = separate_and_flip(right_boundary)
            blue = plt.scatter(cone_xs, cone_ys, color='blue', marker='^')
            orange, = plt.plot(left_xs, left_ys, color='orange')
            red, = plt.plot(right_xs, right_ys, color='red')

            dashed, = plot_line(left_coefs, min(left_xs), max(left_xs), '--k')
            plot_line(right_coefs, min(right_xs), max(right_xs), '--k')
            black, = plot_line(path_coefs, min(left_xs + right_xs),
                    max(left_xs + right_xs))

            green = plt.scatter(0, 0, color='green')

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
