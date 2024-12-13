from .insertAbstractTool import InsertAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsProject
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, QEvent, Qt


class InsertSensorNodeToolPlacement(InsertAbstractTool):
    def __init__(self, canvas, elementRepository, actionManager, toolbarManager):
        super(InsertSensorNodeToolPlacement, self).__init__(canvas, elementRepository, actionManager)
        self.toolbarManager = toolbarManager
        print("Init at Insert Sensor Node")
        if (QgsProject.instance().mapLayersByName("watering_demand_nodes") is not None) and len(
            QgsProject.instance().mapLayersByName("watering_demand_nodes")
        ) != 0:
            self.demandNodeLayer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
            self.toolFindIdentify = QgsMapToolIdentify(self.canvas)
            self.vertexDict = {}

    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())

        print(self.point.x(), self.point.y())

        found_features = self.toolFindIdentify.identify(
            e.x(), e.y(), [self.demandNodeLayer], QgsMapToolIdentify.TopDownAll
        )
        if len(found_features) > 0:
            coord_feature = found_features[0].mFeature.geometry().asPoint()
            if coord_feature not in self.vertexDict:
                m = QgsVertexMarker(self.canvas)
                m.setCenter(coord_feature)
                m.setColor(QColor(0, 255, 0))
                m.setIconSize(20)
                m.setIconType(QgsVertexMarker.ICON_CIRCLE)  # or ICON_CROSS, ICON_X
                m.setPenWidth(4)
                self.vertexDict[coord_feature] = 1
            else:
                del self.vertexDict[coord_feature]
                self.removeMarker(coord_feature)

    def removeMarker(self, coord):
        vertex_items = [i for i in self.canvas.scene().items() if isinstance(i, QgsVertexMarker)]
        for vertex in vertex_items:
            if vertex.center() == coord:
                self.canvas.scene().removeItem(vertex)
        self.canvas.refresh()

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.deactivate()

    def deactivate(self):
        print("deactivate insert sensor node tool")
        self.toolbarManager.insertSensorNodeAction.setChecked(False)
        self.canvas.unsetMapTool(self.canvas.mapTool())
