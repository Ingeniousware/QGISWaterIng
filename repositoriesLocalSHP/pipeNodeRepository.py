import os
import requests
from .abstract_repository import AbstractRepository
from ..watering_utils import WateringUtils

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsLayerTreeLayer
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsSymbol, edit
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from qgis.utils import iface

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
            ("lastUpdate", QVariant.String)
        ]
        
        self.features = ["serverKeyId", "lastModified", "name", "description", "diameterInt",
                           "length", "roughnessAbsolute", "roughnessCoefficient", "nodeUpName", "nodeDownName"]
        
        self.LayerType = "LineString?crs="
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        
        self.lastUpdatedToServer = None
        self.PipeServerDict = {}
        self.PipeOfflineDict = {}
        
    def initializeRepository(self):
        super(PipeNodeRepository, self).initializeRepository() 
        self.openLayers(None, 0.7) 
        self.createBackupLayer()

    def setElementSymbol(self, layer, layer_symbol, layer_size):
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setColor(QColor.fromRgb(13, 42, 174))
        symbol_layer.setWidth(layer_size)
        layer.renderer().setSymbol(symbol)
        layer.saveNamedStyle(self.FileQml)
        layer.triggerRepaint()

    def createElementLayerFromServerResponse(self, serverResponse):
        print("CREATING PIPES")
        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("LineString?crs=" + self.destCrs.authid(), "Line Layer", "memory")
        self.currentLayer.dataProvider().addAttributes(fields)
        self.currentLayer.updateFields()
        
        response_data = serverResponse.json()["data"]

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

            self.currentLayer.startEditing()

            print(element)
            for i in range(len(self.field_definitions)- self.numberLocalFieldsOnly):
                feature.setAttribute(self.field_definitions[i][0], element[i])

            feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())            
            self.currentLayer.addFeature(feature)

            self.currentLayer.commitChanges()

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

        print("pipes adding")
        print("field_definitions: ", self.field_definitions)
        print("element: ", element)
        feature.setGeometry(geometry)
        
        for i in range(len(self.field_definitions) - 1):
            feature.setAttribute(self.field_definitions[i][0], element[i])
            print("element i + 1", element[i])
            print("field definition position: ", self.field_definitions[i][0])

        #feature['lastUpdate'] = WateringUtils.getDateTimeNow()
        
        feature.setAttribute('lastUpdate', WateringUtils.getDateTimeNow())
        
        print("Adding feature ", feature, "to server")
        
        layer.addFeature(feature)
        layer.commitChanges()
        layer.triggerRepaint()


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
        
        #print(f"Updating existing element in {self.LayerName}: {id}")
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

        feature['lastUpdate'] = WateringUtils.getDateTimeNow()
        
        layer.addFeature(feature)
        layer.commitChanges()

        if self.connectorToServer:
            self.connectorToServer.addElementToServer(feature)

        return feature
    
    #Pipes update
    
    def generalUpdate(self, lastUpdated):
        print("updating PIPE")
        self.PipeServerDict = {}
        self.PipeOfflineDict = {}
        
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        self.Layer.attributeValueChanged.connect(
                        lambda feature_id, attribute_index, new_value, layer=self.Layer: 
                        WateringUtils.onChangesInAttribute(feature_id, attribute_index, new_value, layer)
                )
        
        self.FieldDefinitions = [t[0] for t in self.field_definitions[1:-1]]
        
        self.Attributes = self.features[1:]
        self.getPipeServerDict(lastUpdated)
        self.getPipeOfflineDict(lastUpdated)
        
        server_keys = set(self.PipeServerDict.keys())
        offline_keys = set(self.PipeOfflineDict.keys())

        # Deleting in Pipes BackupLayerElements from server
        self.deleteElementsInBackupLayers(lastUpdated)
        
        #Add Element from server to offline
        for element_id in server_keys - offline_keys:
            self.addPipeToOffline(element_id)
        
        # Retrieve pipes to be added to online
        self.addPipesToOnline()

        #Update Element
        for element_id in server_keys & offline_keys:
            if self.PipeServerDict[element_id] != self.PipeOfflineDict[element_id]:
                print("This: ", self.PipeServerDict[element_id], "Diff from this: ", self.PipeOfflineDict[element_id])
                self.updateExistingPipe(element_id, lastUpdated)
                
    def getPipeServerDict(self):
        self.PipeResponse = self.loadElements()
        data = self.PipeResponse.json()["data"]
        for element in data:
            attributes  = [element[self.Attributes[i]] for i in range(len(self.Attributes))]
            points = [self.getPipeTransformedCrs(QgsPointXY(vertex['lng'], vertex['lat'])) for vertex in element["vertices"]]
            attributes.append(self.timeAtUpdate)
            attributes.append(points)
            self.PipeServerDict[element["serverKeyId"]] = attributes
            
    def getPipeOfflineDict(self):
        for feature in self.Layer.getFeatures():
            attributes = [feature[self.FieldDefinitions[i]] for i in range(len(self.FieldDefinitions))]
            
            if not attributes[2]:
                attributes[2] = ""

            attributes.append(self.timeAtUpdate)
            
            geom = feature.geometry()
            points = geom.asMultiPolyline()
            attributes.append([point for point in points])
            
            attributes[-1] = attributes[-1][0]
            self.PipeOfflineDict[feature["ID"]] = attributes
    
    def addPipesToOnline(self):
        features_to_add= [feature for feature in self.Layer.getFeatures() if len(feature['ID']) == 10]
        print("features to add: ", features_to_add)
        
        if self.connectorToServer:
            print("has connector")
            for feature in features_to_add:
                print("adding feature: ", feature)
                self.connectorToServer.addElementToServer(feature)
        else:
            print("no connector")
        
    def addPipeToOffline(self, id):
        print(f"Adding element in {self.LayerName}: {id}")
        
        feature = QgsFeature(self.Layer.fields())
        feature["ID"] = id
        feature["lastUpdate"] = self.timeAtUpdate
        
        feature.setGeometry(QgsGeometry.fromPolylineXY(self.PipeServerDict[id][-1]))
        
        self.Layer.startEditing()
        
        for i, field in enumerate(self.FieldDefinitions):
            feature[field] = self.PipeServerDict[id][i]
        
        
        self.Layer.addFeature(feature)
        self.Layer.commitChanges()
    
    def updateExistingPipe(self, id, lastUpdated):
        #print(f"Updating existing element in {self.LayerName}: {id}")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features:
            if id in self.PipeServerDict:
                if feature['lastUpdate'] < self.PipeServerDict[id][0]:
                    print("option 1->updating from server to local in pipes: ", self.Layer, " ", feature)
                    for i in range(len(self.FieldDefinitions)):
                        feature[self.FieldDefinitions[i]] = self.PipeServerDict[id][i]
                        
                    feature["lastupdate"] = self.timeAtUpdate
                    #update geometry
                    feature.setGeometry(QgsGeometry.fromPolylineXY(self.PipeServerDict[id][-1]))
                    
                    self.Layer.updateFeature(feature)
                # If online feature has been modified and it´s already in the server
                elif feature['lastUpdate'] > lastUpdated and len(str(feature['ID'])) == 36:
                    print("option 2->updating from local to server in pipes" , feature, " ", self.Layer)
                    if self.connectorToServer:
                        self.connectorToServer.addElementToServer(feature)
                        
        self.Layer.commitChanges()
        
    def getPipeTransformedCrs(self, point):
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")   # Web Mercator
        
        geom = QgsGeometry.fromPointXY(point)
        geom.transform(QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance()))
        point = geom.asPoint()
        
        return QgsPointXY(point.x(), point.y())
    