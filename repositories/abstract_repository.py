import requests

from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class AbstractRepository():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK

    def loadElements(self):
        params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        return requests.get(self.UrlGet, params=params_element, headers={'Authorization': "Bearer {}".format(self.Token)})  

    def setElementFields(self, fields_definitions):
        fields = QgsFields()
        for name, data_type in fields_definitions:
            fields.append(QgsField(name, data_type))
        return fields
    
    def loadElementFeatures(self, response, element_features):
        list_of_elements = []
        response_data = response.json()["data"]
        for element in response_data:
            list_of_elements.append(element_features)
        return list_of_elements
    
    def createElementShp(self):
        ...
        
    def openLayers(self, layer_symbol, layer_size):
        element_layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")
        self.setElementSymbol(element_layer, layer_symbol, layer_size)
        
        if not element_layer.isValid():
            print("Error opening:", element_layer.dataProvider().error().message())
        else:
            QgsProject.instance().addMapLayer(element_layer)
            print("opened successfully:", element_layer.name())


    def setElementSymbol(self, layer, layer_symbol, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(layer_symbol))
        symbol.setSize(layer_size) 
        symbol.setColor(QColor.fromRgb(23, 61, 108))
        layer.triggerRepaint()