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

from abc import ABC, abstractmethod
import enum
import json
import shutil
import uuid
import os
import threading
import time
from datetime import datetime

import wntr

from qgis.PyQt import uic # type: ignore
from PyQt5.QtCore import QTimer, QVariant, QDateTime
from PyQt5.QtWidgets import QDockWidget, QMessageBox
from PyQt5.QtGui import QIcon
from qgis.core import QgsProject  # type: ignore



from ..watering_utils import WateringUtils

from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType
from ..INP_Manager.inp_utils import INP_Utils
from ..NetworkAnalysis.previous_and_next_analysis import SimulationsManager
from .watering_simulations_filter import WateringSimulationsFilter
from ..INP_Manager.INPManager import INPManager
from ..INP_Manager.dataType import Time_Options
from ..INP_Manager.inp_options_enum import INP_Options
from ..NetworkAnalysis.nodeNetworkAnalysisLocal import NodeNetworkAnalysisLocal
from ..NetworkAnalysis.pipeNetworkAnalysisLocal import PipeNetworkAnalysisLocal
from ..QGISEpanet.epanet import EpanetSimulator
# from ui.watering_analysis_1 import Simulators

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_analysis_dialog.ui"))


class WateringAnalysis_1(QDockWidget, FORM_CLASS):
    def __init__(self, iface):
        """Constructor."""
        super().__init__(iface.mainWindow())
        self.setupUi(self)

        self.typeSimulators = {
            Simulators.EPANET: {"description": "Toolkit de Epnet 2.2",
                                    "typeSim": Epanet_Simulator()},
            Simulators.WNTR: {"description": "WNTR",
                              "typeSim": WNTR_Simulator()},
            Simulators.WNTR_EPANET: {"description": "WNTR + Epnet 2.2",
                                     "typeSim": WNTR_Epanet_Simulator()},}

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
        
        self.__simulations_manager = SimulationsManager()
        self.__simulations_manager.TimeChanged.subscribe(self.onTimeChanged)
        
        self.filterPushButton.clicked.connect(self.filterSimulation)
        
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.procedimiento)

    def initializeRepository(self):
        # Clear combo boxes and lists
        self.analysis_box.clear()
        self.analysis_box2.clear()
        self.BoxSimulator.clear()
        self.BoxSimulator.addItems([item["description"] for item in self.typeSimulators.values()])
        self.BoxSimulator.setCurrentText("Toolkit de Epnet 2.2")
        self.listOfAnalysis = []
        self.listOfSimulators = []
        simulationsPath = os.path.join(INP_Utils.default_working_directory(), "Analysis")
        self.__simulations_manager.SimulationDirectory = simulationsPath

        if hasattr(self.analysis_box, 'addItems') and isinstance(self.__simulations_manager.DataSimulacions, list):
            valid_items = [item["datetime"] for item in self.__simulations_manager.DataSimulacions if "datetime" in item]
            # self.analysis_box.addItem("Select simulaction")
            self.analysis_box.addItems(valid_items)
            # self.analysis_box2.addItem("Select simulaction")
            self.analysis_box2.addItems([item["datetime"] for item in self.__simulations_manager.DataSimulacions])
    
        # # self.analysis_box.addItem("Select simulaction")
        # self.analysis_box.addItems([item["datetime"] for item in self.__simulations_manager.DataSimulacions])
        # # self.analysis_box2.addItem("Select simulaction")
        # self.analysis_box2.addItems([item["datetime"] for item in self.__simulations_manager.DataSimulacions])


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


    def filterSimulation(self):
        dlg = WateringSimulationsFilter(None)
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
        simulador = self.BoxSimulator.currentText()
        
        result: AbstractTypeSimulator = next((item["typeSim"] for item in self.typeSimulators.values() if item["description"] == simulador), None)
        if (result != None):
            result.Run()


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


