import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsLayerTreeLayer
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class ReservoirNodeRepository(AbstractRepository):
    
    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(ReservoirNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterReservoir"
        self.StorageShapeFile = os.path.join(project_path, "watering_reservoirs.shp")
        self.LayerName = "watering_reservoirs"
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Head[m]", QVariant.Double),
            ("Pressure", QVariant.Double),
            ("Demand", QVariant.Double),
            ("Demand C", QVariant.Double),
            ("Age", QVariant.Double)
        ]
        
        self.features = ["lng","lat","serverKeyId","lastModified",
                        "name","description","z","head"]
        
        self.initializeRepository()
     
    def initializeRepository(self):
        #Reservoirs Loading from API
        response_reservoirs = self.loadElements()
        
        fields = self.setElementFields(self.field_definitions)
        
        #Adding reservoirs to shapefile
        reservoirs_layer = self.createElementLayerFromServerResponse(self.features, response_reservoirs, fields, self.field_definitions)
              
        #Write and open shapefile
        self.writeShp(reservoirs_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Square, 6)
