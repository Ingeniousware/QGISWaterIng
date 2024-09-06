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
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("B. Demand", QVariant.Double),
            ("EmitterCoe", QVariant.Double),
            ("Pattern", QVariant.Bool),
            ("lastUpdate", QVariant.String)
        ]
    
        self.features = ["lng", "lat", "serverKeyId","lastModified", "name","description",
                         "z","baseDemand","emitterCoeff","demandPatternFK"]

        self.LayerType = "Point?crs="
        
        self.Color = QColor.fromRgb(255, 255, 255)
        self.StrokeColor = QColor.fromRgb(23, 61, 108)
        self.currentLayer = None

    def initializeRepository(self):
        super(WateringDemandNodeRepository, self).initializeRepositoryStreamingData()   
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Circle, 2)
        self.createBackupLayer()

    def setDefaultValues(self, feature):
        name = "nodeName"
        description = "node from QGIS"
        baseDemand = 5
        z = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("B. Demand", baseDemand)
        feature.setAttribute("Z[m]", z)       
