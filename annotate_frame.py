#!/usr/bin/env python

import sys

from filter_data import parse_csv_data
from utility import separate_xy, create_annotate_filename

try:
    from matplotlib import pyplot as plt
except:
    pass

REAL_CONES = []

def onclick_handler(event):
    print 'Adding cone: ({}, {})'.format(event.xdata, event.ydata)
    REAL_CONES.append((float(event.xdata), float(event.ydata)))

def register_click_handler():
    fig = plt.figure()
    fig.canvas.mpl_connect('button_press_event', onclick_handler)

def save_cones(filename, frame_number):
    save_file = create_annotate_filename(filename, frame_number)

    print 'Save file: {}'.format(save_file)
    print 'Saving cones: {}'.format(REAL_CONES)

    with open(save_file, "w") as outfile:
        for cone in REAL_CONES:
            outfile.write('{} {}\n'.format(cone[0], cone[1]))

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'Usage: ./{} <scan-filename> <frame-number>'.format(sys.argv[0])
        sys.exit()

    filename = sys.argv[1]
    frame_number = int(sys.argv[2])

    print 'Showing {} : {}'.format(filename, frame_number)

    register_click_handler()

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

    save_cones(filename, frame_number)
