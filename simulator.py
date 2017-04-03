#!/usr/bin/env python
'''
MGoKart Racing Simulator
Bobby Huddleston - rhuddles@umich.edu

This simulator is used for testing algorithms and visualizing their outputs. It can be used to create test courses for the go-kart as well as visualize the detected course and analysis from real world data.

Frames of reference:

GUI - The origin is in the upper left corner and refers to each pixel on the screen
  x increases to the right to self.size().width()
  y increases down to self.size().height()

Lidar - Vehicle is the origin. 1 pixel = 20 mm
  x increases to the right of the vehicle and decreases to the left
  y increases above the vehicle and decreases below
'''

# Python Libraries
import math
import os
import sys
import threading
import time
import traceback
from operator import itemgetter
from tkFileDialog import askopenfile, asksaveasfile, askopenfilename
from Tkinter import Tk

# QT5 Libraries
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# MGoKart Modules
import parse_data as pd
import filter_data as fd
import finish_line as fl
import boundary_mapping as bm
import regression_steering as rs
import predictive_speed as ps

# Constants - TODO: Move these to either class privates or expose to user
scaling_factor = 20.0 # Pixel to real world scaling
STEPPER_SLEW = (378/4) # Speed of the stepper motor in degrees/second
T = .25 # Simulation step size
LIDAR_FOV = 240 # Lidar's field of view in degrees
LIDAR_RANGE = 10000 # Lidar's filter range in millimeters
STEERING_RANGE = 45.0 # Maximum steering wheel angle
WHEEL_RANGE = 35.0 # Maximum wheel angle
VEHICLE_ACCELERATION = 5 # Max acceleration in m/s^2
VEHICLE_DECELERATION = 5 # Max deceleration in m/s^2
L = 942.0 #Wheel base in mm

# Save file contents:
# Cone x,y points
# Delimiter line
# Center x,y points
SAVE_FILE_DELIMITER_LINE = '-----\n'


def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

