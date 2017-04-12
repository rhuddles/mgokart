#!/usr/bin/env python

import main
import me_comms

import threading
import ast

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
        print speed, steering

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

    while True:

        # Get instructions from SIM
        data = sim_conn.recv(1024)
        mtype = data[0]

        speed, bearing = 0.0, 0.0

        # Received Setpoint
        if mtype == 'S':
            speed = int(data[1:].split(',')[0])
            bearing = int(data[1:].split(',')[1])
            print 'Setpoint Speed: ' + str(speed)
            print 'Setpoint Bearing: ' + str(bearing)

        # Received Cones
        elif mtype == 'C':
            with state_lock:
                curr_speed, curr_bearing = CURR_SPEED, CURR_BEARING

            main.predict_boundaries(curr_speed, curr_bearing)
            cones = ast.literal_eval(data[1:])
            speed, bearing = main.get_speed_steering(cones)
            print 'Calc Speed: ' + str(speed)
            print 'Calc Bearing: ' + str(bearing)

        # Send to ME's every time
        me_comms.send(me_conn, '%05.1f,%05.1f' % (speed, bearing))

        with state_lock:
            curr_speed, curr_bearing = CURR_SPEED, CURR_BEARING
        me_comms.send(sim_conn, str(curr_speed) + ',' + str(curr_bearing) + ',')

    me_conn.close()
    sim_conn.close()
