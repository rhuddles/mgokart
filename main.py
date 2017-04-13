#!/usr/bin/env python

# from lidar_comms.takescan import enable_laser
from filter_data import get_cones
from finish_line import detect_finish_line
from boundary_mapping import create_boundary_lines, plot_boundaries
from kalman import predict, update
from me_comms import init_connection, receive_feedback
from parse_data import parse_csv_data
from predictive_speed import get_next_speed
from regression_steering import boundaries_to_steering
from utility import regression, separate_and_flip
from hokuyo import enable_laser

from datetime import datetime
import argparse
import math
import os
import sys
import serial

FOV = 200 # The LIDAR's real-world field of view

# Ports for socket comms with me's
ME_PORT = 8090

LAP_COUNT = 0 # Current lap

# Memory of left and right boundaries and their regressions
# Updated by set_boundaries() - do not set otherwise
LEFT_BOUNDARY = []
LEFT_COEFS = []

RIGHT_BOUNDARY = []
RIGHT_COEFS = []


# Should only be called with boundaries returned by kalman functions
def set_boundaries(left_boundary, right_boundary):
    global LEFT_BOUNDARY, LEFT_COEFS, RIGHT_BOUNDARY, RIGHT_COEFS
    LEFT_BOUNDARY = list(left_boundary)
    LEFT_COEFS = regression(left_boundary)
    RIGHT_BOUNDARY = list(right_boundary)
    RIGHT_COEFS = regression(right_boundary)

def predict_boundaries(curr_speed, curr_bearing):
    predicted_left, predicted_right = predict(LEFT_BOUNDARY, RIGHT_BOUNDARY,
            curr_speed, curr_bearing)

    if predicted_left and predicted_right:
        set_boundaries(predicted_left, predicted_right)

def predict_and_filter(frame, curr_speed, curr_bearing):
    predict_boundaries(curr_speed, curr_bearing)
    return get_cones(frame, LEFT_COEFS, RIGHT_COEFS)

def get_speed_steering(cones):
    global LAP_COUNT
    if detect_finish_line(cones):
        LAP_COUNT += 1

    left_boundary, right_boundary = create_boundary_lines(cones)
    left_boundary, right_boundary = update(left_boundary, right_boundary,
            LEFT_BOUNDARY, RIGHT_BOUNDARY)
    set_boundaries(left_boundary, right_boundary)

    speed = get_next_speed(LEFT_BOUNDARY, RIGHT_BOUNDARY, LAP_COUNT)

    bearing = boundaries_to_steering(LEFT_BOUNDARY, RIGHT_BOUNDARY)

    return speed, bearing

def get_and_send_setpoint(frame, curr_speed, curr_bearing, conn, verbose=False):
    cones = predict_and_filter(frame, curr_speed, curr_bearing)
    speed, bearing = get_speed_steering(cones)

    if verbose:
        print 'Speed:\t%05.1f' % speed
        print 'Bearing:\t%05.1f' % bearing

    if conn:
        conn.sendall('%05.1f,%05.1f' % (speed, bearing))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--connect', action='store_true')
    parser.add_argument('filename', nargs='?')
    args = parser.parse_args()

    if args.connect:
        print 'Trying to connect to socket on port %d' % ME_PORT
        conn = init_connection(ME_PORT)
    else:
        print 'Not trying to connect to a socket!'
        conn = None


    if args.filename:
        print 'Reading data from file: %s' % args.filename

        data = parse_csv_data(args.filename, FOV)

        for frame in data:
            if conn:
                curr_speed, curr_bearing = receive_feedback(conn)
            else:
                curr_speed, curr_bearing = 1.0, 0.0

            get_and_send_setpoint(frame, curr_speed, curr_bearing, conn, True)
    else:
        print 'Reading data from LIDAR'
        laser = enable_laser()

        while True:
            distances = laser.get_scan()
            frame = get_world_points(distances, FOV)

            if conn:
                curr_speed, curr_bearing = receive_feedback(conn)
            else:
                curr_speed, curr_bearing = 1.0, 0.0

            get_and_send_setpoint(frame, curr_speed, curr_bearing, conn, True)
