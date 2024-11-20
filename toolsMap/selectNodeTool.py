from qgis.gui import (
    QgsMapToolEmitPoint,
    QgsAttributeTableView,
    QgsMapTool,
    QgsMapToolEmitPoint,
    QgsMapToolIdentifyFeature,
    QgsMapToolIdentify,
)
from PyQt5.QtGui import QColor
from qgis.PyQt import uic, QtWidgets
from qgis.core import (
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsProject,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsSymbol,
    edit,
)
from qgis.utils import iface


class SelectNodeTool(QgsMapTool):

    def __init__(self, canvas):

        self.canvas = canvas
        self.point = None
        if (QgsProject.instance().mapLayersByName("watering_demand_nodes") is not None) and len(
            QgsProject.instance().mapLayersByName("watering_demand_nodes")
        ) != 0:
            self.layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
            self.test = QgsMapToolIdentify(self.canvas)
        super().__init__(self.canvas)
        print("Init at Tool Select Node")
        # self.action.triggered.connect(self.deactivate)  #deactivate is called automatically, it is defined in QgsMapTool

    def canvasPressEvent(self, e):
        self.layer.removeSelection()  # remove selection only if ctrl and shift are not pressed
        found_features = self.test.identify(e.x(), e.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        self.layer.selectByIds([f.mFeature.id() for f in found_features], QgsVectorLayer.AddToSelection)
        if found_features:
            print(found_features[0].mFeature.attributes())

    def deactivate(self):
        print("Clicked to unselect button.")
        if (QgsProject.instance().mapLayersByName("watering_demand_nodes") is not None) and len(
            QgsProject.instance().mapLayersByName("watering_demand_nodes")
        ) != 0:
            self.layer.removeSelection()  # when a project is open and then a new project is created then it could be that layer is none
            # self.canvas.unsetMapTool(self)  #You don’t have to call it manually, QgsMapTool takes care of it.
