# -*- coding: utf-8 -*-

# Import QGis
from PyQt5.QtCore import Qt
from qgis.PyQt import uic
from qgis.utils import iface
from qgis.core import (
    Qgis,
    QgsJsonExporter,
    QgsProject,
    QgsFeatureRequest,
    QgsFeature,
    QgsField,
    QgsSymbol,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsSingleSymbolRenderer,
    edit,
)
from qgis.PyQt.QtWidgets import QProgressBar
from PyQt5.QtCore import QVariant, QDateTime, QCoreApplication
from PyQt5.QtWidgets import QAction, QMessageBox, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from PyQt5.QtCore import QTimer
from time import time, gmtime, strftime
from datetime import datetime
import requests
import os
import random
import string
import pytz
import socket
import json
from enum import Enum
from typing import Dict, Any

from .repositoriesLocalSHP.change import Change

# serverInput


class WateringUtils:

    def set_progress(progress_value, progressBar):
        progressBar.setValue(progress_value)
        # progressBar.setFormat(f"%p%")

    def timer_hide_progress_bar(progressBar):
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(progressBar.setVisible(False))
        timer.start(6000)
        progressBar.setFormat("Loading completed")

    def hide_progress_bar(progressBar):
        progressBar.setVisible(False)

    def show_progress_bar(progressBar):
        progressBar.setVisible(True)

    def getScenarioId():
        return QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]

    def getProjectId():
        return QgsProject.instance().readEntry("watering", "project_id", "default text")[0]

    def getProjectPath():
        return QgsProject.instance().readEntry("watering", "project_path", "default text")[0]

    def setProjectMetadata(field, value):
        QgsProject.instance().writeEntry("watering", field, value)

    def getProjectMetadata(field):
        return QgsProject.instance().readEntry("watering", field, "default text")[0]

    def isScenarioNotOpened():
        return WateringUtils.getScenarioId() == "default text"

    def isProjectOpened():
        project = QgsProject.instance()
        return bool(project.mapLayers() or project.fileName())

    def isWateringProject():
        scenarioId = QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]
        projectId = QgsProject.instance().readEntry("watering", "project_id", "default text")[0]
        # token = os.environ.get('TOKEN')
        print("scenario" + scenarioId)
        print("project" + projectId)
        return scenarioId != "default text" and projectId != "default text"

    def saveProjectBox():
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(
                None,
                "Save Project",
                "The current project has unsaved changes. Do you want to save it before creating a new project?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )

            if response == QMessageBox.Yes:
                # self.project_path = project.readEntry("watering","project_path","default text")[0]
                if WateringUtils.getProjectMetadata("project_path") != "default text":
                    if project.write():
                        iface.messageBar().pushMessage(
                            self.tr(f"Project saved at {project.fileName()}"), level=Qgis.Success, duration=5
                        )
                    else:
                        iface.messageBar().pushMessage(
                            self.tr("Error"), self.tr("Failed to save the project."), level=1, duration=5
                        )
                else:
                    iface.actionSaveProjectAs().trigger()

            elif response == QMessageBox.Cancel:
                return

    def getServerUrl():
        projectServerUrl = "default text"
        defaultUrl = "https://dev.watering.online"

        if WateringUtils.isProjectOpened():
            projectServerUrl = QgsProject.instance().readEntry("watering", "server_url", "default text")[0]

        return defaultUrl if projectServerUrl == "default text" else projectServerUrl

    def writeWateringMetadata(project_name, project_fk, scenario_name, scenario_fk):
        WateringUtils.setProjectMetadata("server_project_name", project_name)
        WateringUtils.setProjectMetadata("project_id", project_fk)
        WateringUtils.setProjectMetadata("scenario_name", scenario_name)
        WateringUtils.setProjectMetadata("scenario_id", scenario_fk)

    def get_response(url, params):
        absolute_url = WateringUtils.getServerUrl() + url
        try:
            response = requests.get(
                url, params=params, headers={"Authorization": "Bearer {}".format(os.environ.get("TOKEN"))}
            )
            if response.status_code == 200:
                return response

        except requests.ConnectionError:
            iface.messageBar().pushMessage(
                ("Error"), ("Failed to connect to WaterIng Server, check your connection."), level=1, duration=5
            )
        except requests.Timeout:
            iface.messageBar().pushMessage(("Error"), ("Request timed out."), level=1, duration=5)
        except:
            iface.messageBar().pushMessage(("Error"), ("Unable to connect to WaterIng."), level=1, duration=5)

    def send_post_request(url, params, json_data, headers, error_message):
        try:
            response = requests.post(url, params=params, json=json_data, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if error_message is not False:
                QMessageBox.information(None, "Error", WateringUtils.tr(error_message))
            return False

    def translateMeasurements(self, status):
        conditions = {
            0: "Unknown",
            1: "SubstanceConcent",
            2: "WaterLevel",
            3: "Pressure",
            4: "Flow",
            5: "RotationSpeed",
            6: "ClosePorcentage",
            10: "PressureOutPump",
            11: "PumpMotorElectIntensity",
            12: "VolumeFlowed",
            13: "VolumeConsumed",
            14: "WQORP",
            15: "WQPH",
            16: "Temperature",
        }

        return conditions.get(status)

    def translateUnits(self, status):
        conditions = {
            0: "Invariant",
            1: "seconds",
            2: "kg_div_m3",
            3: "m_div_s2",
            4: "bar",
            5: "Pa",
            6: "kPa",
            7: "MPa",
            8: "mws",
            9: "meters",
            10: "mm",
            11: "Kelvin",
            12: "grad_C",
            13: "cP",
            14: "Pa_mult_s",
            15: "kg_div_m_div_s",
            16: "m2_div_s",
            17: "Stokes",
            18: "kg",
            19: "kg_div_hour",
            20: "kg_div_s",
            21: "g_div_s",
            22: "liters_div_s",
            23: "m3_div_s",
            24: "m3_div_hour",
            25: "m3",
            26: "m_div_s",
            27: "kg_div_mol",
            28: "m2",
            29: "Unknown",
            30: "Ampere",
        }
        return conditions.get(status)

    def get_app_data_path():
        platform = os.sys.platform

        if platform == "win32":
            # For Windows
            return os.environ["APPDATA"]
        elif platform == "darwin":
            # For macOS
            return os.path.expanduser("~/Library/Application Support")
        elif platform == "linux" or platform == "linux2":
            # For Linux
            return os.path.expanduser("~/.local/share")
        else:
            # Other platforms or an error
            raise ValueError(f"Unsupported platform: {platform}")

    def getDateTimeNow():
        # Current UTC Time
        current_datetime_utc = datetime.now(pytz.utc)

        # Converts to format '2023-11-29T10:28:46.2756439Z'
        formatted_time = current_datetime_utc.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"

        return QDateTime.fromString(formatted_time, Qt.ISODateWithMs)

    def tr(message, context="QGISPlugin_WaterIng"):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(context, message)

    def generateRandomElementName1(elementInitial):
        # elementInitial, for instance, P for pipes
        # Return a combination of Uppercase letter + 2 random digits
        random_letter = random.choice(string.ascii_uppercase)
        random_number = random.randint(10, 99)
        return f"{elementInitial}-[{random_letter}{random_number}]"

    def generateRandomElementName(elementInitial):
        # elementInitial, for instance, P for pipes
        # Return a combination of digits and letters, lowercase or uppercase, in any order.
        all_characters = string.digits + string.ascii_letters
        random_chars = "".join(random.choice(all_characters) for _ in range(3))

        return f"{elementInitial}-[{random_chars}]"

    def getFeatureIsNewStatus(serverKeyId):
        data = WateringUtils.getProjectMetadata(serverKeyId)

        return True if data == "default text" else False

    def onChangesInAttribute(feature_id, attribute_index, new_value, layer, sync):
        print("----CHANGING FEATURE----")
        print(f"Layer: {layer.name()}")
        print(f"Feature ID: {feature_id}")
        print(f"Attribute Index: {attribute_index}")
        print(f"New Value: {new_value}")

        attrs = {attribute_index: new_value}

        last_update_index = layer.fields().indexOf("lastUpdate")

        if last_update_index == attribute_index:
            return

        attrs[last_update_index] = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")

        layer.dataProvider().changeAttributeValues({feature_id: attrs})

        full_feature = layer.getFeature(feature_id)

        change = Change(layer, feature_id, "update_from_offline", full_feature)

        WateringUtils.write_sync_operation(layer, full_feature, WateringUtils.OperationType.UPDATE)

        sync.offline_change_queue.append(change)

    def onGeometryChange(feature_id, old_geometry, new_geometry, layer, sync):
        with layer.edit():
            feature = layer.getFeature(feature_id)
            feature["lastMdf"] = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
            layer.updateFeature(feature)

        full_feature = layer.getFeature(feature_id)

        change = Change(layer, feature_id, "update_from_offline", full_feature)

        sync.offline_change_queue.append(change)

    def isInternetConnection():
        try:
            # try to connect to Google's DNS server
            socket.create_connection(("8.8.8.8", 53))
            return True
        except OSError:
            pass
        return False

    def scenarioKeyLastUpdate(scenarioFK):
        return scenarioFK + "last_general_update"

    def getLastUpdate(keyUpdate):
        date = WateringUtils.getProjectMetadata(keyUpdate)

        print("date: ", date)

        if date != "default text":
            return date
        else:
            # return WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
            # return '2024-02-28T01:00:00.0000000Z'
            return WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")

    def getClosestNodeToWaterMeter():
        field_waterM_nodeFK = "NodeID"
        field_dNodeFk = "ID"

        waterM_layer = QgsProject.instance().mapLayersByName("watering_waterMeter")[0]
        demandN_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]

        waterM_layer.startEditing()

        for feature_x in waterM_layer.getFeatures():
            min_distance = float("inf")
            closest_feature_id = None

            for feature_y in demandN_layer.getFeatures():
                distance = feature_x.geometry().distance(feature_y.geometry())
                if distance < min_distance:
                    min_distance = distance
                    closest_feature_id = feature_y[field_dNodeFk]

            if closest_feature_id is not None:
                waterM_layer.changeAttributeValue(
                    feature_x.id(), feature_x.fields().indexOf(field_waterM_nodeFK), closest_feature_id
                )

        waterM_layer.commitChanges()

        iface.messageBar().pushMessage(
            "Success", "Successfully identified water meter nodes!", level=Qgis.Success, duration=6
        )

        print("Update completed.")

    def get_last_updated(scenario_key):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)

        with open(file_path, "r") as file:
            data = json.load(file)

        try:
            last_updated = data[WateringUtils.getProjectMetadata("project_id")]["scenarios"][scenario_key][
                "lastUpdated"
            ]
            return last_updated
        except KeyError:
            return WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")

    def get_added_from_signalr(scenarioKey):
        file_path = WateringUtils.get_projects_json_path()
        projKey = WateringUtils.getProjectMetadata("project_id")
        with open(file_path, "r") as file:
            data = json.load(file)

        if projKey in data and scenarioKey in data[projKey]["scenarios"]:
            return data[projKey]["scenarios"][scenarioKey].get("addedFromSignalR", [])
        else:
            return None

    def clear_added_from_signalr(scenarioKey):
        file_path = WateringUtils.get_projects_json_path()
        projKey = WateringUtils.getProjectMetadata("project_id")

        with open(file_path, "r") as file:
            data = json.load(file)

        if projKey in data and scenarioKey in data[projKey]["scenarios"]:
            data[projKey]["scenarios"][scenarioKey]["addedFromSignalR"] = []

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def update_added_from_signalr(scenarioKey, element_id):
        # element_id type: str
        file_path = WateringUtils.get_projects_json_path()
        projKey = WateringUtils.getProjectMetadata("project_id")

        with open(file_path, "r") as file:
            data = json.load(file)

        if projKey in data and scenarioKey in data[projKey]["scenarios"]:
            if "addedFromSignalR" not in data[projKey]["scenarios"][scenarioKey]:
                data[projKey]["scenarios"][scenarioKey]["addedFromSignalR"] = []
            data[projKey]["scenarios"][scenarioKey]["addedFromSignalR"].append(element_id)

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_watering_folder():
        folder_path = WateringUtils.get_app_data_path() + "/QGISWatering/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def get_projects_json_path():
        folder_path = WateringUtils.get_watering_folder()
        return folder_path + "projects.json"

    def get_sync_json_path():
        folder_path = WateringUtils.get_watering_folder()
        path = (
            folder_path
            + "/"
            + WateringUtils.getProjectId()
            + "/"
            + WateringUtils.getScenarioId()
            + "watering_sync.json"
        )
        print(path)
        return path

    def update_last_updated(scenario_key):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)

        with open(file_path, "r") as file:
            data = json.load(file)

        project_key = WateringUtils.getProjectMetadata("project_id")
        if project_key in data and "scenarios" in data[project_key] and scenario_key in data[project_key]["scenarios"]:
            data[project_key]["scenarios"][scenario_key]["lastUpdated"] = WateringUtils.getDateTimeNow().toString(
                "yyyy-MM-dd hh:mm:ss"
            )
        else:
            print("Project or Scenario key not found in the provided JSON.")
            return

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def write_data_in_projects_json(scenario_key, key, insert_data):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)

        with open(file_path, "r") as file:
            data = json.load(file)

        project_key = WateringUtils.getProjectMetadata("project_id")
        if project_key in data and "scenarios" in data[project_key] and scenario_key in data[project_key]["scenarios"]:
            data[project_key]["scenarios"][scenario_key][key] = insert_data
        else:
            print("Project or Scenario key not found in the provided JSON.")
            return

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_data_from_projects_json(scenario_key, key):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)

        with open(file_path, "r") as file:
            data = json.load(file)

        project_key = WateringUtils.getProjectMetadata("project_id")
        if project_key in data and "scenarios" in data[project_key] and scenario_key in data[project_key]["scenarios"]:
            return data[project_key]["scenarios"][scenario_key].get(key, "Key not found.")
        else:
            print("Project or Scenario key not found in the provided JSON.")
            return None

    def delete_data_in_projects_json(scenario_key, key):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            print("JSON file does not exist.")
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        project_key = WateringUtils.getProjectMetadata("project_id")
        if project_key in data and "scenarios" in data[project_key] and scenario_key in data[project_key]["scenarios"]:
            if key in data[project_key]["scenarios"][scenario_key]:
                del data[project_key]["scenarios"][scenario_key][key]
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
                print(f"Key '{key}' and its value have been deleted.")
            else:
                print(f"Key '{key}' not found in the scenario '{scenario_key}'.")
        else:
            print("Project or Scenario key not found in the provided JSON.")

    def is_server_key_id_absent(layer, serverKeyId):
        query = f"\"id\" = '{serverKeyId}'"
        request = QgsFeatureRequest().setFilterExpression(query)
        features = layer.getFeatures(request)
        try:
            first_feature = next(features)
            return False
        except StopIteration:
            return True

    def success_message(message):
        iface.messageBar().pushMessage((message), level=Qgis.Success, duration=5)

    def error_message(message):
        iface.messageBar().pushMessage(("Error"), (message), level=1, duration=5)

    def add_feature_to_backup_layer(feature, layer):
        backup_layer_name = layer.name() + "_backup"
        backup_layer = QgsProject.instance().mapLayersByName(backup_layer_name)[0]
        backup_layer.startEditing()

        new_feat = QgsFeature(backup_layer.fields())
        new_feat.setGeometry(feature.geometry())
        new_feat.setAttributes(feature.attributes())
        lastUpdateIndex = new_feat.fields().indexFromName("lastUpdate")
        new_feat.setAttribute(lastUpdateIndex, WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
        backup_layer.addFeature(new_feat)

        print(f"adding feature {new_feat} to {backup_layer}")

        backup_layer.commitChanges()

    def createNewColumn(self, layerDest, name):
        layer = QgsProject.instance().mapLayersByName(layerDest)[0]
        if not layer:
            raise Exception(f"Layer '{layerDest}' not found in the project.")

        self.new_field_name = name
        if len(self.new_field_name) > 10:
            self.new_field_name = self.new_field_name[:10]

        if layer.fields().indexFromName(self.new_field_name) != -1:
            layer.startEditing()
            layer.dataProvider().deleteAttributes([layer.fields().indexFromName(self.new_field_name)])
            layer.commitChanges()

        if layer.fields().indexFromName(self.new_field_name) == -1:
            layer.startEditing()
            layer.dataProvider().addAttributes([QgsField(self.new_field_name, QVariant.Double)])
            layer.commitChanges()

            layer.startEditing()
            field_index = layer.fields().indexFromName(self.new_field_name)
            default_value = ""
            features = [(f.id(), {field_index: default_value}) for f in layer.getFeatures()]
            layer.dataProvider().changeAttributeValues({f[0]: f[1] for f in features})
            layer.commitChanges()

    def changeColors(layer, field_name, renderer_type):
        if renderer_type == "categorized":
            # Create categories
            categories = []
            # Category for value 1 (red)
            symbol1 = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol1.setColor(QColor(255, 0, 0))  # Red color
            category1 = QgsRendererCategory(1, symbol1, "Unconnected")
            categories.append(category1)
            # Category for value 0 (green)
            symbol0 = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol0.setColor(QColor(0, 255, 0))  # Green color
            category0 = QgsRendererCategory(None, symbol0, "Connected")
            categories.append(category0)
            # Create the categorized symbol renderer
            renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        else:
            # Single symbol renderer
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(QColor(255, 255, 255))  # Default to red color
            renderer = QgsSingleSymbolRenderer(symbol)

        # Set the renderer to the layer
        layer.setRenderer(renderer)
        # Refresh the layer
        layer.triggerRepaint()
        # Add the layer to the map
        QgsProject.instance().addMapLayer(layer)

    def delete_column(layer, name):
        field_index = layer.fields().indexFromName(name)
        if field_index != -1:
            with edit(layer):
                res = layer.dataProvider().deleteAttributes([field_index])
                layer.updateFields()
                return res
        return False

    # New general methods

    def requests_get(url, params):
        absolute_url = WateringUtils.getServerUrl() + url
        headers = {"Authorization": f"Bearer {os.environ.get('TOKEN')}"}
        try:
            response = requests.get(absolute_url, params=params, headers=headers)
            if response.status_code == 200:
                return response
            else:
                WateringUtils.error_message(
                    "Failed request to Watering server with status code: {}".format(response.status_code)
                )
                return False
        except requests.ConnectionError:
            WateringUtils.error_message("No connection.")
            return False
        except requests.Timeout:
            WateringUtils.error_message("Request to server timed out.")
            return False
        except Exception as e:
            WateringUtils.error_message(f"Unable to connect to WaterIng. Error: {str(e)}")
            return False

    def requests_post(url, json):
        absolute_url = WateringUtils.getServerUrl() + url
        headers = {"Authorization": f"Bearer {os.environ.get('TOKEN')}"}
        try:
            response = requests.post(absolute_url, json=json, headers=headers)
            if response.status_code == 200:
                return response
            else:
                WateringUtils.error_message(
                    "Failed request to Watering server with status code: {}".format(response.status_code)
                )
                return False
        except requests.ConnectionError:
            WateringUtils.error_message("No connection.")
            return False
        except requests.Timeout:
            WateringUtils.error_message("Request to server timed out.")
            return False
        except Exception as e:
            WateringUtils.error_message(f"Unable to connect to WaterIng. Error: {str(e)}")
            return False

    def requests_put(url, json):
        absolute_url = WateringUtils.getServerUrl() + url
        headers = {"Authorization": f"Bearer {os.environ.get('TOKEN')}"}
        try:
            response = requests.put(absolute_url, json=json, headers=headers)
            if response.status_code == 200:
                return response
            else:
                WateringUtils.error_message(
                    "Failed request to Watering server with status code: {}".format(response.status_code)
                )
                return False
        except requests.ConnectionError:
            WateringUtils.error_message("No connection.")
            return False
        except requests.Timeout:
            WateringUtils.error_message("Request to server timed out.")
            return False
        except Exception as e:
            WateringUtils.error_message(f"Unable to connect to WaterIng. Error: {str(e)}")
            return False

    def requests_delete(url):
        absolute_url = WateringUtils.getServerUrl() + url
        headers = {"Authorization": f"Bearer {os.environ.get('TOKEN')}"}
        try:
            response = requests.delete(absolute_url, headers=headers)
            if response.status_code == 200:
                return response
            else:
                WateringUtils.error_message(
                    "Failed request to Watering server with status code: {}".format(response.status_code)
                )
                return False
        except requests.ConnectionError:
            WateringUtils.error_message("No connection.")
            return False
        except requests.Timeout:
            WateringUtils.error_message("Request to server timed out.")
            return False
        except Exception as e:
            WateringUtils.error_message(f"Unable to connect to WaterIng. Error: {str(e)}")
            return False

    class OperationType(Enum):
        ADD = "add"
        UPDATE = "update"
        DELETE = "delete"

    def getWateringLayers():
        return [
            "watering_demand_nodes",
            "watering_reservoirs",
            "watering_tanks",
            "watering_pumps",
            "watering_valves",
            "watering_pipes",
            "watering_waterMeter",
            "watering_sensors",
        ]

    def write_sync_operation(layer, feature, operation_type: OperationType):
        sync_file_path = WateringUtils.get_sync_json_path()
        print(f"Sync file path: {sync_file_path}")

        if not os.path.exists(sync_file_path):
            print("Sync file does not exist. Creating directory and initial structure.")
            os.makedirs(os.path.dirname(sync_file_path), exist_ok=True)
            initial_structure = {
                layer: {"add": {}, "update": {}, "delete": {}} for layer in WateringUtils.getWateringLayers()
            }
            print(f"Initial structure: {initial_structure}")
            with open(sync_file_path, "w") as file:
                json.dump(initial_structure, file)
                print("Initial structure written to sync file.")

        with open(sync_file_path, "r") as file:
            sync_data = json.load(file)
            print(f"Loaded sync data: {sync_data}")

        layer_name = layer.name()
        feature_id = str(feature["ID"])
        print(f"Layer name: {layer_name}, Feature ID: {feature_id}")

        if layer_name not in sync_data:
            print(f"Layer '{layer_name}' not found in sync data. Adding layer.")
            sync_data[layer_name] = {"add": {}, "update": {}, "delete": {}}

        # Add feature data to appropriate operation type under the layer
        feature_data = json.loads(QgsJsonExporter(layer).exportFeature(feature))
        print(f"Feature data to be added: {feature_data}")
        sync_data[layer_name][operation_type.value][feature_id] = {"data": feature_data}
        print(f"Updated sync data: {sync_data}")

        # Write updated data back to file
        with open(sync_file_path, "w") as file:
            json.dump(sync_data, file, indent=4)
            print("Updated sync data written to sync file.")

    def get_sync_operations(layer_name: str = None, operation_type: OperationType = None) -> Dict[str, Any]:
        sync_file_path = WateringUtils.get_sync_json_path()
        print(f"Sync file path: {sync_file_path}")

        if not os.path.exists(sync_file_path):
            print("Sync file does not exist. Returning empty dictionary.")
            return {}

        with open(sync_file_path, "r") as file:
            sync_data = json.load(file)
            print(f"Loaded sync data: {sync_data}")

        if layer_name and operation_type:
            result = sync_data.get(layer_name, {}).get(operation_type.value, {})
            print(f"Returning sync operations for layer '{layer_name}' and operation type '{operation_type}': {result}")
            return result
        elif layer_name:
            result = sync_data.get(layer_name, {})
            print(f"Returning sync operations for layer '{layer_name}': {result}")
            return result
        print("Returning all sync operations.")
        return sync_data

    def clear_sync_file():
        sync_file_path = WateringUtils.get_sync_json_path()
        print(f"Sync file path: {sync_file_path}")
        initial_structure = {
            layer: {"add": {}, "update": {}, "delete": {}} for layer in WateringUtils.getWateringLayers()
        }
        print(f"Initial structure to clear sync file: {initial_structure}")

        with open(sync_file_path, "w") as file:
            json.dump(initial_structure, file, indent=4)
            print("Cleared sync file with initial structure.")

    def remove_synced_feature(layer_name: str, feature_id: str, operation_type: OperationType):
        sync_file_path = WateringUtils.get_sync_json_path()
        print(f"Sync file path: {sync_file_path}")

        with open(sync_file_path, "r") as file:
            sync_data = json.load(file)
            print(f"Loaded sync data: {sync_data}")

        if layer_name in sync_data and feature_id in sync_data[layer_name][operation_type.value]:
            print(
                f"Removing feature ID '{feature_id}' from layer '{layer_name}' and operation type '{operation_type}'."
            )
            del sync_data[layer_name][operation_type.value][feature_id]
        else:
            print(
                f"Feature ID '{feature_id}' not found in layer '{layer_name}' under operation type '{operation_type}'. No action taken."
            )

        with open(sync_file_path, "w") as file:
            json.dump(sync_data, file, indent=4)
            print("Updated sync data written to sync file after removal.")


    def generar_name_aleatorio(longitud = 3):

        caracteres = string.ascii_letters + string.digits

        return ''.join(random.choices(caracteres, k = longitud))


class WateringSynchWorker(QObject):
    finished = pyqtSignal()
    isRunning = True

    def __init__(self, scenarioUnitOfWork):
        super().__init__()
        self.scenarioUnitOfWork = scenarioUnitOfWork

    def requestStop(self):
        self.isRunning = False

    def runSynch(self):
        self.scenarioUnitOfWork.update_all()
        self.finished.emit()


class WateringTimer:
    timer = None

    @classmethod
    def setTokenTimer(cls):
        os.environ["TOKEN_TIMER"] = "True"
        cls.timer = QTimer()
        # Timer set for 8 hours
        cls.timer.start(28800000)
        cls.timer.timeout.connect(cls.unsetTokenTimer)

    @classmethod
    def unsetTokenTimer(cls):
        print("Token is now unvalid. Redo the login procedures.")
        os.environ["TOKEN_TIMER"] = "False"
        cls.timer.stop()
