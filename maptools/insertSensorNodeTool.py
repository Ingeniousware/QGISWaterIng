from .insertNodeAbstractTool import InsertNodeAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsProject
from PyQt5.QtGui import QColor

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
            print(found_features[0].mFeature.attributes())
            m = QgsVertexMarker(self.canvas)
            m.setCenter(self.point)
            m.setColor(QColor(0,255,0))
            m.setIconSize(5)
            m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            m.setPenWidth(3)


    def deactivate(self):
        print("deactivate insert demand node tool")

