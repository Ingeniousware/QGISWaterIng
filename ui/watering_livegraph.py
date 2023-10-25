import os
import random
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPen, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QPushButton, QVBoxLayout, QWidget, QGridLayout
from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_livegraph.ui'))

class ChartView(QtWidgets.QWidget, FORM_CLASS):
    def __init__(self, title):
        super(ChartView, self).__init__()
        self.setupUi(self)
        # Set window title
        self.setWindowTitle(title)
        # Setup scene
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setBackgroundBrush(QBrush(QColor("white")))
        # Pen configurations
        self.chart_pen = QPen(QColor("green"))
        self.chart_pen.setWidth(2)

        self.grid_pen = QPen(QColor("gray"))
        self.grid_pen.setStyle(Qt.DashLine)
        self.grid_pen.setWidth(0.400)
        # Initializations
        self.points = []
        self.x = 0
        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(1000)  # 1 second interval
        # Button actions
        self.BTstopGraph.clicked.connect(self.stop_graph)

    def update_chart(self):
        # Update x and y values
        new_x = self.x + 10
        new_y = random.randint(0, 100)
        self.points.append((new_x, -new_y))

        # Remove the oldest point if more than 100 points
        if len(self.points) > 100:
            self.points.pop(0)

        # Create a new QPainterPath and draw
        self.chart_path = QPainterPath()
        self.chart_path.moveTo(*self.points[0])
        for point in self.points[1:]:
            self.chart_path.lineTo(*point)
        self.x = new_x

        self.scene.clear()
        self.scene.addPath(self.chart_path, self.chart_pen)

        # Draw upper and lower lines
        upper_value = -100
        lower_value = -1
        upper_line = QPainterPath()
        lower_line = QPainterPath()
        start_x = self.points[0][0] if self.points else 0
        end_x = self.points[-1][0] if self.points else new_x

        upper_line.moveTo(start_x, upper_value)
        upper_line.lineTo(end_x, upper_value)

        lower_line.moveTo(start_x, lower_value)
        lower_line.lineTo(end_x, lower_value)

        self.scene.addPath(upper_line, self.grid_pen)
        self.scene.addPath(lower_line, self.grid_pen)

        self.graphicsView.fitInView(self.scene.itemsBoundingRect(), mode=Qt.KeepAspectRatio)
    
    def stop_graph(self):
        self.timer.stop()
