# -*- coding: utf-8 -*-

# Import QGis
from PyQt5.QtCore import Qt
from qgis.PyQt import uic
from qgis.utils import iface
from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtWidgets import QProgressBar
from PyQt5.QtCore import QVariant, QDateTime, QCoreApplication
from PyQt5.QtWidgets import QAction, QMessageBox


from PyQt5.QtCore import QTimer
from time import time, gmtime, strftime
from datetime import datetime
import requests
import os
import random
import string

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
        token = os.environ.get('TOKEN')
        print("scenario" + scenarioId)
        print("project" + projectId)
        return scenarioId != "default text" and projectId != "default text" and token is not None
    
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
        current_datetime = datetime.now()
        qdatetime = QDateTime(current_datetime)
        return QVariant(qdatetime)
    

        # noinspection PyMethodMayBeStatic
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
    
    def generateRandomElementName(elementInitial):
        # elementInitial, for instance, P for pipes
        random_letter = random.choice(string.ascii_uppercase)
        random_number = random.randint(10, 99)
        return f"{elementInitial}-[{random_letter}{random_number}]"