import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class WateringDemandNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(WateringDemandNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/DemandNode"
        self.StorageShapeFile = os.path.join(project_path, "watering_demand_nodes.shp")
        self.field_definitions = None
        self.Color = QColor.fromRgb(255, 255, 255)
        self.StrokeColor = QColor.fromRgb(23, 61, 108)
        self.initializeRepository()
        
    def initializeRepository(self):
        #Water Demands Loading
        response_demandNodes = self.loadElements()
        
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Modified", QVariant.String),
            ("Name", QVariant.String),
            ("Description", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Base Demand [l/s]", QVariant.Double),
            ("Demand Pattern", QVariant.Bool),
            ("Pressure", QVariant.Double),
            ("Demand", QVariant.Double),
            ("Demand C", QVariant.Double),
            ("Age", QVariant.Double)
        ]
    
        demandNode_features = ["lng", "lat", "serverKeyId","lastModified", "name","description",
                               "z","baseDemand","demandPatternFK"]
        
        fields = self.setElementFields(self.field_definitions)
        
        #Adding reservoirs to shapefile
        list_of_demandNodes = self.loadElementFeatures(response_demandNodes, demandNode_features)
        demandNodes_layer = self.createElementLayer(demandNode_features, list_of_demandNodes, fields, self.field_definitions)
        
        #Write and open shapefile
        self.writeShp(demandNodes_layer)
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Circle, 2)
