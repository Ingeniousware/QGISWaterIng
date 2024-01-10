import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsLayerTreeLayer
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSvgMarkerSymbolLayer
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
            ("lastUpdate", QVariant.DateTime)
        ]
        
        self.features = ["lng","lat","serverKeyId","lastModified",
                        "name","description","z","head"]
        
        self.LayerType = "Point?crs="
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None        

    def initializeRepository(self):
        super(ReservoirNodeRepository, self).initializeRepository()      
       
        self.openLayers(":/plugins/QGISPlugin_WaterIng/images/reservoirLayer.svg", 12)
        self.createBackupLayer()
        
    def setDefaultValues(self, feature):
        name = "reservorName"
        description = "reservoir form QGIS"
        z = 0
        head = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)
        feature.setAttribute("Head[m]", head)

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

