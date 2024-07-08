import os
from ..watering_utils import WateringUtils
from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class AbstractShpImport():
    def __init__(self):
        #Constructor.
        self.token = os.environ.get('TOKEN')
        scenario_fk = WateringUtils.getScenarioId()
    
    def addSelected_Layer(self, file_path):
        if file_path.lower().endswith('.shp'):
            vlayer = QgsVectorLayer(file_path, "New Layer", "ogr")
            if not vlayer.isValid():
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Warning)
                message_box.setWindowTitle("Error")
                message_box.setText("Layer failed to load!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec_()
            else:
                QgsProject.instance().addMapLayer(vlayer)
                self.TabWidget.show()
                self.LayerTypeCBox.setEnabled(False)
                self.attribute_matcher()
                self.uploadShpFile.setEnabled(True)
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Error")
            message_box.setText("Selected file is not a shapefile (.shp)")
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()
    
    def shpProcessing(self, layer_name):
        ...