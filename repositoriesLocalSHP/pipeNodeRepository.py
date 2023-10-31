import os
import requests
from .abstract_repository import AbstractRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsLayerTreeLayer
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, edit
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from datetime import datetime

class PipeNodeRepository(AbstractRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(PipeNodeRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/WaterPipe"
        self.StorageShapeFile = os.path.join(project_path, "watering_pipes.shp")
        self.LayerName = "watering_pipes"
        self.FileQml =  project_path + "/" + self.LayerName + ".qml"
        #Setting shapefile fields 
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Diameter", QVariant.Double),
            ("Length", QVariant.Double),
            ("Rough.A", QVariant.Double),
            ("C(H.W.)", QVariant.Double),
            ("Up-Node", QVariant.String),
            ("Down-Node", QVariant.String),
            ("lastupdated", QVariant.DateTime)
        ]
        
        self.features = ["serverKeyId", "lastModified", "name", "description", "diameterInt",
                           "length", "roughnessAbsolute", "roughnessCoefficient", "nodeUpName", "nodeDownName"]
        
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        


    def setElementSymbol(self, layer, layer_symbol, layer_size):
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setColor(QColor.fromRgb(13, 42, 174))
        symbol_layer.setWidth(0.7)
        layer.renderer().setSymbol(symbol)
        layer.saveNamedStyle(self.FileQml)

   
    def getServerDict(self):
        self.Response = self.loadElements()
        data = self.Response.json()["data"]
        for element in data:
            attributes  = [element[self.Attributes[i]] for i in range(len(self.Attributes))]  
            points = [QgsPointXY(vertex['lng'], vertex['lat']) for vertex in element["vertices"]]
            geometry = QgsGeometry.fromPolylineXY(points)
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))  
            attributes.append(geometry)
            self.ServerDict[element["serverKeyId"]] = attributes


    def getOfflineDict(self):
        for feature in self.Layer.getFeatures():
            attributes = [feature[self.FieldDefinitions[i]] for i in range(len(self.FieldDefinitions))]

            if len(attributes) > 2 and (not attributes[2]):
                attributes[2] = None
                
            geom = feature.geometry()
            attributes.append(geom)

            self.OfflineDict[feature["ID"]] = attributes


    def createElementLayerFromServerResponse(self, response):

        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("LineString?crs=" + self.destCrs.authid(), "Line Layer", "memory")
        self.currentLayer.dataProvider().addAttributes(fields)
        self.currentLayer.updateFields()
        
        response_data = response.json()["data"]

        for elementJSON in response_data:            
            self.addElementFromJSON(elementJSON)


    def addElementFromJSON(self, elementJSON):
        try:
            element = [elementJSON[field] for field in self.features]

            feature = QgsFeature(self.currentLayer.fields())
            points = [QgsPointXY(vertex['lng'], vertex['lat']) for vertex in elementJSON["vertices"]]
            geometry = QgsGeometry.fromPolylineXY(points)
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)

            print(element)
            for i in range(len(self.field_definitions)- self.numberLocalFieldsOnly):
                feature.setAttribute(self.field_definitions[i][0], element[i])
            
            feature['lastUpdated'] = datetime.now()
            self.currentLayer.dataProvider().addFeature(feature)
        except ValueError:
              print("Error->" + ValueError)



    #When layer already exists
    def addElementFromSignalR(self, elementJSON):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        element = [elementJSON[field] for field in self.features]

        layer.startEditing()
         
        feature = QgsFeature(layer.fields())
        points = [QgsPointXY(vertex['lng'], vertex['lat']) for vertex in elementJSON["vertices"]]
        geometry = QgsGeometry.fromPolylineXY(points)
        geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))

        feature.setGeometry(geometry)
        for i in range(len(self.field_definitions)):
            feature.setAttribute(self.field_definitions[i][0], element[i+2])

        feature['lastUpdated'] = datetime.now()

        layer.addFeature(feature)
        layer.commitChanges()


    def addElement(self, id):
        
        print(f"Adding element in {self.LayerName}: {id}")
        print(self.Layer.fields())
        
        feature = QgsFeature(self.Layer.fields())
        feature["ID"] = id
        feature.setGeometry(self.ServerDict[id][-1])
        
        self.Layer.startEditing()
        
        
        for i, field in enumerate(self.FieldDefinitions):
            feature[field] = self.ServerDict[id][i]

        self.Layer.addFeature(feature)
        self.Layer.commitChanges()


    def updateElement(self, id):
        
        print(f"Updating existing element in {self.LayerName}: {id}")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features:
            for i in range(len(self.FieldDefinitions)-self.numberLocalFieldsOnly):
                feature[self.FieldDefinitions[i]] = self.ServerDict[id][i]
            
            #update geometry
            feature.setGeometry(self.ServerDict[id][-1])
            
            self.Layer.updateFeature(feature)
        
        self.Layer.commitChanges()


    def AddNewElementFromMapInteraction(self, vertexs, upnode, downnode):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        layer.startEditing()

        feature = QgsFeature(layer.fields())
        points = [QgsPointXY(vertex.x(), vertex.y()) for vertex in vertexs]
        g = QgsGeometry.fromPolylineXY(points)
        feature.setGeometry(g)

        self.setDefaultValues(feature)

        layer.addFeature(feature)
        layer.commitChanges()

        if self.connectorToServer:
            self.connectorToServer.addElementToServer(feature)

        return feature