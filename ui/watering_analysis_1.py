# -*- coding: utf-8 -*-

"""
***************************************************************************
    watering_analysis_1.py
    ---------------------
    Date                 : Febrero 2025
    Copyright            : (C) 2025 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt import uic
from PyQt5.QtCore import QTimer, QVariant, QDateTime
from PyQt5.QtWidgets import QDockWidget, QMessageBox
from PyQt5.QtGui import QIcon

import os
from time import time
import threading
import time

from ..watering_utils import WateringUtils

from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType
from ..INP_Manager.inp_utils import INP_Utils
from ..NetworkAnalysis.previous_and_next_analysis import SimulationsManager
from .watering_simulations_filter import WateringSimulationsFilter

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_analysis_dialog.ui"))


class WateringAnalysis_1(QDockWidget, FORM_CLASS):
    def __init__(self, iface):
        """Constructor."""
        super().__init__(iface.mainWindow())
        self.setupUi(self)

        self.ScenarioFK = None
        self.listOfAnalysis = []
        self.listOfSimulators = []
        self.hide_progress_bar()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getAnalysisResults(0))
        self.BtGetAnalysisResultsBackward.clicked.connect(lambda: self.getAnalysisResults(1))
        self.BtGetAnalysisResultsForward.clicked.connect(lambda: self.getAnalysisResults(2))
        self.BtGetAnalysisResultsPlayPause.clicked.connect(lambda: self.playbutton(0))
        self.analysis_box2.hide()
        self.compareCheckBox.clicked.connect(self.checkUserControlState)
        self.is_playing = False
        self.new_field_name = None
        self.BtGetAnalysisResultsPlayPause.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/play.svg"))
        self.BtGetAnalysisResultsPlayPause.clicked.connect(self.switch_icon_play_pause)
        self.BtGetAnalysisResultsBackward.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/backward.svg"))
        self.BtGetAnalysisResultsForward.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/forward.svg"))
        self.BoxSelectType.addItem("What If")
        self.BoxSelectType.addItem("Replay")
        self.BoxSelectType.addItem("Look Ahead")
        self.BoxSelectType.addItem("Distribution Spectrum")
        self.BoxSelectType.addItem("Mark Upstream Line to Source")
        self.BoxSelectType.addItem("Mark Dowstream Line from Source")
        self.BoxSelectType.addItem("Leak Sensitivity")
        self.BoxSelectType.addItem("Leak Impact")
        self.BoxSelectType.addItem("Transient Analysis")
        self.BoxSelectType.addItem("Sectorization")
        self.BoxSelectType.addItem("Model Review")
        self.BoxSelectType.addItem("Connectivity")
        self.BoxSelectType.addItem("Graph Decomposition")
        self.BoxSelectType.addItem("Sector Identification")
        # Node and pipes property comboBox
        # self.nodesComboBox.addItem("Pressure")
        # self.nodesComboBox.addItem("Water Demand")
        # self.nodesComboBox.addItem("Water Age")
        self.nodesComboBox.addItems([item.name for item in NodeResultType])
        self.nodesComboBox.setCurrentText(NodeResultType.pressure.name)
        
        # self.pipesComboBox.addItem("Velocity")
        # self.pipesComboBox.addItem("Flow")
        # self.pipesComboBox.addItem("Headloss")
        self.pipesComboBox.addItems([item.name for item in LinkResultType])
        self.pipesComboBox.setCurrentText(LinkResultType.flowrate.name)

        self.BTExecute.clicked.connect(self.requestAnalysisExecution)
        self.startDateTime.setDateTime(QDateTime.currentDateTime())
        print("0001: Project path (at init WateringAnalysis):  ", WateringUtils.getProjectPath())
        
        simulationsPath = os.path.join(INP_Utils.default_working_directory(), "Analysis")
        self.__simulations_manager = SimulationsManager(simulationsPath)
        self.__simulations_manager.TimeChanged.subscribe(self.onTimeChanged)
        
        self.filterPushButton.clicked.connect(lambda: self.filterSimulation(self.__simulations_manager.DataSimulacions))
        
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.procedimiento)

    def initializeRepository(self):
        # Clear combo boxes and lists
        self.analysis_box.clear()
        self.analysis_box2.clear()
        self.BoxSimulator.clear()
        self.listOfAnalysis = []
        self.listOfSimulators = []
        # self.analysis_box.addItem("Select simulaction")
        self.analysis_box.addItems([item["datetime"] for item in self.__simulations_manager.DataSimulacions])
        # self.analysis_box2.addItem("Select simulaction")
        self.analysis_box2.addItems([item["datetime"] for item in self.__simulations_manager.DataSimulacions])


    def onTimeChanged(self, previous, next):
        self.BtGetAnalysisResultsBackward.setEnabled(previous)
        self.BtGetAnalysisResultsForward.setEnabled(next)


    def procedimiento(self):
        while not self.stop_event.is_set():
            self.__simulations_manager.Previous_NextAnalysis.play()


    def iniciar(self):
        self.thread.start()

    def detener(self):
        self.stop_event.set()  # Activar el flag
        self.thread.join()  # Esperar a que el hilo termine


    def filterSimulation(self, data):
        dlg = WateringSimulationsFilter()
        dlg.show()
        dlg.exec_()


    def checkUserControlState(self):
        if self.compareCheckBox.isChecked():
            self.analysis_box2.show()
        else:
            self.analysis_box2.hide()


    def getAnalysisResults(self, analysis):
        if (analysis == 0):
            text = self.analysis_box.currentText()
            data = self.__simulations_manager.SearchSimulation(text)
            self.__simulations_manager.AnalysisOne = data
        elif(analysis == 1):
            self.__simulations_manager.Previous_NextAnalysis.previous_analysis()
        elif (analysis == 2):
            self.__simulations_manager.Previous_NextAnalysis.next_analysis()
        else:
            print("0001: No se a Implementado la lógica")


    def switch_icon_play_pause(self):
        if self.is_playing:
            icon_path = ":/plugins/QGISPlugin_WaterIng/images/play.svg"
        else:
            icon_path = ":/plugins/QGISPlugin_WaterIng/images/stop.svg"
        self.BtGetAnalysisResultsPlayPause.setIcon(QIcon(icon_path))
        self.is_playing = not self.is_playing

    def playbutton(self, behavior):
        if not self.is_playing:
            self.iniciar()
        else:
            self.detener()

    def createNewColumns(self, layerDest, name):
        print("0001: Implementar la lógica")

    def fieldCalculator(self, repository, repository2):
        print("0001: Implementar la lógica")

    def requestAnalysisExecution(self):
        print("0001: Implementar la lógica")

    def show_message(self, title, text, icon):
        """Display a QMessageBox with given attributes."""
        message_box = QMessageBox()
        message_box.setIcon(icon)
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()

    def postToAnalysisAPI(
        self, name, startDate, duration, formatted_now, new_guid, selectedSimulator, simulatorFK, timeStep
    ):
        print("0001: Implementar la lógica")


    def set_progress(self, progress_value):
        print("0001: Implementar la lógica")


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
