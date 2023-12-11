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
        
        isNew = False
        if len(str(feature["ID"])) == 10:
            isNew = True
            serverKeyId = str(uuid.uuid4())
        else:
            serverKeyId = feature["ID"]
            
        name = feature["Name"] if feature["Name"] else WateringUtils.generateRandomElementName("P")
        last_mdf = WateringUtils.getDateTimeNow()
        description = feature["Descript"] if feature["Descript"] else ""
        diameterInt = feature["Diameter"] if feature["Diameter"] else 0.2
        roughnessAbsolute = feature["Rough.A"] if feature["Rough.A"] else 0.045
        roughnessCoefficient = feature["C(H.W.)"] if feature["C(H.W.)"] else 150
        initialStatus = 1
        currentStatus = 1
        nodeUpFK = WateringUtils.getProjectMetadata("nodeUpFK")
        nodeUpName = "string"
        nodeDownFK = WateringUtils.getProjectMetadata("nodeDownFK")
        nodeDownName = "string"
        
        vertices = self.getVertices(feature, nodeDownFK, nodeUpFK)
        length = self.getPipeLength(vertices)
            
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
        
        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        if (isNew): 
            print("pipe is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else: 
            print("pipe is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)
        
        if serverResponse.status_code == 200:
            print("Water Pipe Node was sent succesfully to the server")
            #writing the server key id to the element that has been created
            
            if isNew:
                layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]
                
                id_element = feature["ID"]
                
                layer.startEditing()
                
                c_feature = None
                for feat in layer.getFeatures():
                    if feat["ID"] == id_element:
                        c_feature = feat
                        c_feature.setAttribute(c_feature.fieldNameIndex("ID"), str(serverKeyId))
                        c_feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())
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
        else: 
            print("Failed on sendig Pipe Node to the server")

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {'scenarioFK': "{}".format(self.ScenarioFK), 
                       'serverKeyId': "{}".format(serverKeyId)}
        
        serverResponse = self.serverRepository.deleteFromServer(elementJSON)
    
    def getVertices(self, feature, nodeDownFK, nodeUpFK):
        vertices = []

        transGeometry = feature.geometry()
        transform = QgsCoordinateTransform(self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance())
        transGeometry.transform(transform)

        if transGeometry.isMultipart():
            line_parts = transGeometry.asMultiPolyline()
            for part in line_parts:
                for index, point in enumerate(part):
                    self._processPoint(point, index, nodeDownFK, nodeUpFK, vertices)
                    break
                break
        else:
            for index, point in enumerate(transGeometry.asPolyline()):
                self._processPoint(point, index, nodeDownFK, nodeUpFK, vertices)

        return vertices[::-1]

    def _processPoint(self, point, index, nodeDownFK, nodeUpFK, vertices):
        current_vertex_fk = nodeUpFK if index % 2 == 0 else nodeDownFK
        vertex = {
            "vertexFK": "{}".format(current_vertex_fk),
            "lng": point.x(),
            "lat": point.y()
        }
        vertices.append(vertex)

    def getPipeLength(self, vertices):
        if len(vertices) < 2:
            return 0

        distance_area = QgsDistanceArea()
        distance_area.setEllipsoid('WGS84')
        distance_area.setSourceCrs(self.serverRepository.currentCRS, QgsProject.instance().transformContext())

        points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in vertices]

        length = sum(distance_area.measureLine(points[i], points[i+1]) for i in range(len(points) - 1))

        return length