#!/usr/bin/env python

import csv
import math

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
    frames = parse_csv_data('data/wilson_center_wall.csv')
    print(frames)
