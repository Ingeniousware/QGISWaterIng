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
        self.initializeRepository()
     
    def initializeRepository(self):
        #Reservoirs Loading from API
        response_reservoirs = self.loadElements()
        
        #Setting shapefile fields 
        reservoirs_field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Head[m]", QVariant.Double),
            ("Pressure", QVariant.Double),
            ("Demand", QVariant.Double),
            ("Demand C", QVariant.Double),
            ("Age", QVariant.Double)
        ]
        
        reservoir_features = ["lng","lat","serverKeyId","lastModified",
                              "name","description","z","head"]
        
        fields = self.setElementFields(reservoirs_field_definitions)
                
        #Adding reservoirs to shapefile
        list_of_reservoirs = self.loadElementFeatures(response_reservoirs, reservoir_features)
        reservoirs_layer = self.createElementLayer(reservoir_features, list_of_reservoirs, fields, reservoirs_field_definitions)
        
        #Write and open shapefile
        self.writeShp(reservoirs_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Square, 6)
