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
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
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
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None        

    def initializeRepository(self):
        super(ReservoirNodeRepository, self).initializeRepository()      
       
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Square, 6)
