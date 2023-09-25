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
        self.listOfDataChannelsKey = []
        self.listOfDataSourcesKey = []
        self.hide_progress_bar()
        self.initializeRepository()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getChannelMeasurementsData(0))

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
        self.listOfDataChannelsKey = []
        
        url_DataChannels = "https://dev.watering.online/api/v1/MeasurementChannels"
        self.SourceFK =  self.listOfDataSourcesKey[indexValue]
        self.ProjectFK = QgsProject.instance().readEntry("watering","project_id","default text")[0]
        params = {'projectKeyId': "{}".format(self.ProjectFK), 'sourceKeyId': "{}".format(self.SourceFK)}
        response_analysis = requests.get(url_DataChannels, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.datachannels_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfDataChannelsKey.append((response_analysis.json()["data"][i]["serverKeyId"]))


    def initializeRepository(self):
        self.loadDataSource()

    
    def getChannelMeasurementsData(self, behavior):

        url_Measurements = "https://dev.watering.online/api/v1/measurements"
        channelFK =  self.listOfDataChannelsKey[self.datachannels_box.currentIndex()]
  
        params = {'channelKeyId': "{}".format(channelFK)}
        response_analysis = requests.get(url_Measurements, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        new_df = pd.DataFrame()
        for i in range(0, response_analysis.json()["total"]):
            #print((response_analysis.json()["data"][i]))
            df = pd.DataFrame([response_analysis.json()["data"][i]])
            temp_df = pd.DataFrame({'timeStamp': [df['timeStamp'][0]],'value': [df['value'][0]],})
            new_df = new_df.append(temp_df, ignore_index = True) 

        self.close()

        #new_df = pd.DataFrame({'timeStamp': [df['timeStamp'][0]],'value': [df['value'][0]],})
        """
        data = {'Date Time': [
            '2023-08-22 02:19:03',
            '2023-08-22 02:23:21',
            '2023-08-22 02:27:47',
            '2023-08-22 02:32:10',
            '2023-08-22 02:36:17'],
            'Value': [
            2.689487,
            2.750362,
            2.811238,
            2.870512,
            2.924979]
                }
                """

        tempdf = pd.DataFrame(new_df)
        tempdf['timeStamp'] = pd.to_datetime(tempdf['timeStamp'], format='%Y-%m-%d %H:%M:%S')
 
        new_df = tempdf.to_numpy()

         # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(new_df[:, 0], new_df[:, 1], marker='o', linestyle='-')
        plt.title('Value vs. Date Time')
        plt.xlabel('timeStamp')
        plt.ylabel('value')
        plt.grid(True)
        plt.show()
      
        
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