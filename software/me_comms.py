#!/usr/bin/env python

import socket

def init_listen_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(1)
    return sock

def get_speed_steering(sock, size):
        # assuming msg format is 'speed,bearing'
        conn, addr = sock.accept()
        msg = conn.recv(size)
        speed, bearing = msg.split(',')
        return float(speed), float(bearing)

def send_socket(port, msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', port))

    # Checking to make sure right number of bytes sent
    while sock.send(msg) != len(msg):
        pass

