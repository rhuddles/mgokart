#!/usr/bin/env python

from hokuyo import *
from me_comms import *
from parse_data import get_world_points

from datetime import datetime
import os
import signal
import sys
import threading

DEFAULT_PORT = 8090
LOG_DIRECTORY = 'logs/'
DEFAULT_VEHICLE_LOG = 'vehicle.log'
DEFAULT_LIDAR_LOG = 'lidar.log'

MESSAGE_LENGTH = 16 - 1
LIDAR_FOV = 200

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


def get_timestamp():
    return datetime.now().strftime(TIMESTAMP_FORMAT)

def parse_point(pt):
    pt = pt.split(',')
    return float(pt[0]), float(pt[1])

# Vehicle state log message parsing
def parse_vehicle_log_msg(msg):
    timestamp, speed, steering = msg.split('|')
    timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)

    return timestamp, float(speed), float(steering)

# LIDAR log message parsing
def parse_lidar_log_msg(msg):
    timestamp, msg = msg.split('|')
    timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)

    points = msg.split(' ')
    points = [parse_point(pt) for pt in points]

    return timestamp, points

# Generator that takes a list of (x,y) points and yields a string for each
# point, with x and y separated by a comma
def points_to_string(points):
    for point in points:
        yield '%f,%f' % (point[0], point[1])

# Log a vehicle state update
def log_vehicle_state(logfile, speed, steering):
    logfile.write('%s|%s|%s\n' % (get_timestamp(), speed, steering))

# Log a LIDAR update
def log_lidar(logfile, points):
    # [(1, 2), (3, 4)] -> "1.0,2.0 3.0,4.0"
    data_str = ' '.join(points_to_string(points))
    logfile.write('%s|%s\n' % (get_timestamp(), data_str))


# Vehicle state updates listener thread
def vehicle_state_updates(log_filename, conn):
    with open(log_filename, 'w') as log:
        while True:
            speed, steering = receive(conn, MESSAGE_LENGTH)
            log_vehicle_state(log, speed, steering)

# LIDAR updates listener thread
def lidar_updates(log_filename, lidar):
    with open(log_filename, 'w') as log:
        while True:
            distances = lidar.get_scan()
            print distances
            points = get_world_points(distances, LIDAR_FOV)
            log_lidar(log, points)


# Usage: ./data_logger.py [log_name [port]]
# Generates 2 log files: log_name_vehicle.log and log_name_lidar.log
if __name__ == '__main__':
    port = DEFAULT_PORT
    vehicle_log = LOG_DIRECTORY + DEFAULT_VEHICLE_LOG
    lidar_log = LOG_DIRECTORY + DEFAULT_LIDAR_LOG

    if len(sys.argv) > 1:
        # log file: 'logs/name_vehicle.log'
        name = sys.argv[1]
        vehicle_log = '%s%s_%s' % (LOG_DIRECTORY, name, DEFAULT_VEHICLE_LOG)
        lidar_log = '%s%s_%s' % (LOG_DIRECTORY, name, DEFAULT_LIDAR_LOG)
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    if not os.path.isdir(LOG_DIRECTORY):
        os.mkdir(LOG_DIRECTORY)

    lidar = enable_laser()
#    lidar = None
    conn = init_connection(port)

    # Start listener threads
    t1 = threading.Thread(target=vehicle_state_updates, args=(vehicle_log, conn))
    t2 = threading.Thread(target=lidar_updates, args=(lidar_log, lidar))

    # Only want main thread to control program lifetime so Ctrl-C works
    t1.daemon = True
    t2.daemon = True

    t1.start()
    t2.start()

    # Sleep until it gets a signal so Ctrl-C works
    signal.pause()
