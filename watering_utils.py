# -*- coding: utf-8 -*-

# Import QGis
from PyQt5.QtCore import Qt
from qgis.PyQt import uic
from qgis.utils import iface
from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtWidgets import QProgressBar
from PyQt5.QtCore import QCoreApplication

from PyQt5.QtCore import QTimer
from time import time, gmtime, strftime

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
    
    def isScenarioNotOpened():
        return WateringUtils.getScenarioId() == "default text"
    
    def isProjectOpened():
        project = QgsProject.instance()
        return bool(project.mapLayers() or project.fileName())
            
    def getServerUrl():
        projectServerUrl = "default text"
        defaultUrl = "https://dev.watering.online"
        
        if WateringUtils.isProjectOpened():
            projectServerUrl =  QgsProject.instance().readEntry("watering","server_url","default text")[0]
            
        return defaultUrl if projectServerUrl == "default text" else projectServerUrl
        
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