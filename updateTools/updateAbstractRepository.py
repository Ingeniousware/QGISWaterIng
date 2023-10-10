from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsPoint, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature,QgsFeatureRequest, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

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
        
    def initializeRepository(self):
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        self.loadElements()
    
    def loadElements(self):
        params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        response = requests.get(url, params=params_element, 
                            headers={'Authorization': "Bearer {}".format(self.Token)}) 
         
        self.getServerDict(response)
        self.getOfflineDict()
        self.updateLayer()

    def getServerDict(self, response):
        data = response.json()["data"]
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
    
    def updateLayer(self):        
        server_keys = set(self.ServerDict.keys())
        offline_keys = set(self.OfflineDict.keys())

        #Add Element
        for element_id in server_keys - offline_keys:
            self.addElement(element_id)

        #Delete Element
        for element_id in offline_keys - server_keys:
            #self.deleteElement(element_id)
            print("-")

        #Update Element
        for element_id in server_keys & offline_keys:
            if self.ServerDict[element_id] != self.OfflineDict[element_id]:
                #self.updateElement(element_id)
                print("-")
                
    def addElement(self, id):
        feature = QgsFeature(self.Layer.fields())
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.ServerDict[id][-1][0],
                                                               self.ServerDict[id][-1][1])))
        self.Layer.startEditing()

        for i, field in enumerate(self.Fields):
            feature[field] = self.ServerDict[id][i]

        self.Layer.addFeature(feature)
        self.Layer.commitChanges()
    
    def deleteElement(self, id):
        """expression = f"ID = {id}"
        feature_ids_to_delete = [f.id() for f in self.Layer.getFeatures(QgsFeatureRequest().setFilterExpression(expression))]

        self.Layer.startEditing()
        
        for fid in feature_ids_to_delete:
            self.Layer.deleteFeature(fid)"""
            
        self.Layer.commitChanges()
    
    def updateElement(self, id):
        ...
        
    def compare(self):
        print("comparision: ")
        print(self.ServerDict["1d1bafe4-98a8-42ce-b5e3-52739e349764"] ==
              self.OfflineDict["1d1bafe4-98a8-42ce-b5e3-52739e349764"])
        
    def getTransformedCrs(self, lng, lat):
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")   # Web Mercator
        
        geom = QgsGeometry.fromPointXY(QgsPointXY(lng, lat))
        geom.transform(QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance()))
        point = geom.asPoint()
        
        return (point.x(), point.y())
    