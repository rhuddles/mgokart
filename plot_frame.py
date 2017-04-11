#!/usr/bin/env python

import sys

from filter_data import parse_csv_data
from utility import separate_xy

try:
    from matplotlib import pyplot as plt
except:
    pass

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'Usage: ./{} <scan-filename> <frame-number>'.format(sys.argv[0])
        sys.exit()

    filename = sys.argv[1]
    frame_number = int(sys.argv[2])

    print 'Showing {} : {}'.format(filename, frame_number)

    # Filter the LIDAR capture specified
    data = parse_csv_data(filename)

    # Select frame specified
    frame = data[frame_number]

    # Plot raw data
    xs, ys = separate_xy(frame)
    red = plt.scatter(xs, ys, marker='x', color='red')

    # Make plot look nice for report
    plt.axis('equal')

    plt.xlabel('Distance in millimeters')
    plt.ylabel('Distance in millimeters')

    plt.legend(
        (red,),
        ('Data Point',),
        loc='upper left'
    )

    plt.title(filename + ' : ' + str(frame_number))
    plt.show()
