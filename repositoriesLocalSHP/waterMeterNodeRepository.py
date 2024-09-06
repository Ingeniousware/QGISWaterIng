import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from qgis.core import QgsSvgMarkerSymbolLayer
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class WaterMeterNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(WaterMeterNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterMeter"
        self.StorageShapeFile = os.path.join(project_path, "watering_waterMeter.shp")
        self.LayerName = "watering_waterMeter"
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Meterstate", QVariant.Double),
            ("FunctType", QVariant.Double),
            ("LastDate", QVariant.String),
            ("NodeID", QVariant.String),
            ("lastUpdate", QVariant.String)
        ]
        
        self.features = ["lng", "lat", "serverKeyId","lastModified","name", "description","meterstate",
                                "functionalType","lastReadDateTime", "connectedToNodeFK"]
        
        self.LayerType = "Point?crs="
        
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None
        
    def initializeRepository(self):
        super(WaterMeterNodeRepository, self).initializeRepository()   
        self.openLayers(":/plugins/QGISPlugin_WaterIng/images/Icon_waterMeter_GT.svg", 12)
        self.createBackupLayer()
        
    def setElementSymbol(self, layer, path_to_gif, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()

        symbol_layer = QgsSvgMarkerSymbolLayer(path_to_gif, layer_size)
        #symbol_layer.setFrameRate(1)
        symbol.changeSymbolLayer(0, symbol_layer)

        symbol.setColor(self.Color)
        if self.StrokeColor:
            symbol.symbolLayer(0).setStrokeColor(self.StrokeColor)
        layer.triggerRepaint()
        
    def setDefaultValues(self, feature):
        name = "waterMeterName"
        description = "water meter from QGIS"
        meterstate = 0
        functionalType = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Meterstate", meterstate)
        feature.setAttribute("FunctType", functionalType)     