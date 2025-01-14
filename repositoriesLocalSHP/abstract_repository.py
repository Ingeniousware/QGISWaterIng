import requests
import os
import uuid
from ..watering_utils import WateringUtils
from .change import Change
from datetime import datetime
import pytz
import json

from qgis.core import (
    QgsField,
    QgsFields,
    QgsProject,
    QgsVectorLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsCoordinateReferenceSystem,
    QgsLayerTreeLayer,
)
from qgis.core import (
    QgsGeometry,
    QgsFeature,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsVectorFileWriter,
    QgsExpression,
    QgsFeatureRequest,
    QgsWkbTypes,
)
from PyQt5.QtCore import QFileInfo, QDateTime
from PyQt5.QtCore import QDateTime, Qt, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from qgis.utils import iface
from qgis.gui import QgsMapCanvas


class AbstractRepository:

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.destCrs = QgsCoordinateReferenceSystem(3857)
        self.currentCRS = QgsCoordinateReferenceSystem(3857)
        self.Layer = None
        self.buffer = ""
        self.FieldDefinitions = None
        self.toAddFeatures = None
        self.pr = None
        self.connectorToServer = None
        self.currentLayer = None
        self.numberLocalFieldsOnly = 1
        self.syncAddingChanges = []
        self.syncUpdatingChanges = []
        self.syncDeletingChanges = []

    def initializeRepository(self, offline):
        # loading element from the API
        serverResponse = self.loadElements(False, offline)
        # Adding elements to shapefile
        self.createElementLayerFromServerResponse(serverResponse)
        # Write shapefile
        self.writeShp()

    def initializeRepositoryStreamingData(self, offline):
        # loading element from the API
        serverResponse = self.loadElements(True, offline)
        # Adding elements to shapefile
        self.createElementLayerFromServerStreamingResponse(serverResponse)
        # Write shapefile
        self.writeShp()

    def setConnectorToServer(self, connector):
        self.connectorToServer = connector
        self.connectorToServer.localRepository = self

    def unsetConnectorToServer(self):
        self.connectorToServer = None

    def loadElements(self, stream, offline):
        params_element = {"ScenarioFK": "{}".format(self.ScenarioFK)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        headers = {"Authorization": "Bearer {}".format(os.environ.get("TOKEN"))}

        if not offline:
            response = requests.get(url, params=params_element, headers=headers, stream=stream, verify=False)
        else:
            print()
            response = self.createEmptyResponse()

        return response

    def createEmptyResponse(self):
        response = requests.Response()
        response._content = json.dumps({"data": {}}).encode('utf-8')
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        return response

    def loadChanges(self, lastUpdate):
        changes_url = WateringUtils.getServerUrl() + self.UrlGet + "/updates"
        params_changes = {
            "ScenarioFK": "{}".format(self.ScenarioFK),
            "lastPull": "{}".format(lastUpdate),
            "page": "1",
            "pageSize": "100",
        }

        response = requests.get(
            changes_url, params=params_changes, headers={"Authorization": "Bearer {}".format(os.environ.get("TOKEN"))}
        )
        return response

    def setElementFields(self, fields_definitions):
        fields = QgsFields()
        for name, data_type in fields_definitions:
            fields.append(QgsField(name, data_type))
        return fields

    def createElementLayerFromServerResponse(self, response):
        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("Point?crs=" + self.destCrs.authid(), "New Layer", "memory")
        self.pr = self.currentLayer.dataProvider()
        self.pr.addAttributes(fields)
        self.currentLayer.updateFields()

        response_json = response.json()
        if "data" in response_json:
            response_data = response_json["data"]

        if response_data:
            self.toAddFeatures = []
            for elementJSON in response_data:
                self.addElementFromJSON(elementJSON)

            self.pr.addFeatures(self.toAddFeatures)
            self.currentLayer.updateExtents()

    def createElementLayerFromServerStreamingResponse(self, response):
        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("Point?crs=" + self.destCrs.authid(), "New Layer", "memory")
        self.pr = self.currentLayer.dataProvider()
        self.pr.addAttributes(fields)
        self.currentLayer.updateFields()

        self.toAddFeatures = []

        response_json = response.json()
        if "data" in response_json:
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    chunk_data = chunk.decode("utf-8")

                    self.buffer += chunk_data

                    json_objects = self.buffer.split("\n")

                    self.buffer = json_objects.pop()

                    for obj in json_objects:
                        if obj.strip():
                            data = json.loads(obj)
                            print("data:", data)
                            print("data type 2: ", type(data))
                            for feature in data["data"]:
                                self.addElementFromJSON(feature)

        if self.buffer.strip():
            data = json.loads(self.buffer)
            print("data 1 :", data)
            for feature in data["data"]:
                self.addElementFromJSON(feature)

        self.pr.addFeatures(self.toAddFeatures)
        self.currentLayer.updateExtents()

    # When layer does not exists
    def addElementFromJSON(self, elementJSON):
        try:
            element = [elementJSON[field] for field in self.features]

            feature = QgsFeature(self.currentLayer.fields())
            geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)

            for i in range(len(self.field_definitions) - self.numberLocalFieldsOnly):
                feature.setAttribute(self.field_definitions[i][0], element[i + 2])

            feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
            self.toAddFeatures.append(feature)

            WateringUtils.write_sync_operation(self.currentLayer, feature, WateringUtils.OperationType.ADD)
        except ValueError as e:
            print("Error->", e)


    # When layer already exists
    def addElementFromSignalR(self, elementJSON):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        id_already_in_offline = self.hasFeatureWithId(layer, elementJSON["serverKeyId"])

        if not id_already_in_offline and not self.multiElementsPostingInProgress():
            print("Adding from signal r")
            element = [elementJSON[field] for field in self.features]
            print("element: ", element)
            layer.startEditing()
            feature = QgsFeature(layer.fields())
            geometry = QgsGeometry.fromPointXY(QgsPointXY(element[0], element[1]))
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))

            feature.setGeometry(geometry)

            for i in range(len(self.field_definitions) - 1):  # except lastUpdate field
                feature.setAttribute(self.field_definitions[i][0], element[i + 2])  # skip lat and lng

            lastUpdatedForSignalR = WateringUtils.get_last_updated(self.ScenarioFK)
            feature.setAttribute("lastUpdate", lastUpdatedForSignalR)

            print("lastUpdatedForSignalR", lastUpdatedForSignalR)
            layer.addFeature(feature)
            layer.commitChanges()
            layer.triggerRepaint()

            WateringUtils.update_added_from_signalr(self.ScenarioFK, str(elementJSON["serverKeyId"]))
        else:
            print("Id already in offline, not adding as new.")

    def AddNewElementFromMapInteraction(self, x, y):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        layer.startEditing()

        feature = QgsFeature(layer.fields())
        geometry = QgsGeometry.fromPointXY(QgsPointXY(x, y))

        # we dont need to transform when we are adding element from the map
        # geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))

        feature.setGeometry(geometry)

        # TODO here we should call to add default values
        # for i in range(len(self.field_definitions)):
        #    feature.setAttribute(self.field_definitions[i][0], element[i+2])

        id = str(uuid.uuid4())
        temp_id = id[:10]

        feature.setAttribute("ID", temp_id)

        self.setDefaultValues(feature)
        feature.setAttribute("Last Mdf", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))

        layer.addFeature(feature)

        commit_success = layer.commitChanges()

        if commit_success:
            WateringUtils.write_sync_operation(layer, feature, WateringUtils.OperationType.ADD)

            print("Changes committed successfully.")
            print("Adding to server...")
            if self.connectorToServer:
                print("Connection established, adding ID in server locally")
                self.connectorToServer.addElementToServer(feature)
            else:
                print("No connection to send to server")
        else:
            print("Failed to commit changes.")

        QgsMapCanvas().refresh()
        return feature

    def deleteFeatureFromMapInteraction(self, feature):
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]

        self.Layer.startEditing()

        print("About to delete the feature ", feature.id(), " from ", self.LayerName)
        self.Layer.deleteFeature(feature.id())

        self.Layer.commitChanges()

        print("Changes after deleting feature are now done")
        if self.connectorToServer:
            self.connectorToServer.removeElementFromServer(feature["ID"])

    def writeShp(self):
        writer = QgsVectorFileWriter.writeAsVectorFormat(
            self.currentLayer, self.StorageShapeFile, "utf-8", self.currentLayer.crs(), "ESRI Shapefile"
        )

        if writer[0] == QgsVectorFileWriter.NoError:
            print(f"Shapefile for {self.LayerName} created successfully!")
        else:
            print("Error creating tanks Shapefile!")

    def openLayers(self, layer_symbol, layer_size):
        element_layer = QgsVectorLayer(self.StorageShapeFile, QFileInfo(self.StorageShapeFile).baseName(), "ogr")
        self.setElementSymbol(element_layer, layer_symbol, layer_size)
        element_layer.saveNamedStyle(self.FileQml)

    def setElementSymbol(self, layer, layer_symbol, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()
        symbol.changeSymbolLayer(0, QgsSimpleMarkerSymbolLayer(layer_symbol))
        symbol.setSize(layer_size)
        symbol.setColor(self.Color)
        if self.StrokeColor:
            symbol.symbolLayer(0).setStrokeColor(self.StrokeColor)
        layer.triggerRepaint()

    # Sync methods start
    def buildIndex(self):
        return set(feature["ID"] for feature in self.Layer.getFeatures())

    def processChange(self, change):
        if "serverKeyId" in change:
            change_id = change["serverKeyId"]

            if change["removed"] == True:
                return Change(self.Layer, change_id, "delete_from_server", [])

            if self.LayerName == "watering_pipes":
                attributes_definitions = self.features[1:]
                attributes = [change[attributes_definitions[i]] for i in range(len(attributes_definitions))]
                attributes.append(change["vertices"])
            else:
                attributes_definitions = self.features[3:]
                attributes = [change[attributes_definitions[i]] for i in range(len(attributes_definitions))]
                attributes.append(self.getTransformedCrs(change["lng"], change["lat"]))

            if change_id in self.idIndex:
                return Change(self.Layer, change_id, "update_from_server", attributes)

            return Change(self.Layer, change_id, "add_from_server", attributes)

    def getServerUpdates(self, data):
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        self.idIndex = self.buildIndex()
        self.addedFromSignalR = WateringUtils.get_added_from_signalr(self.ScenarioFK)
        self.changesList = [
            self.processChange(change) for change in data if change["serverKeyId"] not in self.addedFromSignalR
        ]
        return self.changesList

    def elementExistsInOffline(self, id):
        expression = f"\"ID\" = '{id}'"
        query = self.Layer.getFeatures(QgsFeatureRequest().setFilterExpression(expression))
        return any(True for _ in query)

    def getOfflineUpdates(self, lastUpdated):
        self.v2getOfflineUpdates()
        lastUpdated = self.adjustedDatetime(lastUpdated)
        self.Layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        self.offlineChangesList = []
        self.getChangesFromOffline(lastUpdated)
        self.getDeletedElementsFromOffline(lastUpdated)

        return self.offlineChangesList

    def v2getOfflineUpdates(self):
        self.add_data = WateringUtils.get_sync_operations(self.LayerName, WateringUtils.OperationType.ADD)
        self.updated_data = WateringUtils.get_sync_operations(self.LayerName, WateringUtils.OperationType.UPDATE)
        self.delete_data = WateringUtils.get_sync_operations(self.LayerName, WateringUtils.OperationType.DELETE)

    def getChangesFromOffline(self, lastUpdated):
        for feature in self.Layer.getFeatures():
            adjusted_feature_lastUpdated = self.adjustedDatetime(feature["lastUpdate"])
            if len(str(feature["ID"])) == 10:
                self.offlineChangesList.append(Change(self.Layer, feature["ID"], "add_from_offline", feature))
                self.syncAddingChanges.append(Change(self.Layer, feature["ID"], "add_from_offline", feature))
            if (adjusted_feature_lastUpdated > lastUpdated) and (len(str(feature["ID"])) == 36):
                self.offlineChangesList.append(Change(self.Layer, feature["ID"], "update_from_offline", feature))
                self.syncUpdatingChanges.append(Change(self.Layer, feature["ID"], "update_from_offline", feature))

    def getDeletedElementsFromOffline(self, lastUpdated):
        backup_layer_name = self.LayerName + "_backup.shp"

        backup_file_path = os.path.dirname(self.StorageShapeFile) + "/" + backup_layer_name
        layer = QgsVectorLayer(backup_file_path, "layer", "ogr")

        for feature in layer.getFeatures():
            adjusted_feature_lastUpdated = self.adjustedDatetime(feature["lastUpdate"])
            if adjusted_feature_lastUpdated > lastUpdated:
                self.offlineChangesList.append(Change(self.Layer, feature["ID"], "delete_from_offline", feature))
                self.syncDeletingChanges.append(Change(self.Layer, feature["ID"], "delete_from_offline", feature))

    def initMultiElementsPosting(self):
        change_types = [
            ("syncAddingChanges", self.postMultipleElements),
            ("syncUpdatingChanges", self.putMultipleElements),
            # ,('syncDeletingChanges', self.deleteMultipleElements)
        ]

        for change_type, process_method in change_types:
            changes_list = self.getFeatureJsons(getattr(self, change_type))
            if changes_list:
                process_method(changes_list)
                self.connectorToServer.update_layer_features(changes_list)

        self.deleteElementsOnSync()

    def getFeatureJsons(self, elements_list):
        jsonsList = []

        if elements_list and self.connectorToServer:
            for change in elements_list:
                if self.connectorToServer:
                    response, _, _, featureID = self.connectorToServer.getElementJson(change.data)
                    jsonsList.append((response, featureID))

        return jsonsList

    def deleteElementsOnSync(self):
        self.connectorToServer.serverRepository.deleteMultipleElements(self.delete_data)

    def postMultipleElements(self, jsonsList):
        self.connectorToServer.serverRepository.postMultipleElements(jsonsList)

    def putMultipleElements(self, jsonsList):
        self.connectorToServer.serverRepository.putMultipleElements(jsonsList)

    def deleteMultipleElements(self, jsonsList):
        self.connectorToServer.serverRepository.deleteMultipleElements(jsonsList)

    # Sync methods end

    def getTransformedCrs(self, lng, lat):
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")  # Web Mercator

        geom = QgsGeometry.fromPointXY(QgsPointXY(lng, lat))
        geom.transform(QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance()))
        point = geom.asPoint()

        return (point.x(), point.y())

    def adjustedDatetime(self, dt_str):
        # return datetime.fromisoformat(dt_str.replace("Z", ""))
        return QDateTime.fromString(str(dt_str), Qt.ISODateWithMs)

    def createBackupLayer(self):
        name = self.LayerName + "_backup"
        backup_layer_path = os.path.dirname(self.StorageShapeFile) + "/" + name + ".shp"

        fields = self.setElementFields(self.field_definitions)
        backup_layer = QgsVectorLayer(self.LayerType + self.destCrs.authid(), "New Layer", "memory")
        pr = backup_layer.dataProvider()
        pr.addAttributes(fields)
        backup_layer.updateFields()

        writer = QgsVectorFileWriter.writeAsVectorFormat(
            backup_layer, backup_layer_path, "utf-8", self.currentLayer.crs(), "ESRI Shapefile"
        )
        if writer[0] == QgsVectorFileWriter.NoError:
            print(f"Shapefile for {self.LayerName} created successfully!")
        else:
            print(f"Error creating {self.LayerName} Shapefile!")

        key = "backup_layer_path" + self.LayerName
        WateringUtils.setProjectMetadata(key, backup_layer_path)
        value = WateringUtils.getProjectMetadata(key)

    def hasFeatureWithId(self, layer, id_value):
        query = '"ID" = {}'.format(id_value)
        request = QgsFeatureRequest().setFilterExpression(query)
        features = layer.getFeatures(request)
        return any(features)

    def multiElementsPostingInProgress(self):
        return WateringUtils.getProjectMetadata("elementsPostingInProgress") != "default text"
