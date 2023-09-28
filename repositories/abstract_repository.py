import requests

from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class AbstractRepository():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.destCrs = QgsCoordinateReferenceSystem(3857)
        
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
            features = [element[field] for field in element_features]
            features.extend([0] * 4)
            list_of_elements.append(features)
        return list_of_elements
    
    def createElementLayer(self, element_features, list_of_elements, fields, fields_definitions):
        layer = QgsVectorLayer("Point?crs=" + self.destCrs.authid(), "New Layer", "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()
        
        for element in list_of_elements:
            feature = QgsFeature(layer.fields())
            geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)
            for i in range(len(fields_definitions)):
                feature.setAttribute(fields_definitions[i][0], element[i+2])
            layer.dataProvider().addFeature(feature)
            
        return layer 
        
    def initializeRepository(self):
        ...
    
    def writeShp(self, layer):
        writer = QgsVectorFileWriter.writeAsVectorFormat(layer, self.StorageShapeFile, "utf-8", layer.crs(), "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print("Shapefile created successfully!")
        else:
            print("Error creating tanks Shapefile!")
        
    def openLayers(self, layer_symbol, layer_size):
        element_layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")
        self.setElementSymbol(element_layer, layer_symbol, layer_size)
        
        if not element_layer.isValid():
            print("Error opening:", element_layer.dataProvider().error().message())
        else:
            root = QgsProject.instance().layerTreeRoot()
            shapeGroup = root.findGroup("WaterIng Network Layout")
            shapeGroup.insertChildNode(1, QgsLayerTreeLayer(element_layer))

            QgsProject.instance().addMapLayer(element_layer, False)

            #QgsProject.instance().addMapLayer(element_layer)
            print("opened successfully:", element_layer.name())

    def setElementSymbol(self, layer, layer_symbol, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(layer_symbol))
        symbol.setSize(layer_size) 
        symbol.setColor(QColor.fromRgb(23, 61, 108))
        layer.triggerRepaint()