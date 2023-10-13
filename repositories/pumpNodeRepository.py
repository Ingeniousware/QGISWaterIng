import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class PumpNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(PumpNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterPump"
        self.StorageShapeFile = os.path.join(project_path, "watering_pumps.shp")
        self.LayerName = "watering_pumps"
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Pump Model FK", QVariant.String),
            ("Relative Speed", QVariant.Double)
        ]
        
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z", "relativeSpeed"]
        
        self.initializeRepository()


     
    def initializeRepository(self):
        #Tanks Loading
        response_pumps = self.loadElements()
        
        fields = self.setElementFields(self.field_definitions)
        
        #Adding tanks to shapefile
        pumps_layer = self.createElementLayerFromServerResponse(self.features, response_pumps, fields, self.field_definitions)
        
        #Write and open shapefile
        self.writeShp(pumps_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.SemiCircle, 6)
    