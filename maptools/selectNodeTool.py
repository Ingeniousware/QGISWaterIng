from qgis.gui import QgsMapToolEmitPoint, QgsAttributeTableView, QgsMapTool, QgsMapToolEmitPoint, QgsMapToolIdentifyFeature,QgsMapToolIdentify
from PyQt5.QtGui import QColor
from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsGeometry, QgsVectorLayer, QgsPointXY, QgsProject, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, edit
from qgis.utils import iface


class SelectNodeTool(QgsMapTool):

    def __init__(self, canvas, action):
        
        self.canvas = canvas
        self.action = action
        self.point = None
        self.layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        self.test = QgsMapToolIdentify(self.canvas)
        self.clicked = False
        super().__init__(self.canvas)
        self.canvas.setMapTool(self)
        self.action.triggered.connect(self.deactivate)
        

    def canvasPressEvent(self, e):
        if self.clicked == False:
            self.clicked = True
            found_features = self.test.identify(e.x(), e.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
            self.layer.selectByIds([f.mFeature.id() for f in found_features], QgsVectorLayer.AddToSelection)
            if found_features:
                print(found_features[0].mFeature.attributes())
        else:
            self.deactivate()
            
    def deactivate(self):
        print("Clicked to unselect button.")
        self.layer.removeSelection()
        self.canvas.unsetMapTool(self)
        