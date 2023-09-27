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
from datetime import date, timedelta
import tkinter as tk
from tkinter import filedialog


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
        self.loadDataSource()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getChannelMeasurementsData(0))
        self.yaxis = WateringUtils()
        self.anomalyDetection = AnomalyDetection()
        self.plotAnomalys = PlotController()
        self.selectdate_box.addItem("Last 30 days")
        self.selectdate_box.addItem("Last 15 days")
        self.selectdate_box.addItem("Custom")
        # Hide custome dates until selected
        self.dateInicialLabel.hide()
        self.inicial_dateEdit.hide()
        self.dateFinalLabel.hide()
        self.final_dateEdit.hide()
        self.selectdate_box.currentIndexChanged.connect(self.checkUserControlState)
        self.DownloadDataToFile.clicked.connect(lambda: self.downloadData(0))

    def downloadData(self, behavior):
        root = tk.Tk()
        root.withdraw()

        # Ask the user for the save location and file name.
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])

        if not file_path:
            return
        try:
            df.to_csv(file_path, index=False)
            print(f"CSV file saved to {file_path}")
        except Exception as e:
            print(f"Error saving CSV file: {e}")
        

    def checkUserControlState(self):
        if self.selectdate_box.currentIndex() == 2:
            self.dateInicialLabel.show()
            self.inicial_dateEdit.show()
            self.dateFinalLabel.show()
            self.final_dateEdit.show()

        else:
            self.dateInicialLabel.hide()
            self.inicial_dateEdit.hide()
            self.dateFinalLabel.hide()
            self.final_dateEdit.hide()



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


    def get_date_range(self):
                                     
        # Check box to see the data from the last 30 days
        dateSelected = self.selectdate_box.currentIndex()

        if dateSelected == 0:
            finalDate = date.today()
            initialDate = finalDate - timedelta(days=30)
            
        elif dateSelected == 1 :
            finalDate = date.today()
            initialDate = finalDate - timedelta(days=15)

        else:
            # To visualize data from specific dates
            initialDate = self.inicial_dateEdit.date().toPyDate() 
            finalDate = self.final_dateEdit.date().toPyDate()
        
        initialDate = f"{initialDate} 00:00:00"
        finalDate =  f"{finalDate} 00:00:00"
        print(initialDate, finalDate)
        
        return(initialDate, finalDate)
    
    
    def getChannelMeasurementsData(self, behavior):

        url_Measurements = "https://dev.watering.online/api/v1/measurements"
        channelFK =  self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][0]
        
        initialDate, finalDate = (self.get_date_range())
        params = {'channelKeyId': "{}".format(channelFK), 'startDate': "{}".format(initialDate),'endDate': "{}".format(finalDate)}
        #params = {'channelKeyId': "{}".format(channelFK)}

        headers={'Authorization': "Bearer {}".format(self.token)}
        selectColumns = ['value', 'timeStamp']

        try:
            response_analysis = requests.get(url_Measurements, params=params, headers=headers)
            response_analysis.raise_for_status()
            data = response_analysis.json()["data"]

     
            df = pd.DataFrame(data)[selectColumns]
  
            df['timeStamp'] = pd.to_datetime(df['timeStamp'])


            anomaly = AnomalyDetection.iqr_anomaly_detector(df)
            

            title = self.datachannels_box.currentText()
            yLabel = (self.yaxis.translateMeasurements(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) 
                        + " " + "(" + self.yaxis.translateUnits(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) + ")")
        

            numpyAnomaly = anomaly.to_numpy()

            PlotController.plot_Anomalies(self,numpyAnomaly, title, yLabel)
          
    

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