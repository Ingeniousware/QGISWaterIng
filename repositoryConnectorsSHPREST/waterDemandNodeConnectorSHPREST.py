import os
import requests

from ..repositoryConnectorsSHPREST.abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST


from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid

class waterDemandNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(waterDemandNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_NODE", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_NODE", self.processDELETEElementToLocal)
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
            print("Water Demand Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Demand Node removed after push from server")


    def addElementToServer(self, feature):
        
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        #transforming coordinates for the CRS of the server
        transGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        transGeometry.transform(QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()))
        x = transGeometry.asPoint().x()
        y = transGeometry.asPoint().y()


        id = feature["ID"]
        name = feature["Name"]
        description = feature["Descript"]
        z = feature["Z[m]"]
        baseDemand = feature["B. Demand"]

        isNew = False
        if (id == None): 
            serverKeyId = uuid.uuid4()
            isNew = True
        else: serverKeyId = uuid.UUID(id)
        
        elementJSON = {'serverKeyId': "{}".format(serverKeyId), 
                       'scenarioFK': "{}".format(self.ScenarioFK), 
                       'name': "{}".format(name), 
                       'description': "{}".format(description), 
                       'lng': "{}".format(x), 
                       'lat': "{}".format(y), 
                       'z': "{}".format(z), 
                       'baseDemand': "{}".format(baseDemand)}
        

        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)


        if (isNew): serverResponse = self.serverRepository.postToServer(elementJSON)
        else: serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)

        
        if serverResponse.status_code == 200:
            print("Water Demand Node was sent succesfully to the server")
            #writing the server key id to the element that has been created
            serverKeyId = serverResponse.json()["serverKeyId"]
            print(serverKeyId)       
            feature.setAttribute("ID", serverKeyId)   
            if not serverKeyId in self.lastAddedElements:     
                self.lastAddedElements[serverKeyId] = 1
                self.lifoAddedElements.put(serverKeyId)
                while self.lifoAddedElements.full():
                    keyIdToEliminate = self.lifoAddedElements.get()
                    self.lastAddedElements.pop(keyIdToEliminate) 
        else: 
            print("Failed on sendig Water Demand Node to the server: ", serverResponse.status_code)

    

    def removeElementFromServer(self, serverKeyId):
        print(f"removing {serverKeyId} from server")
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
        print(serverResponse)