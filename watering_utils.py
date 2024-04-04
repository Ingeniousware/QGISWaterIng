# -*- coding: utf-8 -*-

# Import QGis
from PyQt5.QtCore import Qt
from qgis.PyQt import uic
from qgis.utils import iface
from qgis.core import Qgis, QgsProject, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QProgressBar
from PyQt5.QtCore import QVariant, QDateTime, QCoreApplication
from PyQt5.QtWidgets import QAction, QMessageBox, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, QThread, pyqtSignal

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

from .repositoriesLocalSHP.change import Change

#serverInput

class WateringUtils():  
    
    def set_progress(progress_value, progressBar):
        progressBar.setValue(progress_value)
        #progressBar.setFormat(f"%p%")

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
        return QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
    
    def getProjectId():
        return QgsProject.instance().readEntry("watering","project_id","default text")[0]
    
    def getProjectPath():
        return QgsProject.instance().readEntry("watering","project_path","default text")[0]
    
    def setProjectMetadata(field, value):
        QgsProject.instance().writeEntry("watering", field, value)
    
    def getProjectMetadata(field):
        return QgsProject.instance().readEntry("watering",field,"default text")[0]

    def isScenarioNotOpened():
        return WateringUtils.getScenarioId() == "default text"
    
    def isProjectOpened():
        project = QgsProject.instance()
        return bool(project.mapLayers() or project.fileName())
    
    def isWateringProject():
        scenarioId = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        projectId = QgsProject.instance().readEntry("watering","project_id","default text")[0] 
        #token = os.environ.get('TOKEN')
        print("scenario" + scenarioId)
        print("project" + projectId)
        return scenarioId != "default text" and projectId != "default text"
    
    def saveProjectBox():
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(None,
                                            "Save Project",
                                            "The current project has unsaved changes. Do you want to save it before creating a new project?",
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                #self.project_path = project.readEntry("watering","project_path","default text")[0]
                if WateringUtils.getProjectMetadata("project_path") != "default text":
                    if project.write():
                        iface.messageBar().pushMessage(self.tr(f"Project saved at {project.fileName()}"), level=Qgis.Success, duration=5)
                    else:
                        iface.messageBar().pushMessage(self.tr("Error"), self.tr("Failed to save the project."), level=1, duration=5)
                else:
                    iface.actionSaveProjectAs().trigger()
       
            elif response == QMessageBox.Cancel:
                return
            
    def getServerUrl():
        projectServerUrl = "default text"
        defaultUrl = "https://dev.watering.online"
        
        if WateringUtils.isProjectOpened():
            projectServerUrl =  QgsProject.instance().readEntry("watering","server_url","default text")[0]
            
        return defaultUrl if projectServerUrl == "default text" else projectServerUrl
    
    def getResponse(url, params):
        try:
            response = requests.get(url, params=params,
                                    headers={'Authorization': "Bearer {}".format(os.environ.get('TOKEN'))})
            if response.status_code == 200:
                    return response
                
        except requests.ConnectionError:
            iface.messageBar().pushMessage(("Error"), ("Failed to connect to WaterIng Server, check your connection."), level=1, duration=5)
        except requests.Timeout:
                iface.messageBar().pushMessage(("Error"), ("Request timed out."), level=1, duration=5)
        except:
            iface.messageBar().pushMessage(("Error"), ("Unable to connect to WaterIng."), level=1, duration=5)
                
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
            16: "Temperature"
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
            30: "Ampere"
            }
        return conditions.get(status)
    
    def get_app_data_path():
        platform = os.sys.platform

        if platform == "win32":
            # For Windows
            return os.environ['APPDATA']
        elif platform == "darwin":
            # For macOS
            return os.path.expanduser('~/Library/Application Support')
        elif platform == "linux" or platform == "linux2":
            # For Linux
            return os.path.expanduser('~/.local/share')
        else:
            # Other platforms or an error
            raise ValueError(f"Unsupported platform: {platform}")

    def getDateTimeNow():
        # Current UTC Time
        current_datetime_utc = datetime.now(pytz.utc)

        # Converts to format '2023-11-29T10:28:46.2756439Z'
        formatted_time = current_datetime_utc.strftime('%Y-%m-%dT%H:%M:%S.%f') + '0Z'
        
        return QDateTime.fromString(formatted_time, Qt.ISODateWithMs)

    def tr(message, context = "QGISPlugin_WaterIng"):
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
        random_chars = ''.join(random.choice(all_characters) for _ in range(3))

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

        last_update_index = layer.fields().indexOf('lastUpdate')
        
        if last_update_index == attribute_index: return 
        
        attrs[last_update_index] = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")

        layer.dataProvider().changeAttributeValues({feature_id: attrs})
        
        full_feature = layer.getFeature(feature_id)
        
        change = Change(layer, feature_id, "update_from_offline", full_feature)
        
        sync.offline_change_queue.append(change)
        
    def onGeometryChange(feature_id, old_geometry, new_geometry, layer, sync):
        with layer.edit():
            feature = layer.getFeature(feature_id)
            feature['lastMdf'] = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
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
            #return WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
            #return '2024-02-28T01:00:00.0000000Z'
            return WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")

    def getClosestNodeToWaterMeter():
        field_waterM_nodeFK='NodeID'
        field_dNodeFk='ID'

        waterM_layer = QgsProject.instance().mapLayersByName("watering_waterMeter")[0]
        demandN_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]

        waterM_layer.startEditing()

        for feature_x in waterM_layer.getFeatures():
            min_distance = float('inf')
            closest_feature_id = None

            for feature_y in demandN_layer.getFeatures():
                distance = feature_x.geometry().distance(feature_y.geometry())
                if distance < min_distance:
                    min_distance = distance
                    closest_feature_id = feature_y[field_dNodeFk]

            if closest_feature_id is not None:
                waterM_layer.changeAttributeValue(feature_x.id(), feature_x.fields().indexOf(field_waterM_nodeFK), closest_feature_id)

        waterM_layer.commitChanges()

        iface.messageBar().pushMessage("Success", "Successfully identified water meter nodes!", level=Qgis.Success, duration=6)
        
        print("Update completed.")
        
    def get_last_updated(scenario_key):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                json.dump({}, file)

        with open(file_path, 'r') as file:
            data = json.load(file)

        try:
            last_updated = data[WateringUtils.getProjectMetadata("project_id")]['scenarios'][scenario_key]['lastUpdated']
            return last_updated
        except KeyError:
            return WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
    
    def get_added_from_signalr(scenarioKey):
        file_path = WateringUtils.get_projects_json_path()
        projKey = WateringUtils.getProjectMetadata("project_id")
        with open(file_path, 'r') as file:
            data = json.load(file)

        if projKey in data and scenarioKey in data[projKey]['scenarios']:
            return data[projKey]['scenarios'][scenarioKey].get('addedFromSignalR', [])
        else:
            return None
        
    def clear_added_from_signalr(scenarioKey):
        file_path = WateringUtils.get_projects_json_path()
        projKey = WateringUtils.getProjectMetadata("project_id")
    
        with open(file_path, 'r') as file:
            data = json.load(file)

        if projKey in data and scenarioKey in data[projKey]['scenarios']:
            data[projKey]['scenarios'][scenarioKey]['addedFromSignalR'] = []

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            

    def update_added_from_signalr(scenarioKey, element_id):
        # element_id type: str
        file_path = WateringUtils.get_projects_json_path()
        projKey = WateringUtils.getProjectMetadata("project_id")
        
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        if projKey in data and scenarioKey in data[projKey]['scenarios']:
            if 'addedFromSignalR' not in data[projKey]['scenarios'][scenarioKey]:
                data[projKey]['scenarios'][scenarioKey]['addedFromSignalR'] = []
            data[projKey]['scenarios'][scenarioKey]['addedFromSignalR'].append(element_id)
        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        
    def get_watering_folder():
        folder_path = WateringUtils.get_app_data_path() + "/QGISWatering/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path
    
    def get_projects_json_path():
        folder_path = WateringUtils.get_watering_folder()
        return folder_path + 'projects.json'
    
    def update_last_updated(scenario_key):
        file_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                json.dump({}, file)

        with open(file_path, 'r') as file:
            data = json.load(file)

        project_key = WateringUtils.getProjectMetadata("project_id")
        if project_key in data and "scenarios" in data[project_key] and scenario_key in data[project_key]["scenarios"]:
            data[project_key]["scenarios"][scenario_key]["lastUpdated"] = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
        else:
            print("Project or Scenario key not found in the provided JSON.")
            return

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            
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
    
class WateringTimer():
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
            
class WateringSynchWorker(QObject):
    finished = pyqtSignal()
    isRunning = True
    
    def __init__(self, scenarioUnitOfWork):
        super().__init__()
        self.scenarioUnitOfWork = scenarioUnitOfWork

    def requestStop(self):
        self.isRunning = False
        
    def runSynch(self):
        self.scenarioUnitOfWork.newUpdateAll()
        self.finished.emit()
        