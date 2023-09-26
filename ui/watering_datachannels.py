# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QTimer

import os
import requests
from time import time, gmtime, strftime
from ..watering_utils import WateringUtils
from ..anomaly_detection import AnomalyDetection
from ..anomaly_detection import PlotController 

from ..NetworkAnalysis.nodeNetworkAnalysisRepository import NodeNetworkAnalysisRepository
from ..NetworkAnalysis.pipeNetworkAnalysisRepository import PipeNetworkAnalysisRepository

# Import libraries for chart measurments
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
        self.listOfDataChannelsInfo = []
        self.listOfDataSourcesKey = []
        self.hide_progress_bar()
        self.initializeRepository()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getChannelMeasurementsData(0))
        self.yaxis = WateringUtils()
        self.anomalyDetection = AnomalyDetection()
        self.plotAnomalys = PlotController()

    def loadDataSource(self):
        url_DataSources = "https://dev.watering.online/api/v1/DataSources"
        self.ProjectFK = QgsProject.instance().readEntry("watering","project_id","default text")[0]
        params = {'projectKeyId': "{}".format(self.ProjectFK)}
        response_analysis = requests.get(url_DataSources, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.datasource_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfDataSourcesKey.append((response_analysis.json()["data"][i]["serverKeyId"]))

        self.loadDataChannels(self.datasource_box.currentIndex())
        self.datasource_box.currentIndexChanged.connect(self.loadDataChannels)


    def loadDataChannels(self, indexValue):
        self.datachannels_box.clear()
        self.listOfDataChannelsInfo = []
        
        url_DataChannels = "https://dev.watering.online/api/v1/MeasurementChannels"
        self.SourceFK =  self.listOfDataSourcesKey[indexValue]
        self.ProjectFK = QgsProject.instance().readEntry("watering","project_id","default text")[0]
        params = {'projectKeyId': "{}".format(self.ProjectFK), 'sourceKeyId': "{}".format(self.SourceFK)}
        response_analysis = requests.get(url_DataChannels, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.datachannels_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfDataChannelsInfo.append((response_analysis.json()["data"][i]["serverKeyId"], 
                                               response_analysis.json()["data"][i]["measurement"],
                                               response_analysis.json()["data"][i]["units"]))

    def initializeRepository(self):
        self.loadDataSource()
    
    def getChannelMeasurementsData(self, behavior):

        url_Measurements = "https://dev.watering.online/api/v1/measurements"
        channelFK =  self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][0]

        #To visualize data from specific dates#
        #inicialDate, finalDate = str(self.inicial_dateEdit.date().toPyDate()), str(self.final_dateEdit.date().toPyDate())
        #inicialDate, finalDate = (inicialDate + " 00:00:00"), (finalDate + " 00:00:00")
        #params = {'channelKeyId': "{}".format(channelFK), 'startDate': "{}".format(inicialDate),'endDate': "{}".format(finalDate)}
        params = {'channelKeyId': "{}".format(channelFK)}
        headers={'Authorization': "Bearer {}".format(self.token)}
        selectColumns = ['value', 'timeStamp']

        try:
            response_analysis = requests.get(url_Measurements, params=params, headers=headers)
            response_analysis.raise_for_status()
            data = response_analysis.json()["data"]

            df = pd.DataFrame(data)[selectColumns]
            df['timeStamp'] = pd.to_datetime(df['timeStamp'], format='%Y-%m-%d %H:%M:%S')

            anomaly = AnomalyDetection.iqr_anomaly_detector(df)
            title = self.datachannels_box.currentText()
            yLabel = (self.yaxis.translateMeasurements(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) 
                        + " " + "(" + 
                      self.yaxis.translateUnits(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) + ")")
        
            PlotController.plot_anomalies(self,anomaly, title, yLabel)
    
            if not data:
                print("No data available.")
                return
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        except KeyError:
            print("Invalid response format.")

        self.close()
                
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