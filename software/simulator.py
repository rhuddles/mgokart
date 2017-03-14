import math
from operator import itemgetter
import sys
from tkFileDialog import askopenfile, asksaveasfile
from Tkinter import Tk

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import greedy2
import regression_steering as rs
import predictive_speed as ps


# Frames of reference:
# 
# GUI - The origin is in the upper left corner and refers to each pixel on the screen
#   x increases to the right to self.size().width()
#   y increases down to self.size().height()
# 
# Lidar - Vehicle is the origin. 1 pixel = 20 mm
#   x increases to the right of the vehicle and decreases to the left
#   y increases above the vehicle and decreases below

MM_PER_PIXEL = 20

"""
Converts cones in the GUIs frame of reference to cones in the lidar's frame of reference.
Returns only cones within the lidar's field of view. Sorts the cones by angle starting at -135 degrees
lidar_pos: the position of the lidar in the GUI frame of reference given as a tuple
gui_points: locations of cones in the GUI frame of reference given as a list of tuples
"""
def convertGUIToLidar(lidar_pos, gui_points):

    # Cones seen by lidar
    lidar_coords = []

    # Convert from gui frame to lidar frame
    for point in gui_points:
        x = (point[0] - lidar_pos[0])*MM_PER_PIXEL
        y = (lidar_pos[1] - point[1])*MM_PER_PIXEL

        # Convert points to polar form and filter
        dist = math.hypot(x,y)
        angle = math.degrees(math.atan2(x,y))
        if dist <= 10000 and angle > -135 and angle < 135:
            lidar_coords.append(((x,y), dist, angle, point))

    # Sort cones by angle
    return sorted(lidar_coords,key=itemgetter(2))   

class CourseMaker(QWidget):

    def __init__(self):
        super(CourseMaker, self).__init__()

        # Flags
        self.bm_on = False
        self.lk_on = False
        self.edits = False

        # Data
        self.gui_points = []
        self.lidar_points = []
        self.left_bound = []
        self.right_bound = []

        # Tmp
        self.speed = 0

        self.initUI()

    updated = pyqtSignal()

    def enableEdits(self, flag):
        self.edits = flag

        if not flag:
            self.lidar_points = convertGUIToLidar(self.lidar_pos, self.gui_points)

    def clearMap(self):
        self.bm_on = False
        self.lk_on = False
        self.gui_points = []
        self.update()

    def runBM(self):
        self.bm_on = True
        cones_list = []
        for point in self.lidar_points:
            cones_list.append(point[0])
        try:
            self.left_bound, self.right_bound = greedy2.create_boundary_lines(cones_list)
        except:
            print('Error Running boundary mapping')

        self.update()

    def runLK(self):
        self.lk_on = True
        self.steering = rs.boundaries_to_steering(list(self.left_bound), list(self.right_bound))
        self.speed = ps.get_next_speed(list(self.left_bound), list(self.right_bound))
        self.updated.emit()
        self.update()

    def stopBM(self):
        self.bm_on=False
        self.update()

    def stopLK(self):
        self.lk_on=False
        self.update()

    # Draws all selected points on map
    def paintEvent(self, event):

        # Get lidar position
        self.lidar_pos = (self.size().width()/2,4*self.size().height()/5)
        
        # Sizes
        cone_rad = 10
        car = 20
        lidar_range = 500

        # Begin painting
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)

        # Draw visible area
        paint.setBrush(Qt.green)
        paint.drawEllipse(QPoint(self.lidar_pos[0], self.lidar_pos[1]), lidar_range, lidar_range)

        # Draw Car
        fov = QPolygon()
        paint.setBrush(Qt.black)
        paint.drawRect(self.lidar_pos[0] - car/2, self.lidar_pos[1] - car/2, car, car)
        paint.setBrush(Qt.red)
        fov.append(QPoint(self.lidar_pos[0], self.lidar_pos[1]))
        fov.append(QPoint(self.lidar_pos[0]+(self.size().height() - self.lidar_pos[1]), self.size().height()))
        fov.append(QPoint(self.lidar_pos[0]-(self.size().height() - self.lidar_pos[1]), self.size().height()))
        paint.drawPolygon(fov)

        # Draw steering angle
        if self.lk_on:
            paint.setPen(Qt.black)
            paint.pen().setWidth(5)
            x = math.sin(math.radians(self.steering))*100
            y = math.cos(math.radians(self.steering))*100
            paint.drawLine(self.lidar_pos[0],self.lidar_pos[1],self.lidar_pos[0]+x,self.lidar_pos[1]-y)

        # Draw cones
        paint.setBrush(Qt.darkRed)
        for p in self.gui_points:
            paint.drawEllipse(QPoint(p[0],p[1]), cone_rad, cone_rad)

        # Draw boundary cones
        if self.bm_on:
            for p in self.lidar_points:
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
        if self.edits:
            p = QMouseEvent.pos()
            self.gui_points.append((p.x(),p.y()))
            self.update()

    def initUI(self):

        # Set background
        p = self.palette()
        p.setColor(QPalette.Background, Qt.white)
        self.setPalette(p)
        self.setAutoFillBackground(True)


