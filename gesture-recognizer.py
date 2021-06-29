from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit, QLabel
from pyqtgraph.Qt import QtGui
import sys

class GestureRecognizer(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Recognizer")
        self.curr_gesture = ""
        self.gestures = []
        self._init_ui()
        self.setMinimumSize(800, 800)

    def _init_ui(self):
        # init layouts
        self.main_layout = QtGui.QVBoxLayout()
        self.gesture_text_layout = QtGui.QGridLayout()
        self.button_layout = QtGui.QGridLayout()
        self.recognize_layout = QtGui.QGridLayout()
        self.draw_widget = QDrawWidget(100, 100)

        #init line edit
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
        self.gesture_list.currentIndexChanged.connect(self.on_select)
        
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
        self.gesture_list.addItem("Triangle")

        self.setLayout(self.main_layout)

    def on_add_btn_clicked(self):
        gesture = self.line_edit.text()
        if gesture != "":
            self.curr_gesture = self.line_edit.text()
            if self.curr_gesture not in self.gestures:
                self.gestures.append(self.curr_gesture)
                self.gesture_list.clear()
                self.gesture_list.addItems(self.gestures)
        print("add btn clicked: " + self.curr_gesture)
        print(self.draw_widget.getPoints())

    def on_reco_btn_clicked(self):
        # add result
        print("on reco button")

    def on_select(self, i):
        selected_gesture = self.gesture_list.currentText()
        self.curr_gesture = selected_gesture
        self.line_edit.setText(self.curr_gesture)


class QDrawWidget(QtWidgets.QWidget):
    
    def __init__(self, width=800, height=800):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.grid = True
        self.points = []
        self.setMouseTracking(True) # only get events when button is pressed
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
                self.points = custom_filter(self.points) # needs to be implemented outside!
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

def custom_filter(points):
    return points

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = GestureRecognizer()
    widget.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())