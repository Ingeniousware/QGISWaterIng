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
import matplotlib.pyplot as plt


class AnomalyDetection:

    def iqr_anomaly_detector(df, column="value", threshold=1.1):
        copy_data = df.copy()
        quartiles = dict(df[column].quantile([0.25, 0.50, 0.75]))
        iqr = quartiles[0.75] - quartiles[0.25]
        lower_threshold = quartiles[0.25] - (threshold * iqr)
        upper_threshold = quartiles[0.75] + (threshold * iqr)
        # print(f"Lower threshold: {lower_threshold}, \nUpper threshold: {upper_threshold}\n")
        copy_data["Predictions"] = df[column].apply(
            AnomalyDetection.find_anomalies, args=(lower_threshold, upper_threshold)
        )
        return copy_data, lower_threshold, upper_threshold

    def find_anomalies(value, lower_threshold, upper_threshold):

        if value < lower_threshold or value > upper_threshold:
            return 1
        else:
            return 0


class PlotController:

    def plot_Anomalies(self, anomaly, title, yLabel):

        categories = (anomaly[:, 2]).astype(int)
        colormap = np.array(
            [
                "g",
                "r",
            ]
        )

        figure = plt.figure(figsize=(13, 4))
        ax = figure.add_subplot(111)
        ax.plot(anomaly[:, 1], anomaly[:, 0], linestyle="-", color="green")
        ax.scatter(anomaly[:, 1], anomaly[:, 0], marker="o", s=4, linestyle="-", c=colormap[categories])
        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel(yLabel)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.3)

        figure.show()
        # plt.show()
        return figure

    plt.style.use("ggplot")

    def updateLivePlot(self, x_vec, y1_data, title, yLabel, line1):

        if line1 == []:
            plt.ion()
            fig = plt.figure(figsize=(13, 6))
            ax = fig.add_subplot(111)
            (line1,) = ax.plot(x_vec, y1_data, "-o", alpha=0.8, color="green")
            plt.ylabel(yLabel)
            plt.xlabel("Date")
            plt.xticks(rotation=45)
            plt.title(title)
            plt.tight_layout()
            plt.grid(True)
            plt.subplots_adjust(bottom=0.2)
            plt.show()

            """ start_time = x_vec[0]  
            end_time = x_vec[-1]
            plt.xlim([start_time, end_time]) """

        line1.set_data(x_vec, y1_data)
        """ if isinstance(x_vec[0], (int, float)):  # Check if x_vec is numeric
            x_min, x_max = ax.get_xlim()
            new_x_min = min(x_vec) if np.min(x_vec) < x_min else x_min
            new_x_max = max(x_vec) if np.max(x_vec) > x_max else x_max
            ax.set_xlim(new_x_min, new_x_max) """
        if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
            plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])

        ax = plt.gca()  # get the current axes
        ax.relim()  # make sure all the data fits
        ax.autoscale()  # auto-scale
        # only needed mpl < 1.5
        # ax.figure.canvas.draw_idle()       # re-draw the figure

        return line1