class Simulator(QMainWindow):
    def __init__(self):
        super(Simulator, self).__init__()

        self.editFlag = False

        self.course = CourseMaker()
        self.course.updated.connect(self.updateStatus)
        self.initUI()

    def updateStatus(self):
        self.steering_value.setText(str(self.course.steering))
        self.speed_value.setText(str(self.course.speed))

    def runBoundaryMap(self):
        if self.course.bm_on:
            self.bm_button.setText('Run Boundary Mapping')
            self.course.stopBM()
        else:
            self.bm_button.setText('Clear Boundary Mapping')
            self.course.runBM()

    def runLaneKeeping(self):
        if self.course.lk_on:
            self.lk_button.setText('Run Lane Keeping')
            self.course.stopLK()
        else:
            self.lk_button.setText('Clear Lane Keeping')
            self.course.runLK()

    def editMap(self):
        if self.editFlag:
            self.editFlag = False
            self.edit_button.setText('Enable Map Editing')
        else:
            self.editFlag = True
            self.edit_button.setText('Disable Map Editing')

        self.course.enableEdits(self.editFlag)

    def runClear(self):
        self.bm_button.setText('Run Boundary Mapping')
        self.lk_button.setText('Run Lane Keeping')
        self.course.clearMap()

    def save(self):
        Tk().withdraw()
        file = asksaveasfile()
        for p in self.course.points:
            file.write(str(p[0])+' '+str(p[1]) + '\n')
        file.close()

    def load(self):
        Tk().withdraw()
        file = askopenfile()
        self.course.points = []
        for line in file:
            point = line.split()
            test = (int(point[0]),int(point[1]))
            self.course.points.append(test)
        file.close()
        self.course.enableEdits(False)
        self.course.update()

    def initUI(self):

        menu_label = QLabel("Simulator Operation Menu")

        ###--- Map related buttons ---###

        map_label = QLabel("Map Functions")

        self.edit_button = QPushButton('Enable Map Editing')
        clear_button = QPushButton('Clear Map')
        save_button = QPushButton('Save Map')
        load_button = QPushButton('Load Map')

        self.edit_button.clicked.connect(self.editMap)
        clear_button.clicked.connect(self.runClear)
        save_button.clicked.connect(self.save)
        load_button.clicked.connect(self.load)


        ###--- Algorithm related buttons ---###

        alg_label= QLabel("Algorithms")

        self.bm_button = QPushButton('Run Boundary Mapping')
        self.bm_button.clicked.connect(self.runBoundaryMap)

        self.lk_button = QPushButton('Run Lane Keeping')
        self.lk_button.clicked.connect(self.runLaneKeeping)


        ###--- Status related buttons ---###
        status_label = QLabel('Status')
        steering_label = QLabel('Steering Angle:')
        self.steering_value = QLabel('')
        speed_label = QLabel('Speed:')
        self.speed_value = QLabel('')


        ###--- Menu Layout ---###

        menuLayout = QVBoxLayout()
        menuLayout.setAlignment(Qt.AlignTop)
        menuLayout.addWidget(menu_label)
        menuLayout.addWidget(map_label)
        menuLayout.addWidget(self.edit_button)
        menuLayout.addWidget(clear_button)
        menuLayout.addWidget(save_button)
        menuLayout.addWidget(load_button)
        menuLayout.addWidget(alg_label)
        menuLayout.addWidget(self.bm_button)
        menuLayout.addWidget(self.lk_button)
        menuLayout.addWidget(status_label)
        menuLayout.addWidget(steering_label)
        menuLayout.addWidget(self.steering_value)
        menuLayout.addWidget(speed_label)
        menuLayout.addWidget(self.speed_value)

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