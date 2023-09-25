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
        scenario_id, ok = QgsProject.instance().readEntry("watering",
                                            "scenario_id",
                                            "default text")
        
        return scenario_id
    
    def isScenarioNotOpened():
        
        return WateringUtils.getScenarioId() == "default text"
    
    def translateMeasurements(self, status):
        conditions = {0:"Created", 
                      1:"Evaluating",
                      2:"Evaluated",
                      3:"ErrorsOnEvaluation"}
        
        return conditions.get(status)