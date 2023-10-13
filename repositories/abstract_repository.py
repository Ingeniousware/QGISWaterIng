import requests
from ..watering_utils import WateringUtils

from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from qgis.utils import iface

class AbstractRepository():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.destCrs = QgsCoordinateReferenceSystem(3857)
        self.Layer = None
        self.ServerDict = {}
        self.OfflineDict = {}
        self.Response = None
        self.Fields = None
        self.Attributes = None
        
    def loadElements(self):
        print("Am I Creating a layer?")
        params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        response =  requests.get(url, params=params_element, 
                            headers={'Authorization': "Bearer {}".format(self.Token)})  
        return response

    def setElementFields(self, fields_definitions):
        fields = QgsFields()
        for name, data_type in fields_definitions:
            fields.append(QgsField(name, data_type))
        return fields
        
    def loadElementFeatures(self, response, element_features):
        list_of_elements = []
        print(response)
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
    
    def updateFromServerToOffline(self):  
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        self.Fields = [t[0] for t in self.field_definitions[1:-4]]
        self.Attributes = self.features[3:]
        self.getServerDict()
        self.getOfflineDict()
        
        server_keys = set(self.ServerDict.keys())
        offline_keys = set(self.OfflineDict.keys())

        #Add Element
        for element_id in server_keys - offline_keys:
            self.addElement(element_id)
            
        #Delete Element
        for element_id in offline_keys - server_keys:
            self.deleteElement(element_id)

        #Update Element
        for element_id in server_keys & offline_keys:
            if self.ServerDict[element_id] != self.OfflineDict[element_id]:
                self.updateElement(element_id)
    
    def updateFromOfflineToServer(self):
        ...
           
    def updateAll(self):
        print("Update tool has been activated")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        self.Response = self.loadElements()
        
        self.getServerDict()
        self.getOfflineDict()
        
        self.updateFromServerToOffline()
        self.updateFromOfflineToServer()
    
    def getServerDict(self):
        self.Response = self.loadElements()
        data = self.Response.json()["data"]
        for element in data:
            attributes  = [element[self.Attributes[i]] for i in range(len(self.Attributes))]
            attributes.append(self.getTransformedCrs(element["lng"], element["lat"]))
    
            self.ServerDict[element["serverKeyId"]] = attributes
          
    def getOfflineDict(self):
        for feature in self.Layer.getFeatures():
            attributes = [feature[self.Fields[i]] for i in range(len(self.Fields))]
            
            if not attributes[2]:
                attributes[2] = ""
                
            geom = feature.geometry()
            point = geom.asPoint()
            attributes.append((point.x(), point.y()))

            self.OfflineDict[feature["ID"]] = attributes
                
    def addElement(self, id):
        
        print(f"Adding element in {self.LayerName}: {id}")
        
        feature = QgsFeature(self.Layer.fields())
        feature["ID"] = id
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.ServerDict[id][-1][0],
                                                               self.ServerDict[id][-1][1])))
        
        self.Layer.startEditing()
        
        
        for i, field in enumerate(self.Fields):
            feature[field] = self.ServerDict[id][i]

        self.Layer.addFeature(feature)
        self.Layer.commitChanges()
    
    def deleteElement(self, id):
        print(f"Deleting existing element in {self.LayerName}: {id}")
        
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features_to_delete = [feature.id() for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features_to_delete:
            self.Layer.deleteFeature(feature)
            
        self.Layer.commitChanges()
        
    def updateElement(self, id):
        
        print(f"Updating existing element in {self.LayerName}: {id}")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features:
            for i in range(len(self.Fields)):
                feature[self.Fields[i]] = self.ServerDict[id][i]
            
            #update geometry
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.ServerDict[id][-1][0],
                                                               self.ServerDict[id][-1][1])))
            
            self.Layer.updateFeature(feature)
        
        self.Layer.commitChanges()
        
    def getTransformedCrs(self, lng, lat):
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")   # Web Mercator
        
        geom = QgsGeometry.fromPointXY(QgsPointXY(lng, lat))
        geom.transform(QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance()))
        point = geom.asPoint()
        
        return (point.x(), point.y())