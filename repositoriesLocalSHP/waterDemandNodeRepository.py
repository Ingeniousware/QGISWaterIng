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
        self.LayerName = "watering_demand_nodes"
        
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("B. Demand", QVariant.Double),
            ("Pattern", QVariant.Bool),
            ("Pressure", QVariant.Double),
            ("Demand", QVariant.Double),
            ("Demand C", QVariant.Double),
            ("Age", QVariant.Double)
        ]
    
        self.features = ["lng", "lat", "serverKeyId","lastModified", "name","description",
                               "z","baseDemand","demandPatternFK"]
        
        self.Color = QColor.fromRgb(255, 255, 255)
        self.StrokeColor = QColor.fromRgb(23, 61, 108)
        self.currentLayer = None
        self.initializeRepository()
        
    def initializeRepository(self):
        super(WateringDemandNodeRepository, self).initializeRepository()   
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Circle, 2)
