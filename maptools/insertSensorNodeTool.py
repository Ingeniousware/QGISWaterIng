from .insertNodeAbstractTool import InsertNodeAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsProject
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, QEvent, Qt

class InsertSensorNodeTool(InsertNodeAbstractTool):
    def __init__(self, canvas):
        super(InsertSensorNodeTool, self).__init__(canvas)  
        print("Init at Insert Demand Node")
        if (QgsProject.instance().mapLayersByName("watering_demand_nodes") is not None) and len(QgsProject.instance().mapLayersByName("watering_demand_nodes")) != 0:
          self.demandNodeLayer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
          self.toolFindIdentify = QgsMapToolIdentify(self.canvas)

    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())
        
        print(self.point.x(), self.point.y())

        found_features = self.toolFindIdentify.identify(e.x(), e.y(), [self.demandNodeLayer], QgsMapToolIdentify.TopDownAll)
        if len(found_features) > 0:
            #print(found_features[0].mFeature.attributes())
            #print(found_features[0].mFeature.geometry().asPoint())
            m = QgsVertexMarker(self.canvas)
            m.setCenter(found_features[0].mFeature.geometry().asPoint())
            m.setColor(QColor(0,255,0))
            m.setIconSize(20)
            m.setIconType(QgsVertexMarker.ICON_CIRCLE) # or ICON_CROSS, ICON_X
            m.setPenWidth(4)

    def removeMarkers(self):
        vertex_items = [i for i in self.canvas.scene().items() if isinstance(i, QgsVertexMarker)]
        for vertex in vertex_items:
            self.canvas.scene().removeItem(vertex)
        self.canvas.refresh()

    def deactivate(self):
        print("deactivate insert demand node tool")