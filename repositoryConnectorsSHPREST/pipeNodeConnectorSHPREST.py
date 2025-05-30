import os
import requests

from .abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST
from ..watering_utils import WateringUtils

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)
from qgis.core import (
    QgsVectorFileWriter,
    QgsPointXY,
    QgsFeature,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
)
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

    def getElementJson(self, feature):
        isNew = False
        if len(str(feature["ID"])) == 10:
            isNew = True
            serverKeyId = str(uuid.uuid4())
        else:
            serverKeyId = feature["ID"]

        name = feature["Name"] if feature["Name"] else WateringUtils.generateRandomElementName("P")
        description = feature["Descript"] if feature["Descript"] else ""
        diameterInt = feature["Diameter"] if feature["Diameter"] else 0.2
        roughnessAbsolute = feature["Rough.A"] if feature["Rough.A"] else 0.045
        roughnessCoefficient = feature["C(H.W.)"] if feature["C(H.W.)"] else 150
        initialStatus = 1
        currentStatus = 1

        nodeDownFK, nodeUpFK = self.getPipeNodes(feature)
        vertices = self.getVertices(feature, nodeDownFK, nodeUpFK)

        elementJSON = {
            "serverKeyId": "{}".format(serverKeyId),
            "scenarioFK": "{}".format(self.ScenarioFK),
            "nodeUpFK": "{}".format(nodeUpFK),
            "nodeDownFK": "{}".format(nodeDownFK),
            "name": "{}".format(name),
            "description": "{}".format(description),
            "vertices": vertices,
            "diameterInt": "{}".format(diameterInt),
            "roughnessAbsolute": "{}".format(roughnessAbsolute),
            "roughnessCoefficient": "{}".format(roughnessCoefficient),
            "initialStatus": "{}".format(initialStatus),
            "currentStatus": "{}".format(currentStatus),
        }

        return elementJSON, isNew, serverKeyId, feature["ID"]

    def addElementToServer(self, feature):
        elementJSON, isNew, serverKeyId, _ = self.getElementJson(feature)

        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        print("Pipes element JSON: ", elementJSON)
        if isNew:
            print("pipe is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else:
            print("pipe is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)

        if serverResponse and serverResponse.status_code == 200:
            print("Water Pipe Node was sent succesfully to the server")

            if isNew:
                layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]

                id_element = feature["ID"]

                layer.startEditing()

                c_feature = None
                for feat in layer.getFeatures():
                    if feat["ID"] == id_element:
                        c_feature = feat
                        c_feature.setAttribute(c_feature.fieldNameIndex("ID"), str(serverKeyId))
                        c_feature.setAttribute(
                            "lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
                        )
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
            print("Failed on sendig Pipe Node to the server")
            return False

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {"scenarioFK": "{}".format(self.ScenarioFK), "serverKeyId": "{}".format(serverKeyId)}

        return self.serverRepository.deleteFromServer(elementJSON) == 200

    def getVertices(self, feature, nodeDownFK, nodeUpFK):
        vertices = []

        transGeometry = feature.geometry()
        transform = QgsCoordinateTransform(
            self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()
        )
        transGeometry.transform(transform)

        if transGeometry.isMultipart():
            line_parts = transGeometry.asMultiPolyline()

            for part in line_parts:
                order = 0
                for point in part:
                    self.processMultiPoint(point, vertices, order)
                    order = order + 1
        else:
            order = 0
            for point in transGeometry.asPolyline():
                self.processPoint(point, vertices, order)
                order = order + 1

        return vertices

    def processPoint(self, point, vertices, order):
        vertexFK = str(uuid.uuid4())
        vertex = {"vertexFK": vertexFK, "lng": point.x(), "lat": point.y(), "order": order}
        vertices.append(vertex)

    def processMultiPoint(self, point, vertices, order):
        vertexFK = str(uuid.uuid4())
        vertex = {"vertexFK": vertexFK, "lng": point.x(), "lat": point.y(), "order": order}
        vertices.append(vertex)

    def getPipeLength(self, vertices):
        if len(vertices) < 2:
            return 0

        distance_area = QgsDistanceArea()
        distance_area.setEllipsoid("WGS84")
        distance_area.setSourceCrs(self.serverRepository.currentCRS, QgsProject.instance().transformContext())

        points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in vertices]

        length = sum(distance_area.measureLine(points[i], points[i + 1]) for i in range(len(points) - 1))

        return length

    def getPipeNodes(self, feature):
        demand_nodes_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        tanks_layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
        reservoirs_layer = QgsProject.instance().mapLayersByName("watering_reservoirs")[0]

        polyline_geom = feature.geometry()

        if polyline_geom.isMultipart():
            lines = polyline_geom.asMultiPolyline()
            start_point = lines[0][0]
            end_point = lines[-1][-1]
        else:
            line = polyline_geom.asPolyline()
            start_point = line[0]
            end_point = line[-1]

        up_node = None
        down_node = None

        for layer in [demand_nodes_layer, tanks_layer, reservoirs_layer]:
            up_node = self.find_matching_node(start_point, layer)
            if up_node:
                break

        for layer in [demand_nodes_layer, tanks_layer, reservoirs_layer]:
            down_node = self.find_matching_node(end_point, layer)
            if down_node:
                break

        return down_node, up_node

    def find_matching_node(self, point, node_layer):
        tolerance = 0.0001
        for node in node_layer.getFeatures():
            node_point = node.geometry().asPoint()
            if point.distance(node_point) < tolerance:
                return node["ID"]
        return None

    def update_layer_features(self, elementsJSONlist):
        layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]

        if not layer:
            print("Layer not found")
            return

        layer.startEditing()

        for element in elementsJSONlist:
            serverKeyId = element[0]["serverKeyId"]
            current_feature_id = element[1]

            for feature in layer.getFeatures():
                if feature["ID"] == current_feature_id:
                    layer.changeAttributeValue(feature.id(), feature.fieldNameIndex("ID"), serverKeyId)
                    break

        layer.commitChanges()
        print("Layer features updated successfully.")
