import math
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit, QLabel
from numpy.matrixlib.defmatrix import matrix
from pyqtgraph.Qt import QtGui
import sys
from math import cos, pi, sin, sqrt

# workloud distributed equally
# auth: josha benker & erik blank


# main class with ui for recognizing gesture
class GestureRecognizer(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Recognizer")
        self.curr_gesture = ""
        self.gestures = []
        self.gestures_dict = {}
        self._init_ui()
        self.setMinimumSize(800, 800)

    def _init_ui(self):
        # init layouts
        self.main_layout = QtGui.QVBoxLayout()
        self.gesture_text_layout = QtGui.QGridLayout()
        self.button_layout = QtGui.QGridLayout()
        self.recognize_layout = QtGui.QGridLayout()
        self.draw_widget = QDrawWidget(100, 100)

        # init line edit
        self.label = QLabel()
        self.label.setText("Gesture: ")
        self.line_edit = QLineEdit()
        self.add_button = QtGui.QPushButton("Add")
        self.gesture_text_layout.addWidget(self.label, 0, 0)
        self.gesture_text_layout.addWidget(self.line_edit, 0, 1)
        self.gesture_text_layout.addWidget(self.add_button, 0, 2)
        self.add_button.clicked.connect(self.on_add_btn_clicked)

        # init list
        self.gesture_list = QtGui.QComboBox()

        # init recognizer ui
        self.reco_button = QtGui.QPushButton("Recognize")
        self.reco_label = QLabel()
        self.reco_label.setText("Last recognized gesture: ")
        self.result_label = QLabel("___")
        self.recognize_layout.addWidget(self.reco_button, 0, 1)
        self.recognize_layout.addWidget(self.reco_label, 0, 0)
        self.recognize_layout.addWidget(self.result_label)
        self.reco_button.clicked.connect(self.on_reco_btn_clicked)

        # add layouts to main layout
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.gesture_text_layout)
        self.main_layout.addWidget(self.gesture_list)
        self.main_layout.addWidget(self.draw_widget)
        self.main_layout.addLayout(self.recognize_layout)

        self.setLayout(self.main_layout)

    def on_add_btn_clicked(self):
        points = self.draw_widget.getPoints()
        gesture = self.line_edit.text()
        if gesture != "" and len(points) != 0:
            self.curr_gesture = self.line_edit.text()
            if self.curr_gesture not in self.gestures:
                self.gestures.append(self.curr_gesture)
                self.gesture_list.clear()
                self.gesture_list.addItems(self.gestures)
            self.gestures_dict[self.curr_gesture] = points

    def on_reco_btn_clicked(self):
        # add result
        if len(self.gestures) == 0:
            self.result_label.setText("No gestures initialized")
        elif len(self.draw_widget.getPoints()) == 0:
            self.result_label.setText("First draw something")
        else:
            sample = self.draw_widget.getPoints()
            reco = Recognizer()
            score = reco.calculate_similarity(sample, self.gestures_dict[self.curr_gesture])
            output = self.curr_gesture
            for gesture in self.gestures_dict:
                template = self.gestures_dict[gesture]
                curr_score = reco.calculate_similarity(sample, template)
                if curr_score < score:
                    score = curr_score
                    output = gesture
            self.result_label.setText(output)


