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
        self.UrlGet = "/api/v1/TankNode"
        self.StorageShapeFile = os.path.join(project_path, "watering_tanks.shp")
        self.LayerName = "watering_tanks"
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z","initialLevel",
                         "minimumLevel","maximumLevel","minimumVolume", "nominalDiameter","canOverflow"]
        self.Fields = ['Last Mdf', 'Name', 'Descript', 'Z[m]', 'Init. Lvl', 'Min. Lvl', 
                        'Max. Lvl', 'Min. Vol.', 'Diameter', 'Overflow']
        
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Init. Lvl", QVariant.Double),
            ("Min. Lvl", QVariant.Double),
            ("Max. Lvl", QVariant.Double),
            ("Min. Vol.", QVariant.Double),
            ("Diameter", QVariant.Double),
            ("Overflow", QVariant.Bool),
            ("Pressure", QVariant.Double),
            ("Demand", QVariant.Double),
            ("Demand C", QVariant.Double),
            ("Age", QVariant.Double)
        ]
        self.initializeRepository()
     
    def initializeRepository(self):
        #Tanks Loading
        response_tanks = self.loadElements()
        
        fields = self.setElementFields(self.field_definitions)
        
        #Adding tanks to shapefile
        list_of_tanks = self.loadElementFeatures(response_tanks, self.features)
        tanks_layer = self.createElementLayer(self.features, list_of_tanks, fields, self.field_definitions)
        
        #Write and open shapefile
        self.writeShp(tanks_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Pentagon, 6)
    