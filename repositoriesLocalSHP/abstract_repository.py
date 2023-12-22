import requests
import os
import uuid
from ..watering_utils import WateringUtils
from datetime import datetime
import pytz

from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest
from PyQt5.QtCore import QFileInfo, QDateTime
from PyQt5.QtGui import QColor
from qgis.utils import iface

class AbstractRepository():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.destCrs = QgsCoordinateReferenceSystem(3857)
        self.currentCRS = QgsCoordinateReferenceSystem(3857)
        self.Layer = None
        self.ServerDict = {}
        self.OfflineDict = {}
        self.Response = None
        self.FieldDefinitions = None
        self.Attributes = None
        self.toAddFeatures = None
        self.pr = None
        self.connectorToServer = None
        self.currentLayer = None
        self.numberLocalFieldsOnly = 1

    def initializeRepository(self):
        #loading element from the API
        serverResponse = self.loadElements()        
        #Adding elements to shapefile
        self.createElementLayerFromServerResponse(serverResponse)              
        #Write shapefile
        self.writeShp()
        
    def setConnectorToServer(self, connector):
        self.connectorToServer = connector
        self.connectorToServer.localRepository = self
        
    def unsetConnectorToServer(self):
        self.connectorToServer = None

    def loadElements(self):
        params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        response =  requests.get(url, params=params_element, 
                            headers={'Authorization': "Bearer {}".format(os.environ.get('TOKEN'))})  
        return response

    def setElementFields(self, fields_definitions):
        fields = QgsFields()
        for name, data_type in fields_definitions:
            fields.append(QgsField(name, data_type))
        return fields

    def createElementLayerFromServerResponse(self, response):
        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("Point?crs=" + self.destCrs.authid(), "New Layer", "memory")
        self.pr = self.currentLayer.dataProvider()
        self.pr.addAttributes(fields)
        self.currentLayer.updateFields()
        
        response_data = response.json()["data"]

        self.toAddFeatures = []
        for elementJSON in response_data:            
            self.addElementFromJSON(elementJSON)
        
        self.pr.addFeatures(self.toAddFeatures)
        self.currentLayer.updateExtents()
        
        features = self.currentLayer.getFeatures()
        
        self.currentLayer.attributeValueChanged.connect(
                        lambda feature_id, attribute_index, new_value, layer=self.Layer: 
                        WateringUtils.onChangesInAttribute(feature_id, attribute_index, new_value, layer)
                )
        
        self.currentLayer.geometryChanged.connect(
                    lambda feature_id, old_geometry, new_geometry, layer=self.Layer: 
                    WateringUtils.onGeometryChange(feature_id, old_geometry, new_geometry, layer)
                )
        
        #PRINT FEATURES
        #print("FEATURES")
        # Iterate through the features and print their attributes and geometry
        #for feature in features:
            #print(f'Feature ID: {feature.id()}')
            #print(f'Attributes: {feature.attributes()}')
            #print(f'Geometry: {feature.geometry().asWkt()}')  # Print geometry as Well-Known Text (WKT)

        
    #When layer does not exists           
    def addElementFromJSON(self, elementJSON):
        try:
            element = [elementJSON[field] for field in self.features]

            feature = QgsFeature(self.currentLayer.fields())
            geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)

            #print(element)
            for i in range(len(self.field_definitions)- self.numberLocalFieldsOnly):
                #print("ATTTRIBUTE: ", self.field_definitions[i][0], "EEMTN", element[i+2])
                feature.setAttribute(self.field_definitions[i][0], element[i+2])
            
            #print("Datetime: ", datetime.now())
            feature.setAttribute('lastUpdate', WateringUtils.getDateTimeNow())
            #self.currentLayer.dataProvider().addFeature(feature)
            self.toAddFeatures.append(feature)
        except ValueError:
              print("Error->" + ValueError)

    #When layer already exists
    def addElementFromSignalR(self, elementJSON):
        print("Adding from signal r")
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        element = [elementJSON[field] for field in self.features]

        layer.startEditing()
        print("reached first")
        feature = QgsFeature(layer.fields())
        geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
        geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
        print("reached second")

        feature.setGeometry(geometry)
        print("field_definitions: ", self.field_definitions)
        print("element: ", element)
        
        for i in range(len(self.field_definitions) - 1):
            feature.setAttribute(self.field_definitions[i][0], element[i+1])
            print("element i + 1", element[i+1])
            print("field definition position: ", self.field_definitions[i][0])
            
        print("reached third")

        feature.setAttribute('lastUpdate', WateringUtils.getDateTimeNow())

        print("Adding feature ", feature, "to server")

        layer.addFeature(feature)
        layer.commitChanges()
        layer.triggerRepaint()

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
        
        id = str(uuid.uuid4())
        temp_id = id[:10]
        
        feature.setAttribute("ID", temp_id)
        
        self.setDefaultValues(feature)
        feature.setAttribute("Last Mdf", WateringUtils.getDateTimeNow())
        
        layer.addFeature(feature)
        
        commit_success = layer.commitChanges()

        if commit_success:
            print("Changes committed successfully.")
            print("Adding to server...")
            if self.connectorToServer:
                print("Connection established, adding ID in server locally")
                self.connectorToServer.addElementToServer(feature)
            else: 
                print("No connection to send to server")
        else:
            print("Failed to commit changes.")

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

        

    def writeShp(self):
        writer = QgsVectorFileWriter.writeAsVectorFormat(self.currentLayer, self.StorageShapeFile, "utf-8", self.currentLayer.crs(), "ESRI Shapefile")
        
        if writer[0] == QgsVectorFileWriter.NoError:
            print(f"Shapefile for {self.LayerName} created successfully!")
        else:
            print("Error creating tanks Shapefile!")
        
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
    
    def generalUpdate(self, lastUpdated):  
        self.ServerDict = {}
        self.OfflineDict = {}
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        self.FieldDefinitions = [t[0] for t in self.field_definitions[1:-self.numberLocalFieldsOnly]]

        self.Attributes = self.features[3:]
        self.getServerDict(lastUpdated) 
        self.getOfflineDict(lastUpdated)
        
        server_keys = set(self.ServerDict.keys())
        offline_keys = set(self.OfflineDict.keys())

        # Deleting in BackupLayerElements from server
        self.deleteElementsInBackupLayers(lastUpdated)
        
        #Add Element from server to offline
        for element_id in server_keys - offline_keys:
            self.addElementToOffline(element_id)
        
        #Add offline-elements from offline to server
        self.updateAddElementToServer()
        
        # Deleted elements from server
        self.handleDeletedElementsFromServer()
           
        #Update Element
        for element_id in server_keys & offline_keys:
            if self.ServerDict[element_id][1:] != self.OfflineDict[element_id][1:]:
                self.updateElement(element_id, lastUpdated)

    def deleteElementsInBackupLayers(self, lastUpdatedToServer):
        backup_layer_name = self.LayerName + "_backup.shp"
        
        backup_file_path = os.path.dirname(self.StorageShapeFile) + "/" + backup_layer_name
        layer = QgsVectorLayer(backup_file_path, "layer", "ogr")
        
        if not layer.isValid():
            print(f"Failed to load layer: {backup_layer_name}")
            return 

        current_time = WateringUtils.getDateTimeNow()
        for feature in layer.getFeatures():
            if feature['lastUpdate'] > lastUpdatedToServer: 
                layer.changeAttributeValue(feature.id(), layer.fields().indexFromName('lastUpdate'), current_time)
                self.connectorToServer.removeElementFromServer(feature["ID"])
                
    def getElementsIdsFromLayer(self, layer):
        ids = []
        for feature in layer.getFeatures():
            ids.append(feature["ID"])
        return ids

    def cleanLayer(self, layer):
        layer.startEditing()
        all_feature_ids = [feature.id() for feature in layer.getFeatures()]

        success = layer.dataProvider().deleteFeatures(all_feature_ids)
    
        if success:
            layer.commitChanges()
            print("All features deleted and changes committed.")
        else:
            layer.rollback()
            print("Changes were rolled back.")
    
    def getServerDict(self, lastUpdated):
        self.Response = self.loadElements()

        data = self.Response.json()["data"]
        for element in data:
            attributes  = [element[self.Attributes[i]] for i in range(len(self.Attributes))]
            attributes.append(self.getTransformedCrs(element["lng"], element["lat"]))    
            self.ServerDict[element["serverKeyId"]] = attributes
        
    def getOfflineDict(self, lastUpdated):
        for feature in self.Layer.getFeatures():
            attributes = [feature[self.FieldDefinitions[i]] for i in range(len(self.FieldDefinitions))]

            print(attributes)
            
            if len(attributes) > 2 and (not attributes[2]):
                attributes[2] = None
                
            geom = feature.geometry()
            point = geom.asPoint()
            attributes.append((point.x(), point.y()))

            self.OfflineDict[feature["ID"]] = attributes

    def addElementToOffline(self, id):
        print(f"Adding element in {self.LayerName}: {id}")
        
        feature = QgsFeature(self.Layer.fields())
        feature.setAttribute("ID", id)
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.ServerDict[id][-1][0],
                                                               self.ServerDict[id][-1][1])))
        
        self.Layer.startEditing()
        
        for i, field in enumerate(self.FieldDefinitions):
            feature[field] = self.ServerDict[id][i]
        
        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())
        
        self.Layer.addFeature(feature)
        self.Layer.commitChanges()
    
    def handleDeletedElementsFromServer(self):
        elements_deleted_from_server = [id for id in self.OfflineDict if (len(str(id)) != 10) and id not in self.ServerDict]
        
        if elements_deleted_from_server:
            ids_to_delete = [feature.id() for feature in self.Layer.getFeatures() if feature["ID"] in elements_deleted_from_server]
            
            self.Layer.startEditing()
            
            self.Layer.deleteFeatures(ids_to_delete)

            self.Layer.commitChanges()
        
    def updateAddElementToServer(self):
        features_to_add= [feature for feature in self.Layer.getFeatures() if (len(str(feature['ID'])) == 10)
                          and (feature['ID'] in self.OfflineDict)]

        if self.connectorToServer:
            if features_to_add:
                for feature in features_to_add:
                    self.connectorToServer.addElementToServer(feature)
        else:
            print("no connector")

    def deleteElement(self, id, lastUpdatedFromServer):
        print("ID in delete element: ", id)
        print(f"Deleting existing element in {self.LayerName}: {id}")
        
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features_to_delete = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features_to_delete:
            if id in self.ServerDict:
                if feature['lastUpdate'] < self.ServerDict[id][0]:
                    self.Layer.deleteFeature(feature.id())
            
        self.Layer.commitChanges()

        
    def updateElement(self, id, lastUpdated):
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features:
            if (id in self.ServerDict) and (id in self.OfflineDict):
                print("time at server -> ", self.ServerDict[id][0], " time at offline -> ", feature['lastUpdate'])
                if self.ServerDict[id][0] > feature['lastUpdate']:
                    print("option 1 -> from server to offline")
                    self.Layer.startEditing()

                    attrs = {}

                    for i in range(len(self.FieldDefinitions) - self.numberLocalFieldsOnly):
                        field_index = self.Layer.fields().indexOf(self.FieldDefinitions[i])
                        attrs[field_index] = self.ServerDict[id][i]

                    last_update_index = self.Layer.fields().indexOf('lastUpdate')
                    attrs[last_update_index] = str(WateringUtils.getDateTimeNow())

                    self.Layer.dataProvider().changeAttributeValues({feature.id(): attrs})

                    new_geometry = QgsGeometry.fromPointXY(QgsPointXY(self.ServerDict[id][-1][0], self.ServerDict[id][-1][1]))
                    self.Layer.dataProvider().changeGeometryValues({feature.id(): new_geometry})

                    self.Layer.commitChanges()
                    
                # If online feature has been modified and it´s already in the server
                elif (len(str(feature['ID'])) == 36):
                    print("option 2 -> from offline to server")
                    if self.connectorToServer:
                        self.connectorToServer.addElementToServer(feature)
        
        self.Layer.commitChanges()
        
    def getTransformedCrs(self, lng, lat):
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")   # Web Mercator
        
        geom = QgsGeometry.fromPointXY(QgsPointXY(lng, lat))
        geom.transform(QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance()))
        point = geom.asPoint()
        
        return (point.x(), point.y())
        

    def createBackupLayer(self):
        name = self.LayerName + "_backup"
        backup_layer_path = os.path.dirname(self.StorageShapeFile) + "/" + name + ".shp"
        
        fields = self.setElementFields(self.field_definitions)
        backup_layer = QgsVectorLayer(self.LayerType + self.destCrs.authid(), "New Layer", "memory")
        pr = backup_layer.dataProvider()
        pr.addAttributes(fields)
        backup_layer.updateFields()
        
        writer = QgsVectorFileWriter.writeAsVectorFormat(backup_layer, backup_layer_path, "utf-8", self.currentLayer.crs(), "ESRI Shapefile")
        if writer[0] == QgsVectorFileWriter.NoError:
            print(f"Shapefile for {self.LayerName} created successfully!")
        else:
            print(f"Error creating {self.LayerName} Shapefile!")
        
        key = "backup_layer_path" + self.LayerName
        WateringUtils.setProjectMetadata(key, backup_layer_path)
        value = WateringUtils.getProjectMetadata(key)
        
    def transformTimezone(self, time):
        
        input_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        output_format = "%Y/%m/%d %H:%M:%S.%f"
        
        original_datetime = datetime.strptime(time, input_format)
        
        target_timezone = pytz.timezone('UTC')
        target_datetime = original_datetime.astimezone(target_timezone)
        
        formatted_datetime_str = target_datetime.strftime(output_format)
        
        return formatted_datetime_str
    