# ================== Inicio de los modelos de simulación =========================================================
class AbstractTypeSimulator(ABC):
    def __init__(self):
        """"""
        pass


    def removerAnalysis(self):
        # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)


    def updateData(self, pathWork: str, dateTime: str):
        """
        ES - Método que actualiza los datos de las simulaciones en JSON.

        EN - Method that updates simulation data in JSON.

        Parameters
        ----------
        analysisExecutionId : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        time_for_analysis: int
            ES - Hora del análisis.

            EN - Hour of the analysis.
        """
        file_path = os.path.dirname(os.path.normpath(pathWork))
        fileName = os.path.join(file_path, "simulations.json")
        dataTimeStr = dateTime.translate(str.maketrans({":": "-", ".": "-"}))
        directoryPath = os.path.join(os.path.dirname(fileName), dataTimeStr)

        contenido = None
        temp = {"IsLocalcalculated": True,
            "category": 1,
            "directoryName": dataTimeStr,
            "datetime": dateTime,
            "description": "",
            "directoryPath": directoryPath}

        try:
            with open(fileName, "r") as f:
                contenido = json.load(f)
            contenido.append(temp)
            with open(fileName, "w") as f:
                json.dump(contenido, f, indent=4)
        except FileNotFoundError:
            contenido = [temp]
            with open(fileName, "w") as f:
                json.dump(contenido, f, indent=4)


    @abstractmethod
    def Run(self):
        """"""
        pass


class Epanet_Simulator(AbstractTypeSimulator):
    def __init__(self):
        """"""
        super().__init__()


    def Run(self):
        """Se obtienen los resultados de la simulación local con el Toolkit de Epanet 2.2"""

        self.removerAnalysis()
        # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.

        date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        # fecha_to_int = int(fecha_hora.strftime("%y%m%d%H%M%S"))
        # tempFile = f"S_{fecha_to_int}"
        dataTimeStr = date_time.translate(str.maketrans({":": "-", ".": "-"}))
        # tempFile = f"{fecha_hora}"

        inpManager = INPManager()
        inpManager.writeSections()

        inpFileTemp = INP_Utils.generate_directory(os.path.join(os.path.dirname(inpManager.OutFile), "Analysis", dataTimeStr))
        inp_for_sim = inpFileTemp + f"\\{dataTimeStr}.inp"

        try:
            shutil.copy(inpManager.OutFile, inp_for_sim)
        except FileNotFoundError:
            self.show_message("Error", "El archivo de origen no existe.", QMessageBox.critical)
        except PermissionError:
            self.show_message("Error", "No tienes permisos suficientes para copiar el archivo.", QMessageBox.critical)

        ep_sim = EpanetSimulator()
        results = ep_sim.run_sim(inp_for_sim)

        node_result = NodeResultType.pressure
        link_result = LinkResultType.flowrate

        nodeResult_at_0hr = results.node[node_result.name].loc[0 * 3600, :]
        linkResult_at_0hr = results.link[link_result.name].loc[0 * 3600, :]

        analysis_id = str(uuid.uuid4())
        time = datetime.now()
        units = inpManager.options[INP_Options.Hydraulics].inpfile_units
        nodeAnalysis = NodeNetworkAnalysisLocal(nodeResult_at_0hr, inpFileTemp, analysis_id, date_time, node_result)
        nodeAnalysis.Execute()

        pipeAnalysis = PipeNetworkAnalysisLocal(linkResult_at_0hr, inpFileTemp, analysis_id, date_time, units, link_result)
        pipeAnalysis.Execute()

        time: Time_Options = inpManager.options[INP_Options.Times]
        _, rtime, _ = INP_Utils.hora_to_int(time.duration)
        # print("---------------- Fin de los cáculos ------------------------")
        if (rtime > 0):
            for i in range(1, int(rtime)):
                analysis_id = str(uuid.uuid4())
                nodeResult_at_hr = results.node[node_result.name].loc[i * 3600, :]
                linkResult_at_hr = results.link[link_result.name].loc[0 * 3600, :]
                nodeAnalysis.elementAnalysisResults(nodeResult_at_hr, analysis_id)
                pipeAnalysis.elementAnalysisResults(linkResult_at_hr, analysis_id, units)

        self.updateData(inpFileTemp, date_time)
        print("0001: Fin de la simulación con el toolkit de Epanet 2.2.")



class WNTR_Simulator(AbstractTypeSimulator):
    def __init__(self):
        super().__init__()


    def Run(self):
        """Se obtienen los resultados de la simulación local con el WNTR"""
        print("0001: Inicio de la simulación con WNTR.")


