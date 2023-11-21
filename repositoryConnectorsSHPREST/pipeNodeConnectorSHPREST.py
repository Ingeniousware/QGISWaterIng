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
        node_down_fk = WateringUtils.getProjectMetadata("nodeDownFK")
        node_up_fk = WateringUtils.getProjectMetadata("nodeUpFK")
        
        print("node_down_fk: ", node_down_fk)
        print("node_up_fk: ", node_up_fk)
        
        name = feature["Name"] if feature["Name"] else WateringUtils.generateRandomElementName("P")
        last_mdf = WateringUtils.getDateTimeNow().value().toString("yyyy/MM/dd HH:mm:ss.zzz")
        description = feature["Descript"] if feature["Descript"] else ""
        diameterInt = feature["Diameter"] if feature["Diameter"] else 0.2
        roughnessAbsolute = feature["Rough.A"] if feature["Rough.A"] else 0.045
        #roughnessCoefficient = feature["C(H.W.)"]
        roughnessCoefficient = feature["C(H.W.)"] if feature["C(H.W.)"] else 150
        initialStatus = 1
        currentStatus = 1
        nodeUpFK = node_up_fk
        #nodeUpName = feature["Up-Node"]
        nodeUpName = "string"
        nodeDownFK = node_down_fk
        #nodeDownName = feature["Down-Node"]
        nodeDownName = "string"
        
        vertices = self.getVertices(feature, nodeDownFK, nodeUpFK)
        #length = feature["Length"]
        length = self.getPipeLength(vertices)
        print("length: ", length)
        print("VERTICES: ", vertices)
        #vertexFK = uuid.uuid4()
        serverKeyId = uuid.uuid4()
            
        elementJSON = {
            "serverKeyId": "{}".format(serverKeyId),
            "lastModified": "{}".format(last_mdf),
            "scenarioFK": "{}".format(self.ScenarioFK),
            "nodeUpFK": "{}".format(nodeUpFK),
            "nodeUpName": "{}".format(nodeUpName),
            "nodeDownFK": "{}".format(nodeDownFK),
            "nodeDownName": "{}".format(nodeDownName),
            "name": "{}".format(name),
            "description": "{}".format(description),
            "vertices": vertices,
            "diameterInt": "{}".format(diameterInt),
            "length": "{}".format(length),
            "roughnessAbsolute": "{}".format(roughnessAbsolute),
            "roughnessCoefficient": "{}".format(roughnessCoefficient),
            "initialStatus": "{}".format(initialStatus),
            "currentStatus": "{}".format(currentStatus)
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
        
        print("EEMENTS JSON: ", elementJSON)
        
        
        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        serverResponse = self.serverRepository.postToServer(elementJSON)
        
        print("RESPONSE TEXT: ", serverResponse.text, " status: ", serverResponse)
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
    
    def getVertices(self, feature, nodeDownFK, nodeUpFK):
        vertices = []
        
        transGeometry = feature.geometry()
        transform = QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance())
        transGeometry.transform(transform)
        
        for index, point in enumerate(transGeometry.asPolyline()):
            current_vertex_fk = nodeUpFK if index % 2 == 0 else nodeDownFK
            
            vertex = {
                    "vertexFK": "{}".format(current_vertex_fk),  # Substitua por uma chave estrangeira, se necessário
                    "lng": point.x(),
                    "lat": point.y()
            }   
            vertices.append(vertex)
            
        return vertices[::-1]

    def getPipeLength(self, vertices):
        if len(vertices) < 2:
            return 0

        distance_area = QgsDistanceArea()
        distance_area.setEllipsoid('WGS84')
        distance_area.setSourceCrs(self.serverRepository.currentCRS, QgsProject.instance().transformContext())

        points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in vertices]

        length = sum(distance_area.measureLine(points[i], points[i+1]) for i in range(len(points) - 1))

        return length