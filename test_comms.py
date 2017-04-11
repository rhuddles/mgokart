#!/usr/bin/env python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('35.2.135.78', 2000))
s.listen(1)
conn, addr = s.accept()
while 1:
	data = conn.recv(1024)
	if not data: break
	mtype = data[0]
	if mtype == 'S':
		speed = data[1:].split(',')[0]
		angle = data[1:].split(',')[1]
		print 'Speed=' + str(speed)
		print 'Angle=' + str(angle)
	elif mtype == 'C':
		print data[1:]
conn.close()