class WNTR_Epanet_Simulator(AbstractTypeSimulator):
    def __init__(self):
        super().__init__()


    def Run(self):
        """Se obtienen los resultados de la simulación local con el Epanet de WNTR"""
        print("0001: Inicio de la simulación con Epanet de WNTR.")
        self.removerAnalysis()
            # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.

            date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            # fecha_to_int = int(fecha_hora.strftime("%y%m%d%H%M%S"))
            # tempFile = f"S_{fecha_to_int}"
            dataTimeStr = date_time.translate(str.maketrans({":": "-", ".": "-"}))
            # tempFile = f"{fecha_hora}"


            inpManager = INPManager()
            inpManager.writeSections()

            # options: INPOptions = INPOptions(None)
            # options.load()
            # self.writeSections()

            wn = wntr.network.WaterNetworkModel(inpManager.OutFile)
            # os.path.join(inpFile.OutFile, "Simulaciones", tempFile)
            # inpFileTemp = INP_Utils.generate_directory(inpFile.OutFile + "\\Simulaciones\\" + tempFile)
            inpFileTemp = INP_Utils.generate_directory(os.path.join(os.path.dirname(inpManager.OutFile), "Analysis", dataTimeStr))
            # inpFileTemp += "\\" + tempFile
            # inpFileTemp = inpFileTemp + f"\\{dataTimeStr}"

            # Simulate hydraulics
            sim = wntr.sim.EpanetSimulator(wn)
            # sim = wntr.sim.WNTRSimulator(wn)
            self._results = sim.run_sim(inpFileTemp + f"\\{dataTimeStr}")

            node_Result = NodeResultType.pressure

            nodeResult_at_0hr = self._results.node[node_Result.name].loc[0 * 3600, :]
            linkResult_at_0hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
            # pressure_at_5hr = results.node[NodeResultType.pressure.name].loc[0*3600, :]
            # print(pressure_at_5hr)
            # self._guid = str(uuid.uuid4())
            analysis_id = str(uuid.uuid4())
            time = datetime.now()
            units = inpManager.options[INP_Options.Hydraulics].inpfile_units
            nodeAnalysis = NodeNetworkAnalysisLocal(nodeResult_at_0hr, inpFileTemp, analysis_id, date_time, node_Result)
            nodeAnalysis.Execute()

            pipeAnalysis = PipeNetworkAnalysisLocal(linkResult_at_0hr, inpFileTemp, analysis_id, date_time, units)
            pipeAnalysis.Execute()

            time: Time_Options = inpManager.options[INP_Options.Times]
            _, rtime, _ = INP_Utils.hora_to_int(time.duration)
            # print("---------------- Fin de los cáculos ------------------------")
            if (rtime > 0):
                for i in range(1, int(rtime)):
                    analysis_id = str(uuid.uuid4())
                    nodeResult_at_hr = self._results.node[node_Result.name].loc[i * 3600, :]
                    linkResult_at_hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
                    nodeAnalysis.elementAnalysisResults(nodeResult_at_hr, analysis_id)
                    pipeAnalysis.elementAnalysisResults(linkResult_at_hr, analysis_id, units)

            self.updateData(inpFileTemp, date_time)



class Simulators(enum.IntEnum):
    """
    ES - Clase que contine los simuladores de redes hidráulicos implementados.

    EN - Class containing the implemented hydraulic network simulators.
    """
    EPANET = 1
    """
    ES - EPANET. Se hace referencia a la simulación de redes hidráulicas con el Toolkit de Epanet 2.2

    EN - EPANET. Reference is made to the simulation of hydraulic networks with the Epanet Toolkit 2.2.
    """
    WNTR = 2
    """
    ES - WNTR. Se hace referencia a la simulación de redes hidráulicas con WNTR.

    EN - WNTR. Reference is made to the simulation of hydraulic networks with WNTR.
    """
    WNTR_EPANET = 3
    """
    ES - WNTR_EPANET. Se hace referencia a la simulación de redes hidráulicas con el Toolkit de Epanet 2.2 implemtado en WNTR.

    EN - WNTR_EPANET. Reference is made to the simulation of hydraulic networks with the Epanet Toolkit 2.2 implemented in WNTR.
    """
# ================== Final de los modelos de simulación =========================================================