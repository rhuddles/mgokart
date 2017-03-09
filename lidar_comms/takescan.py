#!/usr/bin/env python

import hokuyo as lidar
import serial
import serial.tools.list_ports as list_ports

port = serial.Serial(list_ports.comports()[0][0])
port.isOpen()


laser = lidar.Hokuyo(port, model_name = 'UTM-30LX')

print 'ENABLING SCANNING'
laser.enable_scanning(True)

laser.laser_off()
laser.laser_on()

print 'GETTING SCAN'
distances, timestamp = laser.get_scan()

print distances
print timestamp

port.close()
