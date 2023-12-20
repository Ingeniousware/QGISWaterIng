import os
import requests

from ..repositoryConnectorsSHPREST.abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST
from ..watering_utils import WateringUtils

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid

class reservoirNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(reservoirNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_RESERVOIR", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_RESERVOIR", self.processDELETEElementToLocal)
        self.lastAddedElements = {}
        self.lifoAddedElements = queue.LifoQueue()


    def processPOSTElementToLocal(self, paraminput):
        print("Entering processPOSTElementToLocal")        
        #print(paraminput[0])
        jsonInput = paraminput[0]
        serverKeyId = jsonInput["serverKeyId"]
        print(serverKeyId)
        if not (serverKeyId in self.lastAddedElements):
            self.localRepository.addElementFromSignalR(paraminput[0])
            print("Water Reservoir Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Reservoir Node removed after push from server")


    def addElementToServer(self, feature):
        
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        #transforming coordinates for the CRS of the server
        transGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        transGeometry.transform(QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()))
        x = transGeometry.asPoint().x()
        y = transGeometry.asPoint().y()
        
        isNew = False
        if len(feature["ID"]) == 10:
            isNew = True
            serverKeyId = str(uuid.uuid4())
        else:
            serverKeyId = feature["ID"]
            
        name = feature["Name"]
        description = feature["Descript"]
        z = feature["Z[m]"]
        head = feature["Head[m]"]
            
        elementJSON = {'serverKeyId': "{}".format(serverKeyId), 
                       'scenarioFK': "{}".format(self.ScenarioFK), 
                       'name': "{}".format(name), 
                       'description': "{}".format(description), 
                       'lng': "{}".format(x), 
                       'lat': "{}".format(y), 
                       'z': "{}".format(z), 
                       'head': "{}".format(head)}
        

        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        if (isNew): 
            print("Reservoir is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else: 
            print("Reservoir is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)
        
        if serverResponse.status_code == 200:
            print("Water Reservoir Node was sent succesfully to the server")
            
            if isNew:
                layer = QgsProject.instance().mapLayersByName("watering_reservoirs")[0]
                
                id_element = feature["ID"]
                
                layer.startEditing()

                attr_updates = {}

                for feat in layer.getFeatures():
                    if feat["ID"] == id_element:
                        feat_id = feat.id()

                        id_idx = layer.fields().indexOf('ID')
                        last_update_idx = layer.fields().indexOf('lastUpdate')

                        new_id_value = str(serverKeyId)
                        new_last_update_value = str(WateringUtils.getDateTimeNow())

                        attr_updates[feat_id] = {id_idx: new_id_value, last_update_idx: new_last_update_value}

                        print("Feature Found")
                        break

                if attr_updates:
                    layer.dataProvider().changeAttributeValues(attr_updates)

                    layer.commitChanges()
                else:
                    print("No feature found") 
               
            if not serverKeyId in self.lastAddedElements:     
                self.lastAddedElements[serverKeyId] = 1
                self.lifoAddedElements.put(serverKeyId)
                while self.lifoAddedElements.full():
                    keyIdToEliminate = self.lifoAddedElements.get()
                    self.lastAddedElements.pop(keyIdToEliminate) 
        else: 
            print("Failed on sendig Water Reservoir Node to the server")

    

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
    