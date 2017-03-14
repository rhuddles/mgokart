#!/usr/bin/env python

# from lidar_comms/takescan import enable_laser
from parse_data import parse_csv_data
from filter_data import get_cones
from finish_line import detect_finish_line
from greedy_boundary_mapping import create_boundary_lines
from predictive_speed import get_next_speed
from regression_steering import boundaries_to_steering

import sys

FOV = 200

LAP_COUNT = 0

LEFT_BOUNDARY = []
RIGHT_BOUNDARY = []

LEFT_POLYS = []
RIGHT_POLYS = []

if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['data/' + path for path in sorted(os.listdir('data'))]

    # laser = enable_laser()

    for filename in files:
        # For LIDAR use
        # distances, timestamp = laser.get_scan()
        # frame = get_world_points(distances, FOV)

        frame = parse_csv_data(filename, FOV)[0]
        cones = get_cones(frame)

        if detect_finish_line(cones):
            LAP_COUNT += 1
            # TODO: Stop if 10...

        left_boundary, right_boundary = create_boundary_lines(cones)
        speed = get_next_speed(left_boundary, right_boundary)
        bearing = boundaries_to_steering(left_boundary, right_boundary)

        print 'Speed:', speed
        print 'Bearing:', bearing

        # TODO: Write to socket
