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

from datetime import datetime
import ast
import math
import os
import sys
import threading

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

state_lock = threading.Lock()
CURR_SPEED, CURR_BEARING = 0.0, 0.0

def init_boundaries():
	pass

# Should only be called with boundaries returned by kalman functions
def set_boundaries(left_boundary, right_boundary):
	global LEFT_BOUNDARY, LEFT_COEFS, RIGHT_BOUNDARY, RIGHT_COEFS
	LEFT_BOUNDARY = list(left_boundary)
	LEFT_COEFS = regression(left_boundary)
	RIGHT_BOUNDARY = list(right_boundary)
	RIGHT_COEFS = regression(right_boundary)

def vehicle_update_listener(conn):
    global CURR_SPEED, CURR_BEARING
    while True:
	speed, steering = receive(conn, 15)
	with state_lock:
	    CURR_SPEED, CURR_BEARING = speed, steering
        print CURR_SPEED, CURR_BEARING

if __name__ == '__main__':

	init_boundaries()
	connection = init_connection(ME_PORT)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('35.2.200.236', 2000))
	s.listen(1)
	sim, addr = s.accept()
	speed = 0
	bearing = 0

	vehicle_updates_thread = threading.Thread(target=vehicle_update_listener, args=(connection,))
	vehicle_updates_thread.daemon = True
	vehicle_updates_thread.start()

	while True:

		data = sim.recv(1024)
		if not data: break
		mtype = data[0]		
				
				# Recieved Setpoint
		if mtype == 'S':
			speed = int(data[1:].split(',')[0])
			bearing = int(data[1:].split(',')[1])
			print 'Setpoint Speed: ' + str(speed)
			print 'Setpoint Bearing: ' + str(bearing)

		# Recieved Cones
		elif mtype == 'C':

			with state_lock:
			    curr_speed, curr_bearing = CURR_SPEED, CURR_BEARING

			# Predict new boundary locations
			predicted_left, predicted_right = predict(LEFT_BOUNDARY, RIGHT_BOUNDARY,
					curr_speed, curr_bearing)
			if predicted_left and predicted_right:
				set_boundaries(predicted_left, predicted_right)

			lp, rp = LEFT_COEFS, RIGHT_COEFS

			# Get cones
			cones = ast.literal_eval(data[1:])
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
			speed  = get_next_speed(LEFT_BOUNDARY, RIGHT_BOUNDARY,LAP_COUNT)
			# LAP_COUNT = LAP_COUNT + int(count_lap)

			# Lane keeping (steering)
			bearing = boundaries_to_steering(LEFT_BOUNDARY, RIGHT_BOUNDARY)

			# Write to socket
			print 'HITL Bearing:\t%05.1f' % bearing

		send(connection, '%05.1f,%05.1f' % (speed, bearing))

		with state_lock:
		    curr_speed, curr_bearing = CURR_SPEED, CURR_BEARING
		sim.send(str(curr_speed) + ',' + str(curr_bearing) + ',')

	sim.close()
