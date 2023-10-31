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
        self.LayerName = "watering_valves"
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        self.field_definitions = None

        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Diameter", QVariant.Double),
            ("minorLossC", QVariant.Double),
            ("initialSta", QVariant.Double),
            ("typeValvul", QVariant.Double),
            ("setting", QVariant.Double),
            ("lastupdated", QVariant.DateTime)
        ]
        
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description", "z",
                         "diameter", "minorLossCoef", "initialStatus", "typeValvule", "setting"]
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None
     
    def initializeRepository(self):
        super(ValveNodeRepository, self).initializeRepository()  
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Cross2, 6)

    def setDefaultValues(self, feature):
        name = "valveName"
        description = "valve form QGIS"
        z = 0
        typeValve = 1
        minorLossCoef = 0
        diameter = 0
        initialStatus = 0
        temp = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)
        feature.setAttribute("Diameter", diameter)
        feature.setAttribute("minorLossC", minorLossCoef)
        feature.setAttribute("initialSta", initialStatus)
        feature.setAttribute("typeValvul", typeValve)
        feature.setAttribute("Temp Field", temp)
    