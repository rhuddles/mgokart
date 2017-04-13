#!/usr/bin/env python

import main
from me_comms import init_connection, receive_feedback

import threading
import ast

from datetime import datetime, timedelta

ME_PORT = 8090
SIM_PORT = 2000

state_lock = threading.Lock()
CURR_SPEED, CURR_BEARING = 0.0, 0.0

def vehicle_update_listener(conn):
    global CURR_SPEED, CURR_BEARING
    while True:
        speed, steering = receive_feedback(conn)
        with state_lock:
	    CURR_SPEED, CURR_BEARING = speed, steering
        #print 'FROM ME: {}, {}'.format(speed, steering)

if __name__ == '__main__':

    print 'Connecting to ME side...'
    me_conn = init_connection(ME_PORT)
    print 'Connected'

    print 'Connecting to SIM side...'
    sim_conn = init_connection(SIM_PORT)
    print 'Connected'

    vehicle_updates_thread = threading.Thread(target=vehicle_update_listener, args=(me_conn,))
    vehicle_updates_thread.daemon = True
    vehicle_updates_thread.start()

    motor_disable = False

    calc_time = timedelta(seconds=.025) # LIDAR Speed

    while True:

        try:
            # Get instructions from SIM
            data = sim_conn.recv(1024)
            if len(data) == 0:
                break

            mtype = data[0]

            calc_speed, calc_bearing = 0.0, 0.0

            # Received Setpoint
            if mtype == 'S':
                calc_speed = int(data[1:].split(',')[0])
                calc_bearing = int(data[1:].split(',')[1])
                print 'Setpoint Speed: ' + str(calc_speed)
                print 'Setpoint Bearing: ' + str(calc_bearing)

            # Received Cones
            elif mtype == 'C':
                with state_lock:
                    curr_speed, curr_bearing = CURR_SPEED, CURR_BEARING

                cones = ast.literal_eval(data[1:])

                start = datetime.now()

                #main.predict_boundaries(curr_speed, curr_bearing, calc_time.total_seconds())
                calc_speed, calc_bearing = main.get_speed_steering(cones)

                calc_time = datetime.now() - start

            elif mtype == 'D':
                motor_disable = True

            elif mtype == 'E':
                motor_disable = False
            else:
                print 'Unknown message type'

            if motor_disable:
                with state_lock:
                    CURR_SPEED = calc_speed
                calc_speed = 0

            # Send to ME's every time
            print 'TO ME:  {}, {}'.format(calc_speed, calc_bearing)
            me_conn.sendall('%05.1f,%05.1f' % (calc_speed, calc_bearing))

            with state_lock:
                curr_speed, curr_bearing = CURR_SPEED, CURR_BEARING

            # Send to SIM every time
            print 'TO SIM: {}, {}, {}, {}, {}, {}'.format(curr_speed, curr_bearing, calc_speed, calc_bearing,\
                main.LAP_COUNT, calc_time.total_seconds())

            sim_conn.sendall(\
                str(curr_speed) + ',' + str(curr_bearing) + ',' + \
                str(calc_speed) + ',' + str(calc_bearing) + ',' + \
                str(main.LAP_COUNT) + ',' + \
                str(calc_time.total_seconds()) + ',' \
                '|' + \
                str(main.LEFT_BOUNDARY) + \
                '|' + \
                str(main.RIGHT_BOUNDARY)\
            )
        except Exception as e:
            print e
            break

    me_conn.close()
    sim_conn.close()