class CourseMaker(QWidget):

    def __init__(self):
        super(CourseMaker, self).__init__()

        global scaling_factor

        # Flags
        self.editFlag = False
        self.sim_on = False
        self.mark_cone = True

        # Course center points
        self.center_points = []

        # Input data
        self.gui_points = []

        # Algorithm params
        self.detected_cones = []
        self.finish_cones = []
        self.left_bound = []
        self.right_bound = []
        self.target_steering = 0
        self.target_speed = 0

        # Vehicle params
        self.vehicle_angle = 0
        self.wheel_angle = 0
        self.steering = 0
        self.speed = 0

         # Get lidar position
        res = QApplication.desktop().screenGeometry();
        scaling_factor = 64000.0/res.width()

        self.lidar_pos = ((res.width()- 370)/2,res.height()*3.0/5)
        self.initUI()

    updated = pyqtSignal()


    ###--- Algorithmic Methods ---###

    def lidarScan(self):
        """
        Converts cones in the GUIs frame of reference to cones in the lidar's frame of reference and gets those in the lidar's field of view
        Sets detected_cones with only cones within the lidar's field of view. Sorts the cones by angle starting at -135 degrees.
        """

        # Get cones seen by lidar
        lidar_coords = []
        for point in self.gui_points:
            # Convert from gui frame to lidar frame
            x = (point[0] - self.lidar_pos[0])*scaling_factor
            y = (self.lidar_pos[1] - point[1])*scaling_factor
            # Convert points to polar form and filter
            dist = math.hypot(x,y)
            angle = math.degrees(math.atan2(x,y))
            if dist <= LIDAR_RANGE and abs(angle) < LIDAR_FOV/2:
                lidar_coords.append(((x,y), dist, angle, point))

        # Sort cones by angle
        self.detected_cones = sorted(lidar_coords,key=itemgetter(2))

    def boundaryMapping(self):
        '''
        Runs the boundary mapping algorithm. Sets left and right bound lists.
        '''
        # Error Checking
        if len(self.detected_cones) < 2:
            print('Not enough cones detected! Implement short term memory if you want this to work')
            self.left_bound = []
            self.right_bound = []
            return

        # Format cones list for algorithm
        cones_list = []
        for point in self.detected_cones:
            cones_list.append(point[0])


        finish_line = fl.detect_finish_line(cones_list)
        if len(finish_line) == 2:
            self.finish_cones = finish_line[0] + finish_line[1]
        elif len(finish_line) == 1:
            self.finish_cones = finish_line[0]

        # Run boundary mapping algorithms
        bm_on = True
        try:
            while bm_on:
                self.right_bound, self.left_bound = bm.create_boundary_lines(list(cones_list))

                if (len(self.left_bound) + len(self.right_bound) + 2) < len(cones_list):
                    if len(self.left_bound) < len(self.right_bound):
                        cones_list.pop(0)
                    else:
                        cones_list.pop()
                else:
                    bm_on = False

        except Exception, e:
            print('Error running boundary mapping!')
            traceback.print_exc()

        # TODO: move to execution thread
        self.update()

    def laneKeeping(self):
        '''
        Runs the lane keeping algorithm. Sets target steering angle and vehicle speed.
        '''

        # Error checking
        if not len(self.left_bound) or not len(self.right_bound):
            print('Two boundaries not detected! Implement short term memory if you want this to work')
            self.target_steering = 0
            self.target_speed = 0
            return

        # Run algorithm
        try:
            self.target_steering = rs.boundaries_to_steering(list(self.left_bound), list(self.right_bound))

            # Limit steering angle and print error
            if self.target_steering > STEERING_RANGE:
                print('Steering angle outside of bounds: ' +  str(self.target_steering))
                self.target_steering = STEERING_RANGE
            elif self.target_steering < -STEERING_RANGE:
                print('Steering angle outside of bounds: ' +  str(self.target_steering))
                self.target_steering = -STEERING_RANGE
        except Exception, e:
            print('Error running lane keeping (steering)!')
            traceback.print_exc()
            self.target_steering = 0

        try:
            self.target_speed = ps.get_next_speed(list(self.left_bound), list(self.right_bound))
        except Exception, e:
            print('Error running lane keeping (speed)!')
            traceback.print_exc()
            self.target_speed = 0

    def movePoints(self, points):
        # Cones in transformation
        coords = []

        # Convert from gui frame to lidar frame
        for point in points:
            x = (point[0] - self.lidar_pos[0])*scaling_factor
            y = (self.lidar_pos[1] - point[1])*scaling_factor

            # Convert points to polar form and filter
            dist = math.hypot(x,y)
            angle = math.atan2(x,y)

            new_angle = angle - math.radians(self.vehicle_angle)
            new_x = dist*math.sin(new_angle)
            new_y = dist*math.cos(new_angle) - self.speed*1000*T
            guiX = new_x/scaling_factor + self.lidar_pos[0]
            guiY = self.lidar_pos[1] - new_y/scaling_factor

            coords.append((guiX,guiY))

        return coords

    def moveVehicle(self):
        '''
        Transforms gui points into new positions based on vehicle parameters and step size
        '''
        self.gui_points = self.movePoints(self.gui_points)
        self.center_points = self.movePoints(self.center_points)

    def updateActuators(self):
        '''
        Updates vehicle actuators. Used to model mechanical lag in the system.
        '''

        # Updates steering angle and wheel angle
        if abs(self.target_steering - self.steering) < (STEPPER_SLEW*T):
            self.steering = self.target_steering
        elif self.target_steering - self.steering < 0:
            self.steering = self.target_steering + (STEPPER_SLEW*T)
        else:
            self.steering = self.target_steering - (STEPPER_SLEW*T)
        self.wheel_angle = self.steering*WHEEL_RANGE/STEERING_RANGE

        # Update vehicle speed
        if self.speed > self.target_speed:
            if self.speed - (VEHICLE_DECELERATION*T) > self.target_speed:
                self.speed = self.speed - (VEHICLE_DECELERATION*T)
            else:
                self.speed = self.target_speed
        else:
            if self.speed + (VEHICLE_ACCELERATION*T) < self.target_speed:
                self.speed = self.speed + (VEHICLE_ACCELERATION*T)
            else:
                self.speed = self.target_speed

        # TODO: Add vehicle position and angle change
        dtheta = 1000.0*self.speed*self.wheel_angle*T/L
        self.vehicle_angle = dtheta

    def stepSim(self):
        '''
        Simulates a single step, moving the vehicle and running algorithms on the new location
        '''

        # Simulate
        self.updateActuators()
        self.moveVehicle()
        self.lidarScan()
        self.boundaryMapping()
        self.laneKeeping()

        # Update
        self.update()
        self.updated.emit()

    def runSim(self):
        '''
        Run simulation continuously until stopped
        '''
        while self.sim_on:
            self.stepSim()


    ###--- Operational Methods ---###

    def enableEdits(self, flag):
        '''
        Enables or disables map editing mode based on flag
        '''
        self.editFlag = flag
        self.update()

    def setMarkCone(self, flag):
        self.mark_cone = flag
        self.update()

    def clearMap(self):
        '''
        Clears all input points from map. Editing must be enabled for this to work.
        '''
        if self.editFlag:
            self.gui_points = []
            self.center_points = []
            self.detected_cones = []
            self.right_bound = []
            self.left_bound = []
            self.steering = 0
            self.speed = 0
            self.update()

    def undoPlaceCone(self):
        '''
        Clears the last cone to be placed
        '''
        if len(self.gui_points) and self.editFlag:
            self.gui_points.pop()
            self.update()

    def paintEvent(self, event):
        '''
        Draws all elements on the course. Called by update
        '''

        # Sizes
        cone_rad = 250.0/scaling_factor
        car = 20
        lidar_range = float(LIDAR_RANGE)/scaling_factor
        blind_angle = (360 - LIDAR_FOV)/2
        dy = math.cos(math.radians(blind_angle))*LIDAR_RANGE/scaling_factor
        dx = math.sin(math.radians(blind_angle))*LIDAR_RANGE/scaling_factor

        # Begin painting
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)

        # Draw visible area
        paint.setBrush(Qt.green)
        paint.drawEllipse(QPoint(self.lidar_pos[0], self.lidar_pos[1]), lidar_range, lidar_range)

        # Draw blind spot
        paint.setBrush(Qt.red)
        rectangle = QRect(self.lidar_pos[0] - lidar_range,self.lidar_pos[1] - lidar_range, 2*lidar_range, 2*lidar_range)
        paint.drawPie(rectangle, ((LIDAR_FOV/2)+90) * 16, (360-LIDAR_FOV) * 16);

        # Draw Car
        paint.setBrush(Qt.black)
        paint.drawRect(self.lidar_pos[0] - car/2, self.lidar_pos[1] - car/2, car, car)

        # Draw steering angle
        paint.setPen(Qt.black)
        paint.pen().setWidth(50)
        x = math.sin(math.radians(self.steering))*self.target_speed*2000/scaling_factor
        y = math.cos(math.radians(self.steering))*self.target_speed*2000/scaling_factor
        paint.drawLine(self.lidar_pos[0],self.lidar_pos[1],self.lidar_pos[0]+x,self.lidar_pos[1]-y)

        # Draw target steering angle
        paint.setPen(Qt.red)
        paint.pen().setWidth(50)
        x = math.sin(math.radians(self.target_steering))*self.target_speed*1000/scaling_factor
        y = math.cos(math.radians(self.target_steering))*self.target_speed*1000/scaling_factor
        paint.drawLine(self.lidar_pos[0],self.lidar_pos[1],self.lidar_pos[0]+x,self.lidar_pos[1]-y)

        # Draw cones
        paint.setBrush(Qt.darkRed)
        for p in self.gui_points:
            paint.drawEllipse(QPoint(p[0],p[1]), cone_rad, cone_rad)

        # Draw center points
        paint.setBrush(Qt.blue)
        paint.setPen(Qt.blue)
        for p in self.center_points:
            paint.drawEllipse(QPoint(p[0], p[1]), cone_rad/2., cone_rad/2.)

        # Give size hint if editing enabled
        if self.editFlag and len(self.gui_points):
            paint.setPen(Qt.darkBlue)
            paint.setBrush(Qt.transparent)
            paint.drawEllipse(QPoint(self.gui_points[-1][0],self.gui_points[-1][1]), 5000/scaling_factor, 5000/scaling_factor)

        # Draw boundary cones
        for p in self.detected_cones:
            paint.setBrush(Qt.black)

            paint.drawEllipse(QPoint(p[3][0],p[3][1]), cone_rad, cone_rad)

        # Draw boundary cones
        for p in self.detected_cones:
            if self.finish_cones.count(p[0]):
                paint.setBrush(Qt.darkMagenta)
            elif self.left_bound.count(p[0]):
                paint.setBrush(Qt.blue)
            elif self.right_bound.count(p[0]):
                paint.setBrush(Qt.darkCyan)
            else:
                paint.setBrush(Qt.darkRed)

            paint.drawEllipse(QPoint(p[3][0],p[3][1]), cone_rad, cone_rad)


        paint.end()

    # Gets new cones
    def mouseReleaseEvent(self, QMouseEvent):
        if self.editFlag:
            p = QMouseEvent.pos()

            if self.mark_cone:
                self.gui_points.append((p.x(),p.y()))
            else:
                self.center_points.append((p.x(), p.y()))

            self.update()

    def scalePoints(self, points, old_factor, scaling_factor):
        new_points = []
        for p in points:
            px = float(p[0]-self.lidar_pos[0])*old_factor/scaling_factor + self.lidar_pos[0]
            py = float(p[1]-self.lidar_pos[1])*old_factor/scaling_factor + self.lidar_pos[1]
            new_points.append((px,py))
        return new_points

    def wheelEvent(self, event):
        global scaling_factor
        old_factor = scaling_factor
        scaling_factor -= event.angleDelta().y()/120.0;
        if scaling_factor < 1:
            scaling_factor = 1

        self.gui_points = self.scalePoints(self.gui_points, old_factor, scaling_factor)
        self.center_points = self.scalePoints(self.center_points, old_factor, scaling_factor)

        self.update()

    def initUI(self):
        '''
        Initializes UI for the widget
        '''

        # Set background
        p = self.palette()
        p.setColor(QPalette.Background, Qt.white)
        self.setPalette(p)
        self.setAutoFillBackground(True)


