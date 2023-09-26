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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class AnomalyDetection():

    def iqr_anomaly_detector(df, column='value', threshold=1.1):
        copy_data = df.copy()
        quartiles = dict(df[column].quantile([.25, .50, .75]))
        iqr = quartiles[0.75] - quartiles[0.25]
        lower_threshold = quartiles[0.25] - (threshold * iqr)
        upper_threshold = quartiles[0.75] + (threshold * iqr)
        print(f"Lower threshold: {lower_threshold}, \nUpper threshold: {upper_threshold}\n")
        copy_data['Predictions'] = df[column].apply(AnomalyDetection.find_anomalies, args=(lower_threshold, upper_threshold))
        return copy_data
    
    def find_anomalies(value, lower_threshold, upper_threshold):
    
        if value < lower_threshold or value > upper_threshold:
            return 1
        else: return 0


class PlotController():

    def plot_anomalies(self,anomaly, title, yLabel):

        categories = anomaly['Predictions']       
        colormap = np.array(['g', 'r',])

        plt.figure(figsize=(15, 9))
        plt.plot(anomaly['timeStamp'],anomaly['value'], linestyle='-', color='green')
        plt.scatter(anomaly['timeStamp'],anomaly['value'], marker='o', linestyle='-', c=colormap[categories])
        #plt.scatter(y, x, marker='o', linestyle='-', c=colormap[categories])
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel(yLabel)
        plt.grid(True)
        plt.xticks(rotation=80)
        plt.show()

        """ def plot_anomalies(self, anomaly, x, y):
                
        colormap = np.where(anomaly['Predictions'], 'r', 'g')
        plt.figure(figsize=(16, 6))
        plt.plot(anomaly[:,4], anomaly[:,0], marker='o', linestyle='-', c=colormap)
        plt.title(self.datachannels_box.currentText())
        plt.xlabel('Date')
        plt.ylabel(self.yaxis.translateMeasurements(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) 
                        + " " + "(" + self.yaxis.translateUnits(self.listOfDataChannelsInfo[self.datachannels_box.currentIndex()][1]) + ")")
        plt.grid(True)
        plt.xticks(rotation=80)
        plt.show() """