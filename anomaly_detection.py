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
from matplotlib.widgets import Button


class AnomalyDetection():

    def iqr_anomaly_detector(df, column='value', threshold=1.1):
        copy_data = df.copy()
        quartiles = dict(df[column].quantile([.25, .50, .75]))
        iqr = quartiles[0.75] - quartiles[0.25]
        lower_threshold = quartiles[0.25] - (threshold * iqr)
        upper_threshold = quartiles[0.75] + (threshold * iqr)
        #print(f"Lower threshold: {lower_threshold}, \nUpper threshold: {upper_threshold}\n")
        copy_data['Predictions'] = df[column].apply(AnomalyDetection.find_anomalies, args=(lower_threshold, upper_threshold))
        return copy_data
    
    def find_anomalies(value, lower_threshold, upper_threshold):
    
        if value < lower_threshold or value > upper_threshold:
            return 1
        else: return 0


class PlotController():

    def plot_Anomalies(self,anomaly, title, yLabel):

        categories = (anomaly[:,2]).astype(int)
        colormap = np.array(['g', 'r',])

        plt.figure()
        plt.plot(anomaly[:,1],anomaly[:,0], linestyle='-', color='green')
        plt.scatter(anomaly[:,1],anomaly[:,0], marker='o',s=4, linestyle='-', c=colormap[categories])
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel(yLabel)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.subplots_adjust(bottom = 0.3)
        
        plt.show()
    