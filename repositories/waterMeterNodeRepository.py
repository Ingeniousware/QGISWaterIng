import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class WaterMeterNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(WaterMeterNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterMeter"
        self.StorageShapeFile = os.path.join(project_path, "watering_waterMeter.shp")
        self.field_definitions = None
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Meterstate", QVariant.Double),
            ("FunctionalType", QVariant.Double),
            ("LastReadDateTime", QVariant.String)
        ]
        
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description","meterstate",
                                "functionalType","lastReadDateTime"]
        
        self.initializeRepository()

        
     
    def initializeRepository(self):
       
        response_waterMeter = self.loadElements()        
        fields = self.setElementFields(self.field_definitions)
        
        #Adding tanks to shapefile
        waterMeter_layer = self.createElementLayerFromServerResponse(self.features, response_waterMeter, fields, self.field_definitions)
        
        #Write and open shapefile
        self.writeShp(waterMeter_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Diamond, 6)
    