class QDrawWidget(QtWidgets.QWidget):
    def __init__(self, width=800, height=800):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.grid = True
        self.points = []
        # only get events when button is pressed
        self.setMouseTracking(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Drawable')
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
            try:
                recognizer = Recognizer()
                self.points = recognizer.custom_filter(self.points)
            except NameError:
                pass
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update()

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.points.append((ev.x(), ev.y()))
            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.drawPolyline(self.poly(self.points))

        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
        if self.grid:
            qp.setPen(QtGui.QColor(255, 100, 100, 20))  # semi-transparent

            for x in range(0, self.width(), 20):
                qp.drawLine(x, 0, x, self.height())

            for y in range(0, self.height(), 20):
                qp.drawLine(0, y, self.width(), y)

        qp.end()

    def getPoints(self):
        return self.points


# code is mostly from "Computational Geometry for Gesture Recognition.ipynb"
class Recognizer:
    def distance(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return sqrt(dx * dx + dy * dy)

    def total_length(self, point_list):
        p1 = point_list[0]
        length = 0.0

        for i in range(1, len(point_list)):
            length += self.distance(p1, point_list[i])
            p1 = point_list[i]

        return length

    def resample(self, point_list, step_count=64):
        # resample the given stroke's list of points
        # represent the stroke with the amount of step_count points

        # save here the resampled points
        newpoints = []

        # the sum of the distances of all points along the originally drawn stroke
        length = self.total_length(point_list)

        # the distance the resampled points have to each other
        stepsize = length / (step_count - 1)

        # current position along the strong in regard of step_size (see below)
        curpos = 0

        # add the first point of the original stroke to the point list
        newpoints.append(point_list[0])

        # iterate the stroke's point list
        i = 1
        while i < len(point_list):
            p1 = point_list[i - 1]

            # calculate the distance of the current pair of points
            d = self.distance(p1, point_list[i])

            if curpos + d >= stepsize:
                # once we reach or step over our desired distance, we push our resampled point
                # to the correct position based on our stepsize
                nx = p1[0] + ((stepsize - curpos) / d) * (point_list[i][0] - p1[0])
                ny = p1[1] + ((stepsize - curpos) / d) * (point_list[i][1] - p1[1])

                # store the new data
                newpoints.append([nx, ny])
                point_list.insert(i, [nx, ny])

                # reset curpos
                curpos = 0
            else:
                curpos += d

            i += 1

        return newpoints

    def rotate(self, points, center, angle_degree):
        new_points = []

        # represent our angle in radians
        angle_rad = angle_degree * (pi / 180)

        # define a 3x3 rotation matrix for clockwise rotation
        rot_matrix = matrix([[cos(angle_rad), -sin(angle_rad), 0],
                            [sin(angle_rad),  cos(angle_rad), 0],
                            [      0,               0,        1]])

        t1 = matrix([[1, 0, -center[0]],
                    [0, 1, -center[1]],
                    [0, 0,     1     ]])

        t2 = matrix([[1, 0,  center[0]],
                    [0, 1,  center[1]],
                    [0, 0,     1     ]])

        # create our actual transformation matrix which rotates a point of points around the center of points
        transform = t2  @ rot_matrix @ t1  # beware of the order of multiplications, not commutative!

        for point in points:

            # homogenous point of the point to be rotated
            hom_point = matrix([[point[0]], [point[1]], [1]])

            # rotated point
            rotated_point = transform @ hom_point

            # storing
            new_points.append(((rotated_point[0] / rotated_point[2]), float(rotated_point[1] / rotated_point[2])))

        return new_points

    def centroid(self, points):
        xs, ys = zip(*points)

        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def angle_between(self, point, centroid):
        dx = centroid[0] - point[0]
        dy = centroid[1] - point[1]

        # return the angle in degrees
        return math.atan2(dy, dx) * 180 / math.pi

    def scale(self, points):

        # the desired interval size
        size = 100

        xs, ys = zip(*points)

        # minimum and maximum occurrences of x and y values of the points
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # calculate the range of the coordinates of the points
        x_range = x_max - x_min
        y_range = y_max - y_min

        points_new = []

        # map the points to the desired interval
        for p in points:
            p_new = ((p[0] - x_min) * size / x_range,
                    (p[1] - y_min) * size / y_range)
            points_new.append(p_new)

        return points_new

    def normalize(self, points):
        # use all the processing functions from above to transform our set of points into the desired shape
        points_new = self.resample(points)
        angle = -self.angle_between(points_new[0], self.centroid(points_new))
        points_new = self.rotate(points_new, self.centroid(points_new), angle)
        points_new = self.scale(points_new)

        return points_new

    def custom_filter(self, points):
        return(self.normalize(points))

    def calculate_similarity(self, sample, template):
        template = self.normalize(template)
        sample = self.normalize(sample)
        dist_all = 0
        for p1, p2 in zip(sample, template):
            dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
            dist_all += dist
        return dist_all


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = GestureRecognizer()
    widget.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())
