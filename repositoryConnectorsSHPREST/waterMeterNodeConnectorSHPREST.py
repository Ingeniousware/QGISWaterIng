import os
import requests

from .abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST
from ..watering_utils import WateringUtils

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid
from datetime import datetime, timezone

class waterMeterNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(waterMeterNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_WATERMETER", self.processPOSTElementToLocal)
        connectionHub.on("POST_WATERMETER", self.processDELETEElementToLocal)
        self.lastAddedElements = {}
        self.lifoAddedElements = queue.LifoQueue()


    def processPOSTElementToLocal(self, paraminput):
        print("Entering processPOSTElementToLocal")        
        jsonInput = paraminput[0]
        serverKeyId = jsonInput["serverKeyId"]
        if not (serverKeyId in self.lastAddedElements):
            print("Just before creating valve from server push")
            self.localRepository.addElementFromSignalR(paraminput[0])
            print("Water Valve Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Valve Node removed after push from server")


    def getElementJson(self, feature):
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
            
        name = feature["Name"] if feature["Name"] else WateringUtils.generateRandomElementName("W")
        description = feature["Descript"] if feature["Descript"] else "Water Meter from QGIS Plugin"
        meterState = feature["Meterstate"] if feature["Meterstate"] else 2 #Installed
        functType = feature["FunctType"] if feature["FunctType"] else 1 #ClientMetering
        connectedToNodeFK = feature["NodeID"] if feature["NodeID"] else ""
        formatted_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            
        elementJSON = {'serverKeyId': "{}".format(serverKeyId), 
                        'fkScenario': "{}".format(self.ScenarioFK), 
                        'name': "{}".format(name), 
                        'description': "{}".format(description),
                        #'installedDate': "{}".format(formatted_date), 
                        'lng': "{}".format(x), 
                        'lat': "{}".format(y),
                        'meterstate': "{}".format(meterState), 
                        'functionalType': "{}".format(functType),
                        'connectedToNodeFK': "{}".format(connectedToNodeFK)
                        }
        
        return elementJSON, isNew, serverKeyId
    
    def addElementToServer(self, feature):
        elementJSON, isNew, serverKeyId, _ = self.getElementJson(feature)
    
        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        if (isNew): 
            print("Water Meter is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else: 
            print("Water Meter is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)

        print("Server response: ", serverResponse.text)
        print("Server response status: ", serverResponse.status_code)
        
        if serverResponse.status_code == 200:
            print("Water Valve Node was sent succesfully to the server")
            #writing the server key id to the element that has been created
            
            if isNew:
                layer = QgsProject.instance().mapLayersByName("watering_waterMeter")[0]
                
                id_element = feature["ID"]
                
                layer.startEditing()
                
                c_feature = None
                for feat in layer.getFeatures():
                    if feat["ID"] == id_element:
                        c_feature = feat
                        c_feature.setAttribute(c_feature.fieldNameIndex("ID"), str(serverKeyId))
                        c_feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
                        layer.updateFeature(c_feature)
                        print("Feature Found")
                        break
                    
                layer.commitChanges()
                
            if not serverKeyId in self.lastAddedElements:     
                self.lastAddedElements[serverKeyId] = 1
                self.lifoAddedElements.put(serverKeyId)
                while self.lifoAddedElements.full():
                    keyIdToEliminate = self.lifoAddedElements.get()
                    self.lastAddedElements.pop(keyIdToEliminate) 
            return True
        
        else: 
            print("Failed on sendig Water Meter to the server")
            return False

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        return (self.serverRepository.deleteFromServer(elementJSON) == 200)
    