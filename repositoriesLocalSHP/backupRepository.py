import os
import json

from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsFeature
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest
from PyQt5.QtCore import QFileInfo
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsFields, QgsField, QgsProject
from PyQt5.QtCore import QVariant, QFileInfo

class BackupRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(BackupRepository, self).__init__(token, scenarioFK)      
        #self.UrlGet = "/api/v1/SensorStation"
        self.StorageShapeFile = os.path.join(project_path, "watering_backup.shp")
        self.LayerName = "watering_backup"
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        #Setting shapefile fields
        self.field_definitions = []
        self.features = []
        self.currentLayer = None

    def initializeRepository(self):
        self.currentLayer = QgsVectorLayer("GeometryCollection?crs=epsg:4326", self.LayerName, "memory")

        provider = self.currentLayer.dataProvider()

        provider.addAttributes(self.field_definitions)

        self.currentLayer.updateFields()

        provider.addFeatures(self.features)

        QgsProject.instance().addMapLayer(self.currentLayer)
        
        #self.save_layer_to_shapefile()
        #self.openBackupLayer()
        
    def save_layer_to_shapefile(self, file_path):
        # Write the layer to a shapefile
        error = QgsVectorFileWriter.writeAsVectorFormat(self.currentLayer, file_path, "UTF-8", self.currentLayer.crs(), "ESRI Shapefile")
        if error[0] == QgsVectorFileWriter.NoError:
            print(f"Layer saved successfully to {file_path}")
            return True
        else:
            print(f"Error saving layer: {error}")
            return False
                
    def openBackupLayer(self):
        print("Is backup being opened?")
        no_geometry_layer = QgsVectorLayer(self.StorageShapeFile, self.LayerName, "ogr")
        
        if not no_geometry_layer.isValid():
            print("Backup layer failed to load!")
        else:
            # Add the layer to the Layers panel
            QgsProject.instance().addMapLayer(no_geometry_layer)
            
            print("Backup layer loaded successfully!")      