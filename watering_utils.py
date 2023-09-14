# -*- coding: utf-8 -*-

# Import QGis
from PyQt5.QtCore import Qt
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QProgressBar

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
    