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
        self.initializeRepository()
     
    def initializeRepository(self):
        #Tanks Loading
        response_pumps = self.loadElements()

        #Setting shapefile fields 
        pump_field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Pump Model FK", QVariant.String),
            ("Relative Speed", QVariant.Double)
        ]
        
        pump_features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z", "relativeSpeed", "pumpModelFK"]
        
        fields = self.setElementFields(pump_field_definitions)
        
        #Adding tanks to shapefile
        list_of_pumps = self.loadElementFeatures(response_pumps, pump_features)
        pumps_layer = self.createElementLayer(pump_features, list_of_pumps, fields, pump_field_definitions)
        
        #Write and open shapefile
        self.writeShp(pumps_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.SemiCircle, 6)
    