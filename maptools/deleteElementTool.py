#DeleteElementTool

from qgis.gui import QgsMapToolEmitPoint, QgsAttributeTableView, QgsMapTool, QgsMapToolEmitPoint, QgsMapToolIdentifyFeature,QgsMapToolIdentify
from PyQt5.QtGui import QColor
from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsGeometry, QgsVectorLayer, QgsPointXY, QgsProject, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, edit
from qgis.utils import iface
from qgis.core import QgsProject, QgsFeatureRequest, QgsVectorLayer
from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.gui import QgsMapCanvas
from qgis.core import QgsLayerTreeLayer

class DeleteElementTool(QgsMapTool):

    def __init__(self, canvas):
        self.canvas = canvas
        self.point = None
        self.layer = None
        self.test = QgsMapToolIdentify(self.canvas)
        super().__init__(self.canvas)
        print("Init at Tool Delete Element")

    def canvasPressEvent(self, e):
        
        found_features = self.test.identify(e.x(), e.y(), self.test.TopDownStopAtFirst, self.test.VectorLayer)
        
        if found_features:
            self.layer = found_features[0].mLayer
            self.layer.removeSelection()
            
            print("Clicled layer: ", self.layer)
            print(found_features[0].mFeature.attributes())
            feature_ids = [f.mFeature.id() for f in found_features]

            # Start an undo block in case we want to revert this operation
            self.layer.startEditing()

            # Delete the features with the collected IDs
            success = self.layer.deleteFeatures(feature_ids)

            if success:
                # If features were successfully deleted, save the changes
                self.layer.commitChanges()
            else:
                # If the delete was not successful, roll back the changes
                self.layer.rollBack()
                                  
    def deactivate(self):
        print("Clicked to unselect button of deleting element.")
        self.layer.removeSelection()
    