#!/usr/bin/env python

import socket

def init_connection(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(1)
    conn, addr = sock.accept()
    return conn

def receive(conn, size):
        # assuming msg format is 'speed,bearing'
        msg = conn.recv(size)
        print 'msg:', msg
        speed, bearing = msg.split(',')
        print 'speed:', speed
        print 'bearing:', bearing
        return float(speed), float(bearing)

def send(conn, msg):
    # Checking to make sure right number of bytes sent
    while conn.send(msg) != len(msg):
        pass

