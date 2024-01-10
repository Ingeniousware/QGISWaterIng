import os
import requests
import uuid
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
            ("lastUpdate", QVariant.DateTime)
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
        id_already_in_offline = self.hasFeatureWithId(layer, elementJSON['serverKeyId'])
        
        if not id_already_in_offline:
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
        
        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())
        feature.setAttribute("Last Mdf", str(WateringUtils.getDateTimeNow()))
        
        id = str(uuid.uuid4())
        temp_id = id[:10]
        
        feature.setAttribute("ID", temp_id)

        layer.addFeature(feature)
        layer.commitChanges()

        if self.connectorToServer:
            self.connectorToServer.addElementToServer(feature)

        return feature
    
    #Pipes update
    
    def generalUpdate(self, lastUpdated):
        print("updating PIPE")
        lastUpdated = self.adjustedDatetime(lastUpdated)
        self.PipeServerDict = {}
        self.PipeOfflineDict = {}
        
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        self.Layer.attributeValueChanged.connect(
                        lambda feature_id, attribute_index, new_value, layer=self.Layer: 
                        WateringUtils.onChangesInAttribute(feature_id, attribute_index, new_value, layer)
                )
        
        self.Layer.geometryChanged.connect(
                    lambda feature_id, old_geometry, new_geometry, layer=self.Layer: 
                    WateringUtils.onGeometryChange(feature_id, old_geometry, new_geometry, layer)
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
            if self.PipeServerDict[element_id][1:1] != self.PipeOfflineDict[element_id][1:1]:
                print(f"server: {self.PipeServerDict[element_id][1:]} diffs from offline: {self.PipeOfflineDict[element_id][1:]}")
                self.updateExistingPipe(element_id, lastUpdated)
                
    def getPipeServerDict(self, lastUpdated):
        self.PipeResponse = self.loadElements()
        data = self.PipeResponse.json()["data"]
        for element in data:
            attributes  = [element[self.Attributes[i]] for i in range(len(self.Attributes))]
            points = [self.getPipeTransformedCrs(QgsPointXY(vertex['lng'], vertex['lat'])) for vertex in element["vertices"]]
            attributes.append(points)
            self.PipeServerDict[element["serverKeyId"]] = attributes
            
    def getPipeOfflineDict(self, lastUpdated):
        for feature in self.Layer.getFeatures():
            attributes = [feature[self.FieldDefinitions[i]] for i in range(len(self.FieldDefinitions))]
            
            if not attributes[2]:
                attributes[2] = ""
            
            geom = feature.geometry()

            # Check if the geometry is a single or multipart line
            if geom.isMultipart():
                # It's a MultiPolyline, so we use asMultiPolyline()
                line_parts = geom.asMultiPolyline()
                # Flatten the list of points from all parts
                points = [point for part in line_parts for point in part]
            else:
                # It's a single part line (Polyline), so we use asPolyline()
                points = geom.asPolyline()

            attributes.append([point for point in points])
            
            attributes[-1] = attributes[-1][0]
            
            self.PipeOfflineDict[feature["ID"]] = attributes

    def addPipesToOnline(self):
        features_to_add= [feature for feature in self.Layer.getFeatures() if (len(str(feature['ID'])) == 10)
                          and (feature['ID'] in self.PipeOfflineDict)]
        
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
        feature.setAttribute("ID", id)
        
        feature.setGeometry(QgsGeometry.fromPolylineXY(self.PipeServerDict[id][-1]))
        
        self.Layer.startEditing()
        
        for i, field in enumerate(self.FieldDefinitions):
            feature[field] = self.PipeServerDict[id][i]
        
        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())
        
        self.Layer.addFeature(feature)
        self.Layer.commitChanges()
    
    def handleDeletedElementsFromServer(self):
        elements_deleted_from_server = [id for id in self.OfflineDict if (len(str(id)) != 10) and id not in self.PipeServerDict]
        
        print(" elements_deleted_from_server: ", elements_deleted_from_server)
        if elements_deleted_from_server:
            ids_to_delete = [feature.id() for feature in self.Layer.getFeatures() if feature["ID"] in elements_deleted_from_server]
            
            self.Layer.startEditing()
            
            self.Layer.deleteFeatures(ids_to_delete)

            self.Layer.commitChanges()
            
    def updateExistingPipe(self, id, lastUpdated):
        #print(f"Updating existing element in {self.LayerName}: {id}")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        
        features = [feature for feature in self.Layer.getFeatures() if feature['ID'] == id]

        self.Layer.startEditing()
        
        for feature in features:
            if (id in self.PipeServerDict) and (id in self.PipeOfflineDict):
                serverDictLastUpdate = self.adjustedDatetime(self.PipeServerDict[id][0])
                offlineDictLastUpdate = self.adjustedDatetime(feature['lastUpdate'])
                print("time at server -> ", self.PipeServerDict[id][0], " time at offline -> ", feature['lastUpdate'])
                if serverDictLastUpdate > offlineDictLastUpdate and serverDictLastUpdate > lastUpdated:
                    print("option 1->updating from server to local in pipes: ", self.Layer, " ", feature)
                    self.Layer.startEditing()

                    attrs = {}
                    
                    for i in range(len(self.FieldDefinitions)):
                        field_index = self.Layer.fields().indexOf(self.FieldDefinitions[i])
                        attrs[field_index] = self.PipeServerDict[id][i]
                        
                    last_update_index = self.Layer.fields().indexOf('lastUpdate')
                    attrs[last_update_index] = str(WateringUtils.getDateTimeNow())

                    self.Layer.dataProvider().changeAttributeValues({feature.id(): attrs})
                    #update geometry
                    new_geometry = QgsGeometry.fromPolylineXY(self.PipeServerDict[id][-1])
                    
                    self.Layer.dataProvider().changeGeometryValues({feature.id(): new_geometry})
                    
                    self.Layer.commitChanges()
                    
                # If online feature has been modified and it´s already in the server
                elif len(str(feature['ID'])) == 36 and offlineDictLastUpdate > lastUpdated:
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
    
    def setDefaultValues(self, feature):
        name = "pipeName"
        description = "pipe form QGIS"
        diameter = 0.2
        roughnessAbsolute = 0.045
        roughnessCoefficient = 150
    
        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Diameter", diameter)
        feature.setAttribute("Rough.A", roughnessAbsolute) 
        feature.setAttribute("C(H.W.)", roughnessCoefficient)