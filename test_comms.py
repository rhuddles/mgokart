#!/usr/bin/env python

import main
import me_comms

import threading
import ast

from datetime import datetime

ME_PORT = 8090
SIM_PORT = 2000

ME_MSG_LEN = 15

state_lock = threading.Lock()
CURR_SPEED, CURR_BEARING = 0.0, 0.0

def vehicle_update_listener(conn):
    global CURR_SPEED, CURR_BEARING
    while True:
        speed, steering = me_comms.receive(conn, ME_MSG_LEN)
        with state_lock:
	    CURR_SPEED, CURR_BEARING = speed, steering
        print 'FROM ME: {}, {}'.format(speed, steering)

if __name__ == '__main__':

    print 'Connecting to ME side...'
    me_conn = me_comms.init_connection(ME_PORT)
    print 'Connected'

    print 'Connecting to SIM side...'
    sim_conn = me_comms.init_connection(SIM_PORT)
    print 'Connected'

    vehicle_updates_thread = threading.Thread(target=vehicle_update_listener, args=(me_conn,))
    vehicle_updates_thread.daemon = True
    vehicle_updates_thread.start()

    motor_disable = False

    while True:

        # Get instructions from SIM
        data = sim_conn.recv(1024)
        mtype = data[0]

        calc_time = 0.0
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

            main.predict_boundaries(curr_speed, curr_bearing)
            calc_speed, calc_bearing = main.get_speed_steering(cones)

            calc_time = datetime.now() - start

        elif mtype == 'D':
            motor_disable = True

        elif mtype == 'E':
            motor_disable = False
        else:
            print 'Unknown message type'

        if motor_disable:
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
            str(main.LAP_COUNT) + ',' \
            str(calc_time.total_seconds()) + ',' \
            '|' + \
            str(main.LEFT_BOUNDARY) + \
            '|' + \
            str(main.RIGHT_BOUNDARY)\
        )

    me_conn.close()
    sim_conn.close()
