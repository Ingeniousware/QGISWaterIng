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
)
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
import queue
import uuid


class valveNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self, scenarioFK, connectionHub):
        """Constructor."""
        super(valveNodeConnectorSHPREST, self).__init__(scenarioFK)
        self.serverRepository = None
        self.localRepository = None
        connectionHub.on("POST_VALVE", self.processPOSTElementToLocal)
        connectionHub.on("DELETE_VALVE", self.processDELETEElementToLocal)
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
        # transforming coordinates for the CRS of the server
        transGeometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        transGeometry.transform(
            QgsCoordinateTransform(
                self.localRepository.currentCRS, self.serverRepository.currentCRS, QgsProject.instance()
            )
        )
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
        diameter = feature["Diameter"]
        typeV = int(feature["typeValvul"])
        minorLossCoef = feature["minorLossC"]
        initial = 1

        elementJSON = {
            "serverKeyId": "{}".format(serverKeyId),
            "scenarioFK": "{}".format(self.ScenarioFK),
            "name": "{}".format(name),
            "description": "{}".format(description),
            "lng": "{}".format(x),
            "lat": "{}".format(y),
            "z": "{}".format(z),
            "diameter": "{}".format(diameter),
            "typeValvule": "{}".format(typeV),
            "minorLossCoef": "{}".format(minorLossCoef),
            "initialStatus": "{}".format(initial),
        }

        return elementJSON, isNew, serverKeyId, feature["ID"]

    def addElementToServer(self, feature):
        elementJSON, isNew, serverKeyId, _ = self.getElementJson(feature)

        self.lastAddedElements[str(serverKeyId)] = 1
        self.lifoAddedElements.put(str(serverKeyId))
        while self.lifoAddedElements.full():
            keyIdToEliminate = self.lifoAddedElements.get()
            self.lastAddedElements.pop(keyIdToEliminate)

        if isNew:
            print("Valve is new, posting")
            serverResponse = self.serverRepository.postToServer(elementJSON)
        else:
            print("Valve is not new, putting")
            serverResponse = self.serverRepository.putToServer(elementJSON, serverKeyId)

        print("VALVE RESPONSE: ", serverResponse.text)

        if serverResponse and serverResponse.status_code == 200:
            print("Water Valve Node was sent succesfully to the server")
            # writing the server key id to the element that has been created

            if isNew:
                layer = QgsProject.instance().mapLayersByName("watering_valves")[0]

                id_element = feature["ID"]

                layer.startEditing()

                attr_updates = {}

                for feat in layer.getFeatures():
                    if feat["ID"] == id_element:
                        feat_id = feat.id()

                        id_idx = layer.fields().indexOf("ID")
                        last_update_idx = layer.fields().indexOf("lastUpdate")

                        new_id_value = str(serverKeyId)
                        new_last_update_value = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")

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
            return True

        else:
            print("Failed on sendig Valve Tank Node to the server")
            return False

    def removeElementFromServer(self, serverKeyId):
        elementJSON = {"scenarioFK": "{}".format(self.ScenarioFK), "serverKeyId": "{}".format(serverKeyId)}

        return self.serverRepository.deleteFromServer(elementJSON) == 200

    def update_layer_features(self, elementsJSONlist):
        layer = QgsProject.instance().mapLayersByName("watering_valves")[0]

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
