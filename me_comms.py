#!/usr/bin/env python

import socket

FEEDBACK_MSG_LEN = 15

def init_connection(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    conn, addr = sock.accept()
    return conn

def receive_feedback(conn, verbose=False):
    msg = ''
    recvd = 0
    while recvd < FEEDBACK_MSG_LEN:
        data = conn.recv(size - recvd)
        recvd += len(data)
        msg += data

    # Feedback: speed,bearing
    speed, bearing = msg.split(',')

    if verbose:
        print 'Speed:', speed
        print 'Bearing:', bearing

    return float(speed), float(bearing)
