# -*- coding: utf-8 -*-

# Import QGis
from qgis.core import QgsProject, QgsVectorLayer, QgsMapLayer
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QAction, QMessageBox, QApplication, QMenu, QFileDialog, QToolButton
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from qgis.core import QgsMessageLog, QgsCoordinateTransform, QgsApplication

import json
import os
from .watering_login import WateringLogin

class WateringUtils:  
    def __init__(self, directory="", networkName="", iface=None):
        
        self.iface = iface
        self.ProjectDirectory = directory
        self.NetworkName = networkName
        
    