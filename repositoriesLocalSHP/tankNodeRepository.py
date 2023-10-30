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
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
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
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None

    def initializeRepository(self):
        super(TankNodeRepository, self).initializeRepository() 
        self.openLayers(QgsSimpleMarkerSymbolLayerBase.Pentagon, 6)
    

    def setDefaultValues(self, feature):
        name = "tankName"
        description = "tank form QGIS"
        z = 0
        initialLevel = 3
        minimumLevel = 1
        maximumLevel = 9
        minimumVolume = 2
        nominalDiameter = 25
        canOverflow = True

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)
        feature.setAttribute("Init. Lvl", initialLevel)
        feature.setAttribute("Min. Lvl", minimumLevel) 
        feature.setAttribute("Max. Lvl", maximumLevel) 
        feature.setAttribute("Min. Vol.", minimumVolume) 
        feature.setAttribute("Diameter", nominalDiameter)
        feature.setAttribute("Overflow", canOverflow)  