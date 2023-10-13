import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class ValveNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(ValveNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterValve"
        self.StorageShapeFile = os.path.join(project_path, "watering_valves.shp")
        self.field_definitions = None
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.initializeRepository()
     
    def initializeRepository(self):
        #Valves Loading
        response_valves = self.loadElements()

        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Diameter", QVariant.Double),
            ("minorLossCoef", QVariant.Bool),
            ("initialStatus", QVariant.Double),
            ("typeValvule", QVariant.Double)
        ]
        
        valve_features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z",
                         "diameter"]
        
        fields = self.setElementFields(self.field_definitions)
        
        #Adding tanks to shapefile
        list_of_valves = self.loadElementFeatures(response_valves, valve_features)
        valves_layer = self.createElementLayer(valve_features, list_of_valves, fields, self.field_definitions)
        
        #Write and open shapefile
        self.writeShp(valves_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Cross2, 6)
    