class Simulator(QMainWindow):
    def __init__(self):
        super(Simulator, self).__init__()

        self.editFlag = False
        self.sim_on = False
        self.lidar_frame = 0
        self.lidar_data = []

        self.course = CourseMaker()
        self.course.updated.connect(self.updateStatus)

        if os.path.exists('courses/lastCourse'):
            file = open('courses/lastCourse', 'r')
            self.course.gui_points = []
            for line in file:
                point = line.split()
                test = (int(float(point[0])),int(float(point[1])))
                self.course.gui_points.append(test)
            file.close()
            self.course.update()

        self.initUI()

    def updateStatus(self):
        self.steering_value.setText(str(self.course.steering))
        self.target_speed_value.setText(str(self.course.speed))

    def editMap(self):
        if self.editFlag:
            self.editFlag = False
            self.edit_button.setText('Enable Map Editing')
        else:
            self.editFlag = True
            self.edit_button.setText('Disable Map Editing')

        self.course.enableEdits(self.editFlag)

    def runClear(self):
        self.course.clearMap()

    def savePoints(self, points, file):
        for p in points:
            x_coord = float(p[0] - self.course.lidar_pos[0])*scaling_factor
            y_coord = float(p[1] - self.course.lidar_pos[1])*scaling_factor
            file.write(str(x_coord)+' '+str(y_coord) + '\n')

    def save(self):
        Tk().withdraw()
        file = asksaveasfile(initialdir = './courses')
        if not file: return
        self.savePoints(self.course.gui_points, file)
        file.write(SAVE_FILE_DELIMITER_LINE)
        self.savePoints(self.course.center_points, file)
        file.close()

    def loadPoints(self, file):
        points = []
        for line in file:
            if line == SAVE_FILE_DELIMITER_LINE:
                break
            point = line.split()
            x_coord = int(float(point[0])/scaling_factor + self.course.lidar_pos[0])
            y_coord = int(float(point[1])/scaling_factor + self.course.lidar_pos[1])
            points.append((x_coord, y_coord))
        return points

    def load(self):
        Tk().withdraw()
        file = askopenfile(initialdir = './courses')
        if not file: return
        self.course.enableEdits(True)
        self.course.clearMap()
        self.course.enableEdits(False)
        self.course.gui_points = self.loadPoints(file)
        self.course.center_points = self.loadPoints(file)
        file.close()
        self.course.update()

    def loadFrame(self):
        self.course.enableEdits(True)
        self.course.clearMap()
        self.course.enableEdits(False)
        cones = fd.get_cones(self.lidar_data[self.next_frame_button.value()], None, None)
        for point in cones:
            x_coord = int(float(point[0])/scaling_factor + self.course.lidar_pos[0])
            y_coord = int(-float(point[1])/scaling_factor + self.course.lidar_pos[1])
            self.course.gui_points.append((x_coord, y_coord))
        self.course.update()

    def loadLidarTestCourse(self):
        Tk().withdraw()
        filename = askopenfilename(initialdir = './lidar_data')
        if not filename: return
        self.lidar_data = pd.parse_csv_data(filename)
        self.next_frame_button.setMaximum(len(self.lidar_data) - 1)
        global_cones_list = []
        global_cones_list.append((0,0))
        prev_cones_list = []

        # Get data from all frames
        for frame in self.lidar_data:

            # Reset current cones
            current_cones_list = []

            # Run filtering algorithm. TODO: Add short term memory
            cones = fd.get_cones(frame, None, None)

            # Get matches
            for pc in prev_cones_list:
                for nc in cones:

                    # Cone is already known
                    if dist(pc[1],nc) < 150:
                        if pc[2] < 0:
                            current_cones_list.append((pc[0],nc,pc[2] + 1))
                        else:
                            current_cones_list.append((pc[0],nc,pc[2]))
                        cones.remove(nc)
                        break;

            # Add non-matched cones
            for nc in cones:
                current_cones_list.append((nc,nc,-50))

            # Find Rererence cone
            ref_cone = ((0,0),(0,0),0)
            no_ref = False
            if len(global_cones_list) < 2:
                no_ref = True
            else:
                for cc in current_cones_list:
                    if cc[2] > 0:
                        ref_cone = cc
                        break

            for cc in current_cones_list:
                if cc[2] == 0:
                    # Error but whatever
                    if ref_cone == ((0,0),(0,0),0) and not no_ref:
                        print "Failed to find a refrence cone!!!!"
                    dx = cc[0][0] - ref_cone[1][0]
                    dy = cc[0][1] - ref_cone[1][1]
                    x= global_cones_list[ref_cone[2]][0] + dx
                    y= global_cones_list[ref_cone[2]][1] + dy
                    current_cones_list.remove(cc)
                    new_cc = (cc[0],cc[1], len(global_cones_list))
                    current_cones_list.append(new_cc)
                    global_cones_list.append((x,y))

            # Save list
            prev_cones_list = current_cones_list

        self.course.enableEdits(True)
        self.course.clearMap()
        self.course.enableEdits(False)
        for point in global_cones_list:
            x_coord = int(float(point[0])/scaling_factor + self.course.lidar_pos[0])
            y_coord = int(-float(point[1])/scaling_factor + self.course.lidar_pos[1])
            self.course.gui_points.append((x_coord, y_coord))
        self.course.update()

    def closeEvent(self, event):
        file = open('courses/lastCourse', 'w')
        if file == '': return
        for p in self.course.gui_points:
            file.write(str(p[0])+' '+str(p[1]) + '\n')
        file.close()

        if self.sim_on:
            self.course.sim_on = False
            self.sim_thread.join(0)

    def runSim(self):
        if self.sim_on:
            self.run_button.setText('Run Simulation')
            self.course.sim_on = False
            self.sim_thread.join(0)
            self.sim_on = False
        else:
            self.course.sim_on = True
            self.run_button.setText('Stop Simulation')
            self.sim_thread = threading.Thread(target=self.course.runSim)
            self.sim_thread.start()
            self.sim_on = True

    def setMarkCone(self):
        self.mark_cone = True
        self.course.setMarkCone(self.mark_cone)

    def setMarkCenter(self):
        self.mark_cone = False
        self.course.setMarkCone(self.mark_cone)


    def initUI(self):

        menu_label = QLabel("Simulator Operation Menu")

        ###--- Map related buttons ---###

        map_label = QLabel("Map Functions")

        self.edit_button = QPushButton('Enable Map Editing')

        self.click_for_cone_radio = QRadioButton('Mark Cone')
        self.click_for_cone_radio.setChecked(True)
        self.click_for_center_radio = QRadioButton('Mark Center')
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.click_for_cone_radio)
        self.radio_group.addButton(self.click_for_center_radio)

        undo_button = QPushButton('Undo')
        clear_button = QPushButton('Clear Map')
        save_button = QPushButton('Save Map')
        load_button = QPushButton('Load Map')
        load_lidar_button = QPushButton('Load Lidar')

        self.edit_button.clicked.connect(self.editMap)
        self.click_for_cone_radio.clicked.connect(self.setMarkCone)
        self.click_for_center_radio.clicked.connect(self.setMarkCenter)
        undo_button.clicked.connect(self.course.undoPlaceCone)
        clear_button.clicked.connect(self.runClear)
        save_button.clicked.connect(self.save)
        load_button.clicked.connect(self.load)
        load_lidar_button.clicked.connect(self.loadLidarTestCourse)

        ###--- Simulation related buttons ---###
        sim_label= QLabel('Simulation')

        self.step_button = QPushButton('Step Forward')
        self.run_button = QPushButton('Run Simulation')
        next_scan = QLabel('Lidar Frame:')
        self.next_frame_button = QSpinBox()
        self.next_frame_button.setMaximum(10000)
        self.next_frame_button.setSingleStep(10)

        self.step_button.clicked.connect(self.course.stepSim)
        self.run_button.clicked.connect(self.runSim)
        self.next_frame_button.valueChanged.connect(self.loadFrame)

        ###--- Status related buttons ---###
        status_label = QLabel('Status')
        steering_label = QLabel('Steering Angle (degrees):')
        self.steering_value = QLabel('0')
        speed_label = QLabel('Speed (m/s):')
        self.target_speed_value = QLabel('0')

        ###--- Menu Layout ---###

        menuLayout = QVBoxLayout()
        menuLayout.setAlignment(Qt.AlignTop)
        menuLayout.addWidget(menu_label)
        # Map
        menuLayout.addWidget(map_label)
        menuLayout.addWidget(self.edit_button)
        menuLayout.addWidget(self.click_for_cone_radio)
        menuLayout.addWidget(self.click_for_center_radio)
        menuLayout.addWidget(undo_button)
        menuLayout.addWidget(clear_button)
        menuLayout.addWidget(save_button)
        menuLayout.addWidget(load_button)
        menuLayout.addWidget(load_lidar_button)
        # Simulation
        menuLayout.addWidget(sim_label)
        menuLayout.addWidget(self.step_button)
        menuLayout.addWidget(self.run_button)
        menuLayout.addWidget(next_scan)
        menuLayout.addWidget(self.next_frame_button)
        # Status
        menuLayout.addWidget(status_label)
        menuLayout.addWidget(steering_label)
        menuLayout.addWidget(self.steering_value)
        menuLayout.addWidget(speed_label)
        menuLayout.addWidget(self.target_speed_value)

        menuWidget = QWidget()
        menuWidget.setLayout(menuLayout)

        ###--- Main Layout ---###

        vLine = QFrame()
        vLine.setFrameStyle(QFrame.VLine)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.course,3)
        mainLayout.addWidget(vLine)
        mainLayout.addWidget(menuWidget)

        main_widget = QWidget(self)
        main_widget.setLayout(mainLayout)

        self.setCentralWidget(main_widget)
        self.setWindowTitle('MGoKart Racing Simulator')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.showMaximized()

def main():

    app = QApplication(sys.argv)
    ex = Simulator()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
