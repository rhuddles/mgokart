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
from tkFileDialog import askopenfile, asksaveasfile
from Tkinter import Tk

# QT5 Libraries
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# MGoKart Modules
import boundary_mapping as bm
import regression_steering as rs
import predictive_speed as ps

# Constants - TODO: Move these to either class privates or expose to user
MM_PER_PIXEL = 20 # Pixel to real world scaling
STEPPER_SLEW = (378/4) # Speed of the stepper motor in degrees/second
T = .25 # Simulation step size
LIDAR_FOV = 240 # Lidar's field of view in degrees
LIDAR_RANGE = 10000 # Lidar's filter range in millimeters
STEERING_RANGE = 45.0 # Maximum steering wheel angle
WHEEL_RANGE = 35.0 # Maximum wheel angle
VEHICLE_ACCELERATION = 5 # Max acceleration in m/s^2
VEHICLE_DECELERATION = 5 # Max deceleration in m/s^2


class CourseMaker(QWidget):

    def __init__(self):
        super(CourseMaker, self).__init__()

        # Flags
        self.editFlag = False
        self.sim_on = False

        # Input data
        self.gui_points = []

        # Algorithm params
        self.detected_cones = []
        self.left_bound = []
        self.right_bound = []
        self.target_steering = 0
        self.target_speed = 0

        # Vehicle params
        self.wheel_angle = 0
        self.steering = 0
        self.speed = 0

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
            x = (point[0] - self.lidar_pos[0])*MM_PER_PIXEL
            y = (self.lidar_pos[1] - point[1])*MM_PER_PIXEL
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
        print 'Detected Cones: ' + str(len(self.detected_cones))
        for point in self.detected_cones:
            cones_list.append(point[0])

        # Run boundary mapping algorithm
        try:
            self.left_bound, self.right_bound = bm.create_boundary_lines(cones_list)
            print 'Left Bound: ' + str(len(self.left_bound))
            print 'Right Bound: ' + str(len(self.right_bound))
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

    def moveVehicle(self):
        '''
        Transforms gui points into new positions based on vehicle parameters and step size
        '''

        # Cones in transformation
        coords = []

        # Convert from gui frame to lidar frame
        for point in self.gui_points:
            x = (point[0] - self.lidar_pos[0])*MM_PER_PIXEL
            y = (self.lidar_pos[1] - point[1])*MM_PER_PIXEL

            # Convert points to polar form and filter
            dist = math.hypot(x,y)
            angle = math.atan2(x,y)

            new_angle = angle - math.radians(self.steering)
            new_x = dist*math.sin(new_angle)
            new_y = dist*math.cos(new_angle) - self.speed*1000*T
            guiX = new_x/MM_PER_PIXEL + self.lidar_pos[0]
            guiY = self.lidar_pos[1] - new_y/MM_PER_PIXEL

            coords.append((guiX,guiY))

        self.gui_points = coords

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

    def stepSim(self):
        '''
        Simulates a single step, moving the vehicle and running algorithms on the new location
        '''

        # Simulate
        self.moveVehicle()
        self.updateActuators()
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

    def clearMap(self):
        '''
        Clears all input points from map. Editing must be enabled for this to work.
        '''
        if self.editFlag:
            self.gui_points = []
            self.detected_cones = []
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

        # Get lidar position
        self.lidar_pos = (self.size().width()/2,self.size().height()*4.0/5)

        # Sizes
        cone_rad = 250.0/MM_PER_PIXEL
        car = 20
        lidar_range = float(LIDAR_RANGE)/MM_PER_PIXEL
        blind_angle = (360 - LIDAR_FOV)/2
        dy = math.cos(math.radians(blind_angle))*LIDAR_RANGE/MM_PER_PIXEL
        dx = math.sin(math.radians(blind_angle))*LIDAR_RANGE/MM_PER_PIXEL

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
        x = math.sin(math.radians(self.steering))*self.target_speed*2000/MM_PER_PIXEL
        y = math.cos(math.radians(self.steering))*self.target_speed*2000/MM_PER_PIXEL
        paint.drawLine(self.lidar_pos[0],self.lidar_pos[1],self.lidar_pos[0]+x,self.lidar_pos[1]-y)

        # Draw target steering angle
        paint.setPen(Qt.red)
        paint.pen().setWidth(50)
        x = math.sin(math.radians(self.target_steering))*self.target_speed*1000/MM_PER_PIXEL
        y = math.cos(math.radians(self.target_steering))*self.target_speed*1000/MM_PER_PIXEL
        paint.drawLine(self.lidar_pos[0],self.lidar_pos[1],self.lidar_pos[0]+x,self.lidar_pos[1]-y)

        # Draw cones
        paint.setBrush(Qt.darkRed)
        for p in self.gui_points:
            paint.drawEllipse(QPoint(p[0],p[1]), cone_rad, cone_rad)

        # Give size hint if editing enabled
        if self.editFlag and len(self.gui_points):
            paint.setPen(Qt.darkBlue)
            paint.setBrush(Qt.transparent)
            paint.drawEllipse(QPoint(self.gui_points[-1][0],self.gui_points[-1][1]), 5000/MM_PER_PIXEL, 5000/MM_PER_PIXEL)

        # Draw boundary cones
        for p in self.detected_cones:
            paint.setBrush(Qt.black)

            paint.drawEllipse(QPoint(p[3][0],p[3][1]), cone_rad, cone_rad)



        # Draw boundary cones
        for p in self.detected_cones:
            if self.left_bound.count(p[0]):
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
            self.gui_points.append((p.x(),p.y()))
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

    def save(self):
        Tk().withdraw()
        file = asksaveasfile(initialdir = './courses')
        if not file: return
        for p in self.course.gui_points:
            file.write(str(p[0])+' '+str(p[1]) + '\n')
        file.close()

    def load(self):
        Tk().withdraw()
        file = askopenfile(initialdir = './courses')
        if not file: return
        self.course.gui_points = []
        for line in file:
            point = line.split()
            test = (int(float(point[0])),int(float(point[1])))
            self.course.gui_points.append(test)
        file.close()
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


    def initUI(self):

        menu_label = QLabel("Simulator Operation Menu")

        ###--- Map related buttons ---###

        map_label = QLabel("Map Functions")

        self.edit_button = QPushButton('Enable Map Editing')
        undo_button = QPushButton('Undo')
        clear_button = QPushButton('Clear Map')
        save_button = QPushButton('Save Map')
        load_button = QPushButton('Load Map')

        self.edit_button.clicked.connect(self.editMap)
        undo_button.clicked.connect(self.course.undoPlaceCone)
        clear_button.clicked.connect(self.runClear)
        save_button.clicked.connect(self.save)
        load_button.clicked.connect(self.load)

        ###--- Simulation related buttons ---###
        sim_label= QLabel('Simulation')

        self.step_button = QPushButton('Step Forward')
        self.run_button = QPushButton('Run Simulation')

        self.step_button.clicked.connect(self.course.stepSim)
        self.run_button.clicked.connect(self.runSim)

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
        menuLayout.addWidget(undo_button)
        menuLayout.addWidget(clear_button)
        menuLayout.addWidget(save_button)
        menuLayout.addWidget(load_button)
        # Simulation
        menuLayout.addWidget(sim_label)
        menuLayout.addWidget(self.step_button)
        menuLayout.addWidget(self.run_button)
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
