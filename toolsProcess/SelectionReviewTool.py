import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsFeatureRequest, QgsRectangle, QgsWkbTypes, QgsGeometry, QgsPointXY, QgsMapLayer, QgsProject
from ..watering_utils import WateringUtils
from ..ui.watering_selection_review import WateringSelectionReview

class SelectionReviewTool:

    def __init__(self, iface):
        self.iface = iface
        self.mapTool = None

    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.iface.tr(u"Error"), 
                self.iface.tr(u"Load a project scenario first in Download Elements!"), 
                level=1, duration=5
            )
            return

        if os.environ.get('TOKEN') is None:
            self.iface.messageBar().pushMessage(
                self.iface.tr("Error"), 
                self.iface.tr("You must login to WaterIng first!"), 
                level=1, duration=5
            )
            return

        print("Inside Selection Review")
        self.setupMapTool()

    def setupMapTool(self):
        mc = self.iface.mapCanvas()
        self.mapTool = RectangleSelectionTool(mc)
        mc.setMapTool(self.mapTool)
        self.mapTool.featuresIdentified.connect(self.onFeaturesIdentified)

    def onFeaturesIdentified(self, features):
        print("Features selected:")
        for feature in features:
            print("Feature ID: " + str(feature.id()))

class RectangleSelectionTool(QgsMapTool):
    featuresIdentified = pyqtSignal(list)

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
                QgsPointXY(rect.xMinimum(), rect.yMinimum())
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
            QgsPointXY(rect.xMinimum(), rect.yMinimum())
        ]
        self.rubberBand.setToGeometry(QgsGeometry.fromPolygonXY([points]), None)

    def printSelectedFeatures(self):
        rect = QgsRectangle(self.startPoint, self.endPoint)
        if rect.isNull():
            return

        features = []
        for layer in self.canvas.layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                if tree_layer.isVisible():
                    request = QgsFeatureRequest().setFilterRect(rect)
                    for feature in layer.getFeatures(request):
                        print(f"Feature found: {feature.id()}")
                        features.append(feature)
                        
        print("Total features found: ", len(features))
        self.featuresIdentified.emit(features)
        self.runSelectionReviewDialog(features)
        
    def runSelectionReviewDialog(self, features_list):
        dlg = WateringSelectionReview(features_list)
        dlg.show()
        dlg.exec_()

    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
