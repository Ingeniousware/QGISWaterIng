import os
import random
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPen, QColor, QBrush, QPainterPath, QPixmap, QPainter
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

        self.limits_pen = QPen(QColor("orange"))
        self.limits_pen.setStyle(Qt.DashLine)
        self.limits_pen.setWidth(0.200)

        self.grid_pen = QPen(QColor("gray"))
        self.grid_pen.setStyle(Qt.DashLine)
        self.grid_pen.setWidth(0.200)

        self.draw_grid_on_background()
        # Initializations
        self.points = []
        self.x = 0
        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(1000)  # 1 second interval
        # Button actions
        self.BTstopGraph.clicked.connect(self.stop_graph)
        self.upper_bound = -100
        self.lower_bound = -1
    

    def draw_grid_on_background(self):
        grid_spacing = 20
        # Adjusting width and height to ensure they are multiples of grid_spacing
        width = (self.graphicsView.width() // grid_spacing) * grid_spacing
        height = (self.graphicsView.height() // grid_spacing) * grid_spacing
        
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(self.grid_pen)
        for x in range(0, width, grid_spacing):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height, grid_spacing):
            painter.drawLine(0, y, width, y)
        painter.end()
        self.graphicsView.setBackgroundBrush(QBrush(pixmap))

    def update_chart(self):
        # Update x and y values
        new_x = self.x + 10
        new_y = random.randint(0, 110)
        print(new_x)
        print(new_y)

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
        #self.scene.clear()
        self.scene.addPath(self.chart_path, self.chart_pen)
        start_x = self.points[0][0] if self.points else 0
        end_x = self.points[-1][0] if self.points else new_x
        self.draw_upper_limit(start_x, end_x)
        self.draw_lower_limit(start_x, end_x)

        if new_y > 100:
            self.add_vertical_line()
        self.graphicsView.fitInView(self.scene.itemsBoundingRect(), mode=Qt.KeepAspectRatio)

    def draw_upper_limit(self, start_x, end_x):
        upper_line = QPainterPath()
        upper_line.moveTo(start_x, self.upper_bound)
        upper_line.lineTo(end_x, self.upper_bound)
        self.scene.addPath(upper_line, self.limits_pen)

    def draw_lower_limit(self, start_x, end_x):
        lower_line = QPainterPath()
        lower_line.moveTo(start_x, self.lower_bound)
        lower_line.lineTo(end_x, self.lower_bound)
        self.scene.addPath(lower_line, self.limits_pen)

    def add_vertical_line(self):
        line_pen = QPen(QColor("red"))
        line_pen.setWidth(1)
        line_path = QPainterPath()
        line_path.moveTo(self.x, -10)
        line_path.lineTo(self.x, 0)
        self.scene.addPath(line_path, line_pen)

    
    def stop_graph(self):
        self.timer.stop()
