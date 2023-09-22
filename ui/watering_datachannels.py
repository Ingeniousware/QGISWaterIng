# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QTimer

import os
import requests
from time import time, gmtime, strftime
from ..watering_utils import WateringUtils

from ..NetworkAnalysis.nodeNetworkAnalysisRepository import NodeNetworkAnalysisRepository
from ..NetworkAnalysis.pipeNetworkAnalysisRepository import PipeNetworkAnalysisRepository

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_datachannels_dialog.ui'))


class WateringDatachannels(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WateringDatachannels, self).__init__(parent)
        self.setupUi(self)
        self.token = os.environ.get('TOKEN')
        self.ProjectFK = None
        self.SourceFK = None
        self.listOfDataChannels = []
        self.hide_progress_bar()
        self.initializeRepository()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getChannelMeasurementsData(0))
        
    def initializeRepository(self):

       #read here the datasources from https://dev.watering.online/api/v1/DataSources, take the datasource selected by the user and use it when downloading the measurementchannels
        url_DataSources = "https://dev.watering.online/api/v1/DataSources"
        self.ServeKeyId = "73476ef2-d8e8-41ca-a37e-c73197c848f5"

        url_analysis = "https://dev.watering.online/api/v1/MeasurementChannels"
        self.SourceFK = "61dffbf4-76f8-44b1-961d-dafad685673b"
        self.ProjectFK = QgsProject.instance().readEntry("watering","project_id","default text")[0]
        params = {'projectKeyId': "{}".format(self.ProjectFK), 'sourceKeyId': "{}".format(self.SourceFK)}
        response_analysis = requests.get(url_analysis, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.analysis_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfDataChannels.append((response_analysis.json()["data"][i]["serverKeyId"]))

    def getChannelMeasurementsData(self, behavior):
        #read the measurements from https://dev.watering.online/api/v1/measurements

        """ self.show_progress_bar()
        analysisExecutionId = self.listOfDataChannels[self.analysis_box.currentIndex()][0]
        datetime = self.listOfDataChannels[self.analysis_box.currentIndex()][1]
        self.set_progress(33)  
        pipeNodeRepository = PipeNetworkAnalysisRepository(self.token, analysisExecutionId, datetime, behavior) 
        self.set_progress(67)  
        waterDemandNodeRepository = NodeNetworkAnalysisRepository(self.token, analysisExecutionId, datetime, behavior)
        self.set_progress(100)  
        self.timer_hide_progress_bar() """
        ...
        
    def set_progress(self, progress_value):
        t = time() - self.start
        hms = strftime("%H:%M:%S", gmtime(t))
        self.progressBar.setValue(progress_value)
        self.progressBar.setFormat(f"{hms} - %p%")

    def timer_hide_progress_bar(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_progress_bar)
        self.timer.start(6000)
        self.progressBar.setFormat("Loading completed")
        
    def hide_progress_bar(self):
        self.progressBar.setVisible(False)

    def show_progress_bar(self):
        self.progressBar.setVisible(True)
        self.start = time()