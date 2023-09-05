import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class TankNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(TankNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/TankNode"
        self.StorageShapeFile = os.path.join(project_path, "watering_tanks.shp")
        self.tanksLayer()
     
    def tanksLayer(self):
        #Tanks Loading
        response_tanks = self.loadElements()

        #Setting shapefile fields 
        tank_field_definitions = [
            ("Tank ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Initial Level [m]", QVariant.Double),
            ("Minimum Level [m]", QVariant.Double),
            ("Maximum Level [m]", QVariant.Double),
            ("Minimum Volume [m3]", QVariant.Double),
            ("Diameter", QVariant.Double),
            ("Can Overflow", QVariant.Bool)
        ]
        
        tank_features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z","initialLevel",
                         "minimumLevel","maximumLevel","minimumVolume", "nominalDiameter","canOverflow"]
        
        fields = self.setElementFields(tank_field_definitions)
        
        #Adding tanks to shapefile
        list_of_tanks = self.loadElementFeatures(response_tanks, tank_features)
        tanks_layer = self.createElementLayer(tank_features, list_of_tanks, fields, tank_field_definitions)
        
        #Write and open shapefile
        self.writeShp(tanks_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Pentagon, 6)
    