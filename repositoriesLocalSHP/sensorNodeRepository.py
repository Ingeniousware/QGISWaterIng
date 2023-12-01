import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsAnimatedMarkerSymbolLayer
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class SensorNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(SensorNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/SensorStation"
        self.StorageShapeFile = os.path.join(project_path, "watering_sensors.shp")
        self.LayerName = "watering_sensors"
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("lastUpdate", QVariant.String)
        ]
    
        self.features = ["lng", "lat", "serverKeyId", "lastModified","name", "description", "z"]
        
        self.LayerType = "Point?crs="
        self.Color = QColor.fromRgb(255, 255, 255)
        self.StrokeColor = QColor.fromRgb(23, 61, 108)
        self.currentLayer = None

    def initializeRepository(self):
        super(SensorNodeRepository, self).initializeRepository()   
        self.openLayers(':/plugins/QGISPlugin_WaterIng/images/sensorLayer.gif', 30)
        self.createBackupLayer()

    def setDefaultValues(self, feature):
        name = "sensorName"
        description = "sensor form QGIS"
        z = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)        
    
    def setElementSymbol(self, layer, path_to_gif, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()

        symbol_layer = QgsAnimatedMarkerSymbolLayer(path_to_gif, layer_size)
        symbol_layer.setFrameRate(1)
        symbol.changeSymbolLayer(0, symbol_layer)

        symbol.setColor(self.Color)
        if self.StrokeColor:
            symbol.symbolLayer(0).setStrokeColor(self.StrokeColor)
        layer.triggerRepaint()
