#!/usr/bin/env python

import socket

def init_connection(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    conn, addr = sock.accept()
    return conn

def receive(conn, size, verbose=False):
    msg = ''
    recvd = 0
    while recvd < size:
        data = conn.recv(size - recvd)
        recvd += len(data)
        msg += data

    # assuming msg format is 'speed,bearing'
    speed, bearing = msg.split(',')

    if verbose:
        print 'speed:', speed
        print 'Bearing:', bearing

    return float(speed), float(bearing)

def send(conn, msg):
    # Checking to make sure right number of bytes sent
    sent = 0
    print msg
    while sent < len(msg):
        sent += conn.send(msg[sent:])

