import requests
from ..watering_utils import WateringUtils

from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest
from PyQt5.QtCore import QVariant, QFileInfo, QDateTime
from PyQt5.QtGui import QColor
from qgis.utils import iface
from datetime import datetime

class AbstractRepository():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.destCrs = QgsCoordinateReferenceSystem(3857)
        self.currentCRS = QgsCoordinateReferenceSystem(3857)
        self.Layer = None
        self.currentLayer = None
        self.ServerDict = {}
        self.OfflineDict = {}
        self.Response = None
        self.FieldDefinitions = None
        self.Attributes = None
        self.connectorToServer = None        
        self.numberLocalFieldsOnly = 1

    def setConnectorToServer(self, connector):
        self.connectorToServer = connector
        self.connectorToServer.localRepository = self

    def loadElements(self):
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

    def createElementLayerFromServerResponse(self, response):
        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("Point?crs=" + self.destCrs.authid(), "New Layer", "memory")
        self.currentLayer.dataProvider().addAttributes(fields)
        self.currentLayer.updateFields()
        
        response_data = response.json()["data"]

        for elementJSON in response_data:            
            self.addElementFromJSON(elementJSON)
            
        self.currentLayer.updateExtents()
    

    def getDateTimeNow(self):
        current_datetime = datetime.now()
        qdatetime = QDateTime(current_datetime)
        return QVariant(qdatetime)

    #When layer does not exists           
    def addElementFromJSON(self, elementJSON):
        try:
            element = [elementJSON[field] for field in self.features]

            feature = QgsFeature(self.currentLayer.fields())
            geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)

            self.currentLayer.startEditing()

            print(element)
            for i in range(len(self.field_definitions)- self.numberLocalFieldsOnly):
                feature.setAttribute(self.field_definitions[i][0], element[i+2])  
            
            feature.setAttribute("lastUpdate", self.getDateTimeNow())            
            self.currentLayer.addFeature(feature)
            #self.currentLayer.dataProvider().addFeature(feature)

            self.currentLayer.commitChanges()

        except ValueError:
              print("Error->" + ValueError)

    #When layer already exists
    def addElementFromSignalR(self, elementJSON):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        element = [elementJSON[field] for field in self.features]

        layer.startEditing()
         
        feature = QgsFeature(layer.fields())
        geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
        geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))

        feature.setGeometry(geometry)
        for i in range(len(self.field_definitions)):
            feature.setAttribute(self.field_definitions[i][0], element[i+2])

        feature['lastUpdate'] = self.getDateTimeNow()

        layer.addFeature(feature)
        layer.commitChanges()

    def AddNewElementFromMapInteraction(self, x, y):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        layer.startEditing()
         
        feature = QgsFeature(layer.fields())
        geometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        
        #we dont need to transform when we are adding element from the map
        # geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))

        feature.setGeometry(geometry)

        #TODO here we should call to add default values
        #for i in range(len(self.field_definitions)):
        #    feature.setAttribute(self.field_definitions[i][0], element[i+2])
        
        self.setDefaultValues(feature)
        feature['lastUpdate'] = self.getDateTimeNow()

        layer.addFeature(feature)
        layer.commitChanges()

        if self.connectorToServer:
            self.connectorToServer.addElementToServer(feature)

        return feature

    def deleteFeatureFromMapInteraction(self, feature):
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        self.Layer.startEditing()
        
        print("About to delete the feature ", feature.id(), " from ", self.LayerName)
        self.Layer.deleteFeature(feature.id())
        
        self.Layer.commitChanges()

        print("Changes after deleting feature are now done")
        if self.connectorToServer:
            self.connectorToServer.removeElementFromServer(feature)

        

    def setDefaultValues(self, feature):
        ...
        


    def initializeRepository(self):
        #loading element from the API
        serverResponse = self.loadElements()        
        #Adding elements to shapefile
        self.createElementLayerFromServerResponse(serverResponse)              
        #Write shapefile
        self.writeShp()

        

    def writeShp(self):
        #TODO check the use of writeAsVectorFormatV3 because writeAsVectorFormat has been depreciated
        writer = QgsVectorFileWriter.writeAsVectorFormat(self.currentLayer, self.StorageShapeFile, "utf-8", self.currentLayer.crs(), "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print(f"Shapefile for {self.LayerName} created successfully!")
        else:
            print("Error creating tanks Shapefile! ") #, QgsVectorFileWriter.errorMessage())

        
    def openLayers(self, layer_symbol, layer_size):
        element_layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")
        self.setElementSymbol(element_layer, layer_symbol, layer_size)
        element_layer.saveNamedStyle(self.FileQml)     
          
        if not element_layer.isValid():
            print("Error opening:", element_layer.dataProvider().error().message())
        else:
            QgsProject.instance().addMapLayer(element_layer, False)
            print("opened successfully:", element_layer.name())


    def setElementSymbol(self, layer, layer_symbol, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(layer_symbol))
        symbol.setSize(layer_size) 
        symbol.setColor(self.Color)
        if self.StrokeColor:
            symbol.symbolLayer(0).setStrokeColor(self.StrokeColor)
        layer.triggerRepaint()
    
    def updateFromServerToOffline(self, lastUpdatedFromServer):  
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        self.FieldDefinitions = [t[0] for t in self.field_definitions[1:-self.numberLocalFieldsOnly]]

        print(self.LayerName)
        print(self.FieldDefinitions)

        self.Attributes = self.features[1:]
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
    

    def updateFromOfflineToServer(self, lastUpdatedToServer):
        if self.connectorToServer:
            features = [feature for feature in self.Layer.getFeatures() if feature['lastUpdate'] > lastUpdatedToServer].sort(key=lambda element: element['lastUpdate'])          
            for feature in features:                                                    
                self.connectorToServer.addElementToServer(feature)



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
            attributes = [feature[self.FieldDefinitions[i]] for i in range(len(self.FieldDefinitions))]

            if len(attributes) > 2 and (not attributes[2]):
                attributes[2] = None
                
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
        
        
        for i, field in enumerate(self.FieldDefinitions):
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
        
        #print(f"Updating existing element in {self.LayerName}: {id}")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features:
            for i in range(len(self.FieldDefinitions)-self.numberLocalFieldsOnly):
                feature[self.FieldDefinitions[i]] = self.ServerDict[id][i]
            
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