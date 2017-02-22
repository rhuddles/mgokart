#!/usr/bin/env python

import csv
import math
import matplotlib.pyplot as plt
import os

def polar_to_cart(theta, dist):
    rads = math.radians(theta)
    return (dist * math.cos(rads), dist * math.sin(rads))

def get_world_points(data):
    points = []
    theta = -45.0
    step = 270.0 / len(data)

    for val in data:
        points.append(polar_to_cart(theta, float(val)))
        theta += step

    return points

def parse_csv_data(filename):
    frames = []

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None) # ignore header line

        for row in reader:
            row = row[1:-1:6]
            frames.append(get_world_points(row))

    return frames

if __name__ == '__main__':
    files = sorted(os.listdir('data'))
    for filename in files:
        frames = parse_csv_data('data/' + filename)
        frame = frames[0]
        x = [pt[0] for pt in frame]
        y = [pt[1] for pt in frame]
        plt.scatter(x, y, color='b', marker='.')
        plt.scatter(0, 0, color='g')
        plt.show()
