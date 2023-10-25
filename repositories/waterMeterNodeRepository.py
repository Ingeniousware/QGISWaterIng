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
        self.LayerName = "watering_waterMeter"
        self.field_definitions = None
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Meterstate", QVariant.Int),
            ("FunctionalType", QVariant.Int),
            ("LastReadDateTime", QVariant.String)
        ]
        
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description","meterstate",
                                "functionalType","lastReadDateTime"]
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None
        self.initializeRepository()

        
     
    def initializeRepository(self):
        super(WaterMeterNodeRepository, self).initializeRepository()   
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Diamond, 6)
    