import os
import requests

from ..repositoryConnectorsSHPREST.abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST


from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid

class sensorNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(sensorNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_SENSOR", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_SENSOR", self.processDELETEElementToLocal)
        self.lastAddedElements = {}
        self.lifoAddedElements = queue.LifoQueue()
        self.Layer = QgsProject.instance().mapLayersByName("watering_sensors")[0]


    def processPOSTElementToLocal(self, paraminput):
        print("Entering processPOSTElementToLocal")        
        #print(paraminput[0])
        jsonInput = paraminput[0]
        serverKeyId = jsonInput["serverKeyId"]
        #print(serverKeyId)
        if not (serverKeyId in self.lastAddedElements):
            self.localRepository.addElementFromSignalR(paraminput[0])
            print("Water Sensor Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Sensor Node removed after push from server")


    def addElementToServer(self, feature):
        
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        #transforming coordinates for the CRS of the server
        transGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        transGeometry.transform(QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()))
        x = transGeometry.asPoint().x()
        y = transGeometry.asPoint().y()

        isNew = False
        if feature["ID"] == None: 
            isNew = True
            serverKeyId = uuid.uuid4() 
        else:
            serverKeyId = feature["ID"]
            
        name = feature["Name"]
        description = feature["Descript"]
        z = feature["Z[m]"]

        elementJSON = {'serverKeyId': "{}".format(serverKeyId), 
                       'scenarioFK': "{}".format(self.ScenarioFK), 
                       'name': "{}".format(name), 
                       'description': "{}".format(description), 
                       'lng': "{}".format(x), 
                       'lat': "{}".format(y), 
                       'z': "{}".format(z)
                       }
        

        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)


        #if (isNew): serverResponse = self.serverRepository.postToServer(elementJSON)
        #else: serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)

        if (isNew): 
            print("sensor is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else: 
            print("sensor is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)
        
        print("SERVER RESPONSE SENSOR: ", serverResponse)
        
        if serverResponse.status_code == 200:
            print("Water Sensor Node was sent succesfully to the server")
            
            self.Layer.startEditing()
            feature.setAttribute(self.Layer.fields().indexFromName('ID'), serverKeyId)
            #feature.setAttribute(self.Layer.fields().indexFromName('lastUpdate'), now)
            self.Layer.updateFeature(feature)
            self.Layer.commitChanges()
                
            #feature.setAttribute("ID", serverKeyId)  
             
            if not serverKeyId in self.lastAddedElements:     
                self.lastAddedElements[serverKeyId] = 1
                self.lifoAddedElements.put(serverKeyId)
                while self.lifoAddedElements.full():
                    keyIdToEliminate = self.lifoAddedElements.get()
                    self.lastAddedElements.pop(keyIdToEliminate) 
        else: 
            print("Failed on sendig Water Sensor Node to the server: ", serverResponse.status_code)

    

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
    