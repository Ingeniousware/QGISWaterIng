from ..ActionManagement.insertNodeAction import insertNodeAction
from .insertAbstractTool import InsertAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsProject
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, QEvent, Qt


class InsertSensorNodeTool(InsertAbstractTool):

    def __init__(self, canvas, elementRepository, actionManager, toolbarManager):
        super(InsertSensorNodeTool, self).__init__(canvas, elementRepository, actionManager)
        self.toolbarManager = toolbarManager
        print("Init at Insert Sensor Node")
        if (QgsProject.instance().mapLayersByName("watering_sensors") is not None) and len(
            QgsProject.instance().mapLayersByName("watering_sensors")
        ) != 0:
            self.demandNodeLayer = QgsProject.instance().mapLayersByName("watering_sensors")[0]
            self.toolFindIdentify = QgsMapToolIdentify(self.canvas)
            self.vertexDict = {}

    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())

        # print(self.point.x(), self.point.y(), " ---- ", e.x(), e.y())

        # this can be needed for the case later when a node is substituted by another type of node
        # found_features = self.toolFindIdentify.identify(e.x(), e.y(), [self.demandNodeLayer], QgsMapToolIdentify.TopDownAll)
        # if len(found_features) > 0:
        # element has been found
        #        ...

        # TODO eliminate the direct call to the AddNewElementFromMapInteraction in the next line when the action and action manager are implemented and working
        # self.elementRepository.AddNewElementFromMapInteraction(self.point.x(), self.point.y())
        action = insertNodeAction(self.elementRepository, self.point.x(), self.point.y())
        self.actionManager.execute(action)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.deactivate()

    def deactivate(self):
        print("deactivate insert sensor node tool")
        self.toolbarManager.insertSensorNodeAction.setChecked(False)
        self.canvas.unsetMapTool(self.canvas.mapTool())
