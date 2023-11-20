import os
import requests

from .abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST
from ..watering_utils import WateringUtils

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsDistanceArea
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid

class pipeNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(pipeNodeConnectorSHPREST, self).__init__(scenarioFK)    
        self.serverRepository = None  
        self.localRepository = None
        connectionHub.on("POST_PIPE", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_PIPE", self.processDELETEElementToLocal)
        self.lastAddedElements = {}
        self.lifoAddedElements = queue.LifoQueue()
        print("SCENARIO FK pipe", scenarioFK)


    def processPOSTElementToLocal(self, paraminput):
        print("Entering processPOSTElementToLocal")
           
        jsonInput = paraminput[0]
        serverKeyId = jsonInput["serverKeyId"]
        if not (serverKeyId in self.lastAddedElements):
            print("Just before creating pipe from server push")
            self.localRepository.addElementFromSignalR(paraminput[0])
            print("Pipe Node inserted after push from server")
            print("dict-> ", self.lastAddedElements)
        else:
            print("Key found -> ", serverKeyId)


    def processDELETEElementToLocal(self, paraminput):
        self.localRepository.deleteElement(paraminput[0])
        print("Water Pipe Node removed after push from server")


    def addElementToServer(self, feature):
        print("ADDING PIPESS")

        vertices = self.getVertices(feature)
        print("VERTICES: ", vertices)
        
        name = feature["Name"]
        last_mdf = WateringUtils.getDateTimeNow().value().toString("yyyy/MM/dd HH:mm:ss.zzz")
        description = feature["Descript"]
        #diameterInt = feature["Diameter"]
        diameterInt = 0.2
        #length = feature["Length"]
        length = self.getPipeLength(vertices)
        print("length: ", length)
        #roughnessAbsolute = feature["Rough.A"]
        roughnessAbsolute = 0.045
        #roughnessCoefficient = feature["C(H.W.)"]
        roughnessCoefficient = 150
        #initialStatus = feature["Name"]
        #currentStatus = feature["Name"]
        nodeUpFK = uuid.uuid4()
        nodeUpName = feature["Up-Node"]
        nodeDownFK = uuid.uuid4()
        nodeDownName = feature["Down-Node"]
        
        vertices = self.getVertices(feature)
        vertexFK = uuid.uuid4()
        serverKeyId = uuid.uuid4()
            
        elementJSON = {
            "serverKeyId": "{}".format(serverKeyId),
            "lastModified": "{}".format(last_mdf),
            "scenarioFK": "{}".format(self.ScenarioFK),
            "name": "{}".format(name),
            "description": "{}".format(description),
            "vertices": vertices,
            "diameterInt": "{}".format(diameterInt),
            "length": "{}".format(length),
            "roughnessAbsolute": "{}".format(roughnessAbsolute),
            "roughnessCoefficient": "{}".format(roughnessCoefficient)
        }
        
        """elementJSON = {"serverKeyId": "00000000-0000-0000-0000-000000000000",
                        "scenarioFK": "a85ef45c-014a-43fe-9d7d-bac7abf417e3",
                        "nodeUpFK": "5d89c584-a10a-4869-8b7d-7994ff5c231e",
                        "nodeUpName": "string",
                        "nodeDownFK": "86108cd1-ad50-47eb-8078-d81570ebe4f3",
                        "nodeDownName": "string",
                        "name": "my new pipe",
                        "description": "nothing",
                        "vertices": [
                                    {
                                    "vertexFK": "5d89c584-a10a-4869-8b7d-7994ff5c231e",
                                    "lng": -70.9772316455841100,
                                    "lat": -17.8174670657465270
                                    },
                                    {
                                    "vertexFK": "86108cd1-ad50-47eb-8078-d81570ebe4f3",
                                    "lng": -71.0184303760528600,
                                    "lat": -17.8370773271525700
                                    }
                        ],
                        "diameterInt": "0.5",
                        "roughnessAbsolute": "0",
                        "roughnessCoefficient": "0",
                        "initialStatus": 1,
                        "currentStatus": 1}"""
        
        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        serverResponse = self.serverRepository.postToServer(elementJSON)
        
        print("RESPONSE TEXT: ", serverResponse.text)
        if serverResponse.status_code == 200:
            print("Water Pipe Node was sent succesfully to the server")
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
            print("Failed on sendig Pipe Node to the server")

        print("END ADDING PIPESS")
    

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
    
    def getVertices(self, feature):
        vertices = []
        
        transGeometry = feature.geometry()
        transform = QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance())
        transGeometry.transform(transform)
        
        for point in transGeometry.asPolyline():
            vertex = {
                    "vertexFK": "anything",  # Substitua por uma chave estrangeira, se necessário
                    "lng": point.x(),
                    "lat": point.y()
            }
            vertices.append(vertex)
            
        return vertices

    def getPipeLength(self, vertices):
        if len(vertices) < 2:
            return 0

        distance_area = QgsDistanceArea()
        distance_area.setEllipsoid('WGS84')
        distance_area.setSourceCrs(self.serverRepository.currentCRS, QgsProject.instance().transformContext())

        points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in vertices]

        length = sum(distance_area.measureLine(points[i], points[i+1]) for i in range(len(points) - 1))

        return length