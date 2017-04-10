#!/usr/bin/env python

# from lidar_comms.takescan import enable_laser
from filter_data import get_cones
from finish_line import detect_finish_line
from boundary_mapping import create_boundary_lines, plot_boundaries
from kalman import predict, update
from me_comms import *
from parse_data import parse_csv_data
from predictive_speed import get_next_speed
from regression_steering import boundaries_to_steering
from utility import regression, separate_and_flip
from hokuyo import enable_laser

from datetime import datetime
import math
import os
import sys
import serial

FOV = 200 # The LIDAR's real-world field of view

# Ports for socket comms with me's
ME_PORT = 8090
MSG_LEN = 11

LAP_COUNT = 0 # Current lap

# Memory of left and right boundaries and their regressions
# Updated by set_boundaries() - do not set otherwise
LEFT_BOUNDARY = []
LEFT_COEFS = []

RIGHT_BOUNDARY = []
RIGHT_COEFS = []

def init_boundaries():
    pass

# Should only be called with boundaries returned by kalman functions
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
        files = ['lidar_data/' + path for path in sorted(os.listdir('lidar_data'))]

    # laser = enable_laser()
    init_boundaries()
    connection = init_connection(ME_PORT)

    for filename in files:
        # For LIDAR use
        # distances = laser.get_scan()
        # frame = get_world_points(distances, FOV)
        # --

        # curr_speed, curr_bearing = receive(conn, MSG_LEN)
        curr_speed, curr_bearing = 0, 0

        # For csv file use
        data = parse_csv_data(filename, FOV)
        print 'done parsing'
        # --

        for frame in data:

            start = datetime.now()
            checkpoint = datetime.now()
            # Predict new boundary locations
            predicted_left, predicted_right = predict(LEFT_BOUNDARY, RIGHT_BOUNDARY,
                    curr_speed, curr_bearing)
            if predicted_left and predicted_right:
                set_boundaries(predicted_left, predicted_right)

            print 'Prediction took %s seconds' % str(datetime.now() - checkpoint)
            checkpoint = datetime.now()

            lp, rp = LEFT_COEFS, RIGHT_COEFS
            # Filtering
            cones = get_cones(frame, LEFT_COEFS, RIGHT_COEFS)
#            plot_cones = list(cones)

            print 'Filtering took %s seconds' % str(datetime.now() - checkpoint)
            checkpoint = datetime.now()

            # Finish line detection
            if detect_finish_line(cones):
                LAP_COUNT += 1
                # TODO: Stop if 10...

            print 'Finish line took %s seconds' % str(datetime.now() - checkpoint)
            checkpoint = datetime.now()

            # Boundary mapping
            left_boundary, right_boundary = create_boundary_lines(cones)
            left_boundary, right_boundary = update(left_boundary, right_boundary,
                    LEFT_BOUNDARY, RIGHT_BOUNDARY)
            set_boundaries(left_boundary, right_boundary)

            print 'Boundary mapping took %s seconds' % str(datetime.now() - checkpoint)
            checkpoint = datetime.now()

            # Lane keeping (speed)
            speed, count_lap  = get_next_speed(LEFT_BOUNDARY, RIGHT_BOUNDARY)
            LAP_COUNT = LAP_COUNT + int(count_lap)

            print 'Speed took %s seconds' % str(datetime.now() - checkpoint)
            checkpoint = datetime.now()

            # Lane keeping (steering)
            bearing = boundaries_to_steering(LEFT_BOUNDARY, RIGHT_BOUNDARY)

            print 'Steering took %s seconds' % str(datetime.now() - checkpoint)

            print 'Took %s seconds' % str(datetime.now() - start)
#            # Plotting
#
#            # Plot cones and boundaries
#            plot = plot_boundaries(plot_cones, LEFT_BOUNDARY, RIGHT_BOUNDARY)
#
#            # Plot heading vector
#            vecx = 1000 * speed * math.sin(math.radians(bearing))
#            vecy = 1000 * speed * math.cos(math.radians(bearing))
#            plot.plot([0, vecx], [0, vecy], 'k', label='Trend Line')
#
#            # Plot reference vector
#            plot.plot([0, 0], [1000 * coord for coord in [0, 1]], '--g', label='Reference Line')
#
#            plot.legend(loc='upper left')
#
#            xmin, xmax = plot.xlim()
#            ymin, ymax = plot.ylim()
#            plot.text(xmax, ymax + 700, 'Speed: %5.2f m/s' % speed)
#            plot.text(xmax, ymax + 300, 'Bearing: %5.2f degrees' % bearing)
#            plot.draw()
#            plot.pause(0.00001)
#            plot.gcf().clear()

            # Write to socket
            print 'Speed:\t%05.1f' % speed
            print 'Bearing:\t%05.1f' % bearing
            send(connection, '%05.1f,%05.1f' % (speed, bearing))

