import os
import requests

from .abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST


from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid

class pumpNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(pumpNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_PUMP", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_PUMP", self.processDELETEElementToLocal)
        self.lastAddedElements = {}
        self.lifoAddedElements = queue.LifoQueue()


    def processPOSTElementToLocal(self, paraminput):
        print("Entering processPOSTElementToLocal")
           
        jsonInput = paraminput[0]
        serverKeyId = jsonInput["serverKeyId"]
        print("last added elements: ", self.lastAddedElements)
        print("serverkeyid: ", serverKeyId)
        
        if not (serverKeyId in self.lastAddedElements):
            print("Just before creating valve from server push")
            print(paraminput[0])
            self.localRepository.addElementFromSignalR(paraminput[0])
            print("Water Valve Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Pump Node removed after push from server")


    def addElementToServer(self, feature):
        
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        #transforming coordinates for the CRS of the server
        transGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        transGeometry.transform(QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()))
        x = transGeometry.asPoint().x()
        y = transGeometry.asPoint().y()


        name = feature["Name"]
        description = feature["Descript"]
        z = feature["Z[m]"]
        model = feature["Model FK"]
        speed = feature["Rel. Speed"]


        serverKeyId = uuid.uuid4()
        elementJSON = {'serverKeyId': "{}".format(serverKeyId), 
                       'scenarioFK': "{}".format(self.ScenarioFK), 
                       'name': "{}".format(name), 
                       'description': "{}".format(description), 
                       'lng': "{}".format(x), 
                       'lat': "{}".format(y), 
                       'z': "{}".format(z),
                       'pumpModelFK': "{}".format(model),
                       'relativeSpeed': "{}".format(speed)
                        }
        

        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        serverResponse = self.serverRepository.postToServer(elementJSON)
        if serverResponse.status_code == 200:
            print("Water Pump Node was sent succesfully to the server")
            #writing the server key id to the element that has been created
            serverKeyId = serverResponse.json()["serverKeyId"]    
            feature.setAttribute("ID", serverKeyId)   
            if not serverKeyId in self.lastAddedElements:     
                self.lastAddedElements[serverKeyId] = 1
                self.lifoAddedElements.put(serverKeyId)
                while self.lifoAddedElements.full():
                    keyIdToEliminate = self.lifoAddedElements.get()
                    self.lastAddedElements.pop(keyIdToEliminate) 
        else: 
            print("Failed on sendig Pump Tank Node to the server")

    

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
    