import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class PumpNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(PumpNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterPump"
        self.StorageShapeFile = os.path.join(project_path, "watering_pumps.shp")
        self.LayerName = "watering_pumps"
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Model FK", QVariant.String),
            ("Rel. Speed", QVariant.Double),
            ("Pressure", QVariant.Double),
            ("Demand", QVariant.Double),
            ("Demand C", QVariant.Double)
        ]
        
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z", "relativeSpeed"]
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None
     
    def initializeRepository(self):
        super(PumpNodeRepository, self).initializeRepository() 
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.SemiCircle, 6)

    def setDefaultValues(self, feature):
        name = "pumpName"
        description = "pump form QGIS"
        z = 0
        model = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        speed = 0
        pressure = 0
        demand = 0
        demandC = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)
        feature.setAttribute("Model FK", model)
        feature.setAttribute("Rel. Speed", speed)
        feature.setAttribute("Pressure", pressure)
        feature.setAttribute("Demand", demand)
        feature.setAttribute("Demand C", demandC)
    
    