# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import os
import requests
from time import time, gmtime, strftime
from ..watering_utils import WateringUtils
from ..anomaly_detection import AnomalyDetection
from ..anomaly_detection import PlotController
from ..repositories.getDataRepository import getDataRepository

from ..NetworkAnalysis.nodeNetworkAnalysisRepository import NodeNetworkAnalysisRepository
from ..NetworkAnalysis.pipeNetworkAnalysisRepository import PipeNetworkAnalysisRepository

# Import libraries for chart measurments
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import time
import threading




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
        self.DownloadDataToFile.clicked.connect(self.downloadData)
        self.RefreshGraphs.clicked.connect(self.updateGraphs)
    

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


    def getChannelMeasurementsData(self, behavior):
        
        data = getDataRepository.createDataFrame_api(self)
        
        if data.empty:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Error")
            message_box.setText("No data available to graph")
            message_box.setStandardButtons(QMessageBox.Ok)

            message_box.exec_()
            return
        
        data['timeStamp'] = pd.to_datetime(data['timeStamp'])

        anomaly = AnomalyDetection.iqr_anomaly_detector(data)
        title = self.datachannels_box.currentText()
        yLabel = (self.yaxis.translateMeasurements(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) 
                        + " " + "(" + self.yaxis.translateUnits(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) + ")")
        numpyAnomaly = anomaly.to_numpy()

        #WateringDatachannels.refreshData(self,numpyAnomaly, title, yLabel)
        refresh_State = self.updateGraphs(0)
        if refresh_State == 0:
            print("its inside the if")
            PlotController.plot_Anomalies(self,numpyAnomaly, title, yLabel)
            
        else:
            
            x_vec = numpyAnomaly[:,1]
            y_vec = numpyAnomaly[:,0]
            line1 = []
            threading.Thread(target=WateringDatachannels.refreshData(self, x_vec, y_vec, line1, title, yLabel), daemon = True).start()
            #WateringDatachannels.refreshData(self, x_vec, y_vec, line1, title, yLabel)
    
        self.close()

    def updateGraphs(self, behavior):
        refresh_State = self.RefreshGraphs.checkState()
        return refresh_State

    def refreshData(self, x_vec, y_vec, line1, title, yLabel):

        #line1 = PlotController.live_plotter(self,x_vec,y_vec,title, yLabel,line1)
        counter = 0

        while True:
            df = getDataRepository.createDataFrame_api(self)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'])
            lastValue = df['value'].iloc[-1]
            lastDate = df['timeStamp'].iloc[-1]

            previousLastValue = pd.DataFrame(x_vec).iloc[-1]
            print(lastValue,previousLastValue, lastDate)

            if lastDate == previousLastValue.iloc[-1]:
                counter += 1
                time.sleep(5)
                print("No new data")
            else:
                counter +=1
                #lastDate = datetime.now()
                """ y_vec[-1] = lastValue
                x_vec[-1] = lastDate """
                y_vec = np.append(y_vec,lastValue)
                x_vec = np.append(x_vec,lastDate)
                #line1 = PlotController.live_plotter(self, x_vec,y_vec,title, yLabel,line1)
                print("Plotting new values")
                time.sleep(5)
        
            #print(y_vec,x_vec)
            line1 = PlotController.live_plotter(self, x_vec,y_vec,title, yLabel,line1)
            self.close()
            #time.sleep(2)
            if counter == 10:
                    print("End of loop")
                    break
          
    def downloadData(self):

        dataFrame = getDataRepository.createDataFrame_api(self)
        
        if dataFrame.empty:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Error")
            message_box.setText("No data available to download")
            message_box.setStandardButtons(QMessageBox.Ok)

            message_box.exec_()
            return
                
        dataFrame['value'],dataFrame['timeStamp'] = dataFrame['value'].astype(str), dataFrame['timeStamp'].astype(str)
        
        i_Date, f_Date = getDataRepository.get_date_range(self)
        for char in ("-",":"," "):
            i_Date = i_Date.replace(char, "")
            f_Date = f_Date.replace(char, "")

        file_name = QFileDialog.getSaveFileName(parent = None, caption="Select file", filter="CSV File (*.csv)", 
                                                directory = (str(self.datachannels_box.currentText()) + " " + f_Date + "-" + i_Date))    
        
        dataFrame.to_csv((file_name[0]), index=True)
        print(f'DataFrame saved to {file_name[0]}')

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