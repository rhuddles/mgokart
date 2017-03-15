#!/usr/bin/env python

# from lidar_comms.takescan import enable_laser
from filter_data import get_cones
from finish_line import detect_finish_line
from greedy_boundary_mapping import create_boundary_lines
from kalman import predict, update
from parse_data import parse_csv_data
from predictive_speed import get_next_speed
from regression_steering import boundaries_to_steering
from utility import regression

import os
import sys

FOV = 200 # The LIDAR's real-world field of view

LAP_COUNT = 0 # Current lap

# Memory of left and right boundaries and their regressions
# Updated by set_boundaries() - do not set otherwise
LEFT_BOUNDARY = []
LEFT_COEFS = []

RIGHT_BOUNDARY = []
RIGHT_COEFS = []

def init_boundaries():
    pass

def set_boundaries(left_boundary, right_boundary):
    global LEFT_BOUNDARY, LEFT_COEFS, RIGHT_BOUNDARY, RIGHT_COEFS
    LEFT_BOUNDARY = list(left_boundary)
    LEFT_COEFS = regression(left_boundary)
    RIGHT_BOUNDARY = list(right_boundary)
    RIGHT_COEFS = regression(right_boundary)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    # laser = enable_laser()
    init_boundaries()

    for filename in files:
        # For LIDAR use
        # distances, timestamp = laser.get_scan()
        # frame = get_world_points(distances, FOV)
        # --

        # TODO: get speed and steering from ME's
        curr_speed = 5 # m/s
        curr_bearing = 0 # degrees

        # For csv file use
        frame = parse_csv_data(filename, FOV)[0]
        # --

        # Predict new boundary locations
        # predicted_left, predicted_right = predict(LEFT_BOUNDARY, RIGHT_BOUNDARY,
        #         curr_speed, curr_bearing)
        # set_boundaries(predicted_left, predicted_right)

        # Filtering
        cones = get_cones(frame, LEFT_COEFS, RIGHT_COEFS)

        # Finish line detection
        if detect_finish_line(cones):
            LAP_COUNT += 1
            # TODO: Stop if 10...

        # Boundary mapping
        left_boundary, right_boundary = create_boundary_lines(cones)
        left_boundary, right_boundary = update(left_boundary, right_boundary,
                LEFT_BOUNDARY, RIGHT_BOUNDARY)
        set_boundaries(left_boundary, right_boundary)

        # Lane keeping (speed)
        speed = get_next_speed(LEFT_BOUNDARY, RIGHT_BOUNDARY)

        # Lane keeping (steering)
        bearing = boundaries_to_steering(LEFT_BOUNDARY, RIGHT_BOUNDARY)

        print 'Speed:', speed
        print 'Bearing:', bearing

        # TODO: Write to socket
