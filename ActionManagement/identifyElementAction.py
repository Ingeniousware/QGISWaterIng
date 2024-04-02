from qgis.gui import QgsMapToolIdentify, QgsIdentifyMenu
from qgis.utils import iface
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMenu

class WateringIdentifyTool(QgsMapToolIdentify):
    def __init__(self, canvas, actionManager, toolbarManager):
        super().__init__(canvas)
        self.canvas = canvas
        self.actionManager = actionManager
        self.toolbarManager = toolbarManager

    def canvasReleaseEvent(self, event):
        identified_features = self.identify(event.x(), event.y(), self.TopDownStopAtFirst)
    
        if identified_features:
            feature = identified_features[0].mFeature
            layer = identified_features[0].mLayer
            iface.openFeatureForm(layer, feature, True)

        
              
    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.deactivate()

    def deactivate(self):
        print("deactivate watering identify element tool")   
        self.toolbarManager.wateringIdentifyAction.setChecked(False)
        self.canvas.unsetMapTool(self.canvas.mapTool())