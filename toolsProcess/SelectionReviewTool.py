import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsFeatureRequest, QgsRectangle, QgsWkbTypes, QgsGeometry, QgsPointXY, QgsMapLayer, QgsProject
from ..watering_utils import WateringUtils
from ..ui.watering_selection_review import WateringSelectionReview
import itertools


class SelectionReviewTool:

    def __init__(self, iface):
        self.iface = iface
        self.mapTool = None

    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.iface.tr("Error"),
                self.iface.tr("Load a project scenario first in Download Elements!"),
                level=1,
                duration=5,
            )
            return

        if os.environ.get("TOKEN") is None:
            self.iface.messageBar().pushMessage(
                self.iface.tr("Error"), self.iface.tr("You must login to WaterIng first!"), level=1, duration=5
            )
            return

        print("Inside Selection Review")
        self.setupMapTool()

    def setupMapTool(self):
        mc = self.iface.mapCanvas()
        self.mapTool = RectangleSelectionTool(mc)
        mc.setMapTool(self.mapTool)


class RectangleSelectionTool(QgsMapTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.rubberBand = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.startPoint = None
        self.endPoint = None
        self.isDrawing = False

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.isDrawing:
                self.startPoint = self.toMapCoordinates(event.pos())
                self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
                self.isDrawing = True
            else:
                self.endPoint = self.toMapCoordinates(event.pos())
                self.isDrawing = False
                self.drawRectangle()

    def canvasMoveEvent(self, event):
        if self.isDrawing and self.startPoint:
            self.endPoint = self.toMapCoordinates(event.pos())
            rect = QgsRectangle(self.startPoint, self.endPoint)
            points = [
                QgsPointXY(rect.xMinimum(), rect.yMinimum()),
                QgsPointXY(rect.xMaximum(), rect.yMinimum()),
                QgsPointXY(rect.xMaximum(), rect.yMaximum()),
                QgsPointXY(rect.xMinimum(), rect.yMaximum()),
                QgsPointXY(rect.xMinimum(), rect.yMinimum()),
            ]
            self.rubberBand.setToGeometry(QgsGeometry.fromPolygonXY([points]), None)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
            self.startPoint = None
            self.endPoint = None
            self.isDrawing = False
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if not self.isDrawing and self.startPoint and self.endPoint:
                self.printSelectedFeatures()

    def drawRectangle(self):
        if not self.startPoint or not self.endPoint:
            return
        rect = QgsRectangle(self.startPoint, self.endPoint)
        points = [
            QgsPointXY(rect.xMinimum(), rect.yMinimum()),
            QgsPointXY(rect.xMaximum(), rect.yMinimum()),
            QgsPointXY(rect.xMaximum(), rect.yMaximum()),
            QgsPointXY(rect.xMinimum(), rect.yMaximum()),
            QgsPointXY(rect.xMinimum(), rect.yMinimum()),
        ]
        self.rubberBand.setToGeometry(QgsGeometry.fromPolygonXY([points]), None)

    def getNodesVsNodesDistanceArray(self):
        rect = QgsRectangle(self.startPoint, self.endPoint)
        if rect.isNull():
            return

        features = []
        for layer in self.canvas.layers():
            if layer.type() == QgsMapLayer.VectorLayer and layer.name() == "watering_demand_nodes":
                tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                if tree_layer.isVisible():
                    request = QgsFeatureRequest().setFilterRect(rect)
                    for feature in layer.getFeatures(request):
                        print(f"Feature found: {feature.id()}")
                        features.append(feature)

        if not features:
            return []

        distances = []
        for feature1, feature2 in itertools.combinations(features, 2):
            geom1 = feature1.geometry()
            geom2 = feature2.geometry()
            distance = geom1.distance(geom2)
            distances.append(
                [feature1.attribute("Name"), feature2.attribute("Name"), distance, feature1.id(), feature2.id()]
            )
            print(f"Distance between {feature1.attribute('Name')} and {feature2.attribute('Name')}: {distance}")

        distance_array = []
        for item in distances:
            distance_array.append([item[0], item[1], item[2], item[3], item[4]])

        print(distance_array)
        return distance_array

    def getNodesVsPipesDistanceArray(self):
        rect = QgsRectangle(self.startPoint, self.endPoint)
        if rect.isNull():
            return

        nodes = []
        pipes = []

        for layer in self.canvas.layers():
            if layer.type() == QgsMapLayer.VectorLayer and layer.name() == "watering_demand_nodes":
                tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                if tree_layer.isVisible():
                    request = QgsFeatureRequest().setFilterRect(rect)
                    for feature in layer.getFeatures(request):
                        print(f"Node found: {feature.id()}")
                        nodes.append(feature)

        for layer in self.canvas.layers():
            if layer.type() == QgsMapLayer.VectorLayer and layer.name() == "watering_pipes":
                tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                if tree_layer.isVisible():
                    request = QgsFeatureRequest().setFilterRect(rect)
                    for feature in layer.getFeatures(request):
                        print(f"Pipe found: {feature.id()}")
                        pipes.append(feature)

        if not nodes or not pipes:
            return []

        distances = []
        for node in nodes:
            for pipe in pipes:
                geom1 = node.geometry()
                geom2 = pipe.geometry()
                distance = geom1.distance(geom2)
                distances.append([node.attribute("Name"), pipe.attribute("Name"), distance, node.id(), pipe.id()])
                print(f"Distance between {node.attribute('Name')} and {pipe.attribute('Name')}: {distance}")

        distance_array = []
        for item in distances:
            distance_array.append([item[0], item[1], item[2], item[3], item[4]])

        print(distance_array)
        return distance_array

    def printSelectedFeatures(self):
        rect = QgsRectangle(self.startPoint, self.endPoint)
        if rect.isNull():
            return

        node_node_list = self.getNodesVsNodesDistanceArray()
        node_pipe_list = self.getNodesVsPipesDistanceArray()

        self.runSelectionReviewDialog(node_node_list, node_pipe_list)

    def runSelectionReviewDialog(self, node_node_list, node_pipe_list):
        dlg = WateringSelectionReview(node_node_list, node_pipe_list)
        dlg.show()
        dlg.exec_()

    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
