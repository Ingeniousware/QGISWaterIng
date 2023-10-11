from qgis.core import QgsProject, QgsCoordinateReferenceSystem
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY


import os
import requests
from ..watering_utils import WateringUtils

class UpdateAbstractTool():

    def __init__(self):
        self.Token = os.environ.get('TOKEN')
        self.ScenarioFK = WateringUtils.getScenarioId()
        self.Layer = None
        self.ServerDict = {}
        self.OfflineDict = {}
        self.Response = None
        
    def initializeRepository(self):
        print("Update tool has been activated")
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        self.loadElements()
    
    def loadElements(self):
        params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        self.Response = requests.get(url, params=params_element, 
                            headers={'Authorization': "Bearer {}".format(self.Token)}) 
         
        self.getServerDict()
        self.getOfflineDict()
        
        self.updateFromServerToOffline()
        self.updateFromOfflineToServer()
    
    def getServerDict(self):
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
    
    def updateFromServerToOffline(self):        
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
        
        features_to_delete = [feature.id() for feature in self.Layer.getFeatures() if feature['ID'] == id]
        self.Layer.startEditing()
        
        for feature in features_to_delete:
            self.Layer.deleteFeature(feature)
            
        self.Layer.commitChanges()
    
    def updateElement(self, id):
        
        print(f"Updating existing element in {self.LayerName}: {id}")
        
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
    