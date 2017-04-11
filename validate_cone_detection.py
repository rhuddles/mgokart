#!/usr/bin/env python

from boundary_mapping import create_boundary_lines
from filter_data import get_cones, parse_csv_data
from finish_line import detect_finish_line
from kalman import predict, update
from utility import dist, regression, separate_xy

try:
    from matplotlib import pyplot as plt
except:
    pass

LEFT_BOUNDARY = []
LEFT_POLYS = []

RIGHT_BOUNDARY = []
RIGHT_POLYS = []

CURR_SPEED = 0.0
CURR_BEARING = 0.0

def update_boundaries(frame):
    # Filter Data
    cones = get_cones(frame, LEFT_POLYS, RIGHT_POLYS)

    #plot_frame(frame, cones)

    # Predict Boundaries
    predicted_left, predicted_right = predict(LEFT_BOUNDARY, RIGHT_BOUNDARY,
            CURR_SPEED, CURR_BEARING)
    if predicted_left and predicted_right:
        set_boundaries(predicted_left, predicted_right)

    # Detect Finish Line
    detect_finish_line(cones)

    # Create Boundary Lines
    left_boundary, right_boundary = create_boundary_lines(cones)
    left_boundary, right_boundary = update(left_boundary, right_boundary,
            LEFT_BOUNDARY, RIGHT_BOUNDARY)
    set_boundaries(left_boundary, right_boundary)

def set_boundaries(left_boundary, right_boundary):
    global LEFT_BOUNDARY, LEFT_COEFS, RIGHT_BOUNDARY, RIGHT_COEFS
    LEFT_BOUNDARY = list(left_boundary)
    LEFT_COEFS = regression(left_boundary)
    RIGHT_BOUNDARY = list(right_boundary)
    RIGHT_COEFS = regression(right_boundary)

def plot_frame(frame, cones):
    # Plot raw data
    xs, ys = separate_xy(frame)
    red = plt.scatter(xs, ys, marker='x', color='red')

    # Plot grouped cones
    xs, ys = separate_xy(cones)
    blue = plt.scatter(xs, ys, marker='^', color='blue')

    green = plt.scatter(0, 0, color='green')

    # Make plot look nice for report
    plt.axis('equal')

    plt.xlabel('Distance in millimeters')
    plt.ylabel('Distance in millimeters')

    plt.legend(
        (red, blue, green),
        ('Filtered Data Point', 'Detected Cone', 'Vehicle Position'),
        loc='upper left'
    )

    plt.title('Distance and Clustering Filtering')
    plt.show()

def create_annotate_filename(filename, number):
    base, _ = filename.split('.')
    return '{}_{}'.format(base, str(number))

def read_annotate_file(filename):
    real_cones = []
    for line in open(filename):
        cone_x, cone_y = line.strip().split(' ')
        real_cones.append((float(cone_x), float(cone_y)))
    return real_cones

def check_close(cone, real_cones):
    for real_cone in real_cones:
        if dist(cone, real_cone) < 250: # 25cm
            print 'Found {} matches real {}'.format(cone, real_cone)
            return True

    print 'Found {} doesn\'t match'.format(cone)
    return False

def validate_scan(frame, annotate_file):
    found_cones = get_cones(frame, LEFT_POLYS, RIGHT_POLYS)
    real_cones = read_annotate_file(annotate_file)

    print 'Found cones [{}]: {}'.format(len(found_cones), found_cones)
    print 'Real cones [{}]: {}'.format(len(real_cones), real_cones)
    print
    
    correct = 0
    total = len(real_cones)

    for cone in found_cones:
        if check_close(cone, real_cones):
            correct += 1

    print
    print 'Scan: {}'.format(annotate_file)
    print 'Correct: {}'.format(correct)
    print 'Total: {}'.format(total)
    print 'Percent: {}%'.format(int(float(correct) / float(total) * 100))
    print

if __name__ == '__main__':
    filename = 'lidar_data/5_so_fast.csv'
    data = parse_csv_data(filename, fov=200)

    # Set up boundaries and coefficients
    update_boundaries(data[0])

    # Starting with second frame
    for i in range(1, len(data)):
        validate_scan(data[i], create_annotate_filename(filename, i))

        # Refresh boundaries and coefficients
        update_boundaries(data[i])

        break # FIXME
