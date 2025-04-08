# -*- coding: utf-8 -*-

"""
***************************************************************************
    previous_and_next_analysis.py
    ---------------------
    Date                 : Marzo 2025
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


import json
import os



from qgis.core import QgsProject  # type: ignore
from qgis.core import (QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsVectorLayerJoinInfo, QgsClassificationQuantile, # type: ignore
                       QgsRendererRangeLabelFormat, QgsStyle, QgsGradientColorRamp, QgsGraduatedSymbolRenderer)

from .nodeNetworkAnalysisFile import NodeNetworkAnalysisFile
from .pipeNetworkAnalysisFile import PipeNetworkAnalysisFile
from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType

from wntr.epanet.toolkit import ENepanet


class Event:
    def __init__(self):
        self.__event = None


    def subscribe(self, func):
        self.__event = func


    # def unsubscribe(self, func):
    #     self.__subscribers.remove(func)

    def notify(self, previous: bool, next: bool):
        """
        ES - Notifica cunado el timpo del análisis cambio.
        
        EN - Notifies when the analysis time has changed
        
        Parameters
        ----------
        previous : bool
            ES - Si es verdadero, se puede ir al análisis anterior.

            EN - If true, you can go to the previous analysis.

        forward : bool
            ES - Si es verdadero, se puede ir al análisis siguiente.

            EN - If true, you can go to the next analysis.
        """
        if self.__event is not None:
            self.__event(previous, next)


class SimulationsManager:
    """ES - Clase que implementa la lógica para manegar las simulaciones realizada a la rede de estudio.

    EN - Class that implements the logic to manage the simulations performed on the study network."""

    def __init__(self):
        self.__fileName = "simulations.json"
        self.__simulactions_directory = None
        self.__dataSimulations = None

        self.TimeChanged = Event()

        self.__analysisOne = None
        self.__analysisTwo = None
        self.NodeProperty: NodeResultType = NodeResultType.pressure
        self.PipeProperty: LinkResultType = LinkResultType.flowrate
        self.__nodeProperty = self.NodeProperty.name
        self.__pipeProperty = self.PipeProperty.name
        self.__previousAndNextAnalysis = None


    def __loadJson(self, fileName):
        """Carga los datos del archivo JSON"""
        with open(fileName, "r") as file:
            return json.load(file)


    def __previous_and_next_analysis(self):
        fileName = self.AnalysisOne.get("directoryPath")
        self.__previousAndNextAnalysis = PreviousAndNextAnalysis(fileName)
        self.__previousAndNextAnalysis.TimeChanged.subscribe(self.onTimeChanged)
        self.__previousAndNextAnalysis.HoraActual = 0


    @property
    def SimulationDirectory(self):
        """ES - Propiedad que devuelve la ruta del directorio de las simulaciones.

        EN - Property that returns the path of the simulations directory."""
        return self.__simulactions_directory
    @SimulationDirectory.setter
    def SimulationDirectory(self, value):
        self.__simulactions_directory = os.path.join(value, self.__fileName)


    @property
    def DataSimulacions(self):
        """ES - Devuelve los datos de las simulaciones realizadas.

        En - Returns the data of the simulations performed."""
        if (self.__dataSimulations is None):
            try:
                self.__dataSimulations = self.__loadJson(self.SimulationDirectory)
                # self.__analysisOne = self.__dataSimulations[-1]
            except FileNotFoundError as e:
                self.__dataSimulations = None
                print("Error en el directorio: ", e)

        return self.__dataSimulations
    @DataSimulacions.setter
    def DataSimulacions(self, value):
        self.__dataSimulations = value


    @property
    def AnalysisOne(self):
        return self.__analysisOne
    @AnalysisOne.setter
    def AnalysisOne(self, value):
        self.__analysisOne = value
        self.__previous_and_next_analysis()


    @property
    def AnalysisTwo(self):
        return self.__analysisTwo
    @AnalysisTwo.setter
    def AnalysisTwo(self, value):
        self.__analysisTwo = value
        # self.__previous_and_next_analysis()


    @property
    def Previous_NextAnalysis(self):
        return self.__previousAndNextAnalysis


    def onTimeChanged(self, previous, next):
        self.TimeChanged.notify(previous, next)


    def SearchSimulation(self, text: str):
        """ES - Busca una simulación a partir del `text`.

        EN - Search for a simulation from the `text`

        Parameters
        ----------
        text : str
            ES - Texto a buscar.

            EN - Text to search.
        """
        for item in self.__dataSimulations:
            if text in item['directoryName'] or text in item['datetime']:
                return item
        return None


class PreviousAndNextAnalysis:
    """
    ES - Clase que implementa la lógica para moverse entre las horas de la simulación especificada.

    EN - Class that implements the logic for moving between the specified simulation times."""

    def __init__(self, analysis_directory):
        """Constructor of PreviousAndNextAnalysis"""
        # C:\Users\Carlos\AppData\Roaming\QGISWatering\eba59fc8-6194-480d-9ef6-779a75a4c5a6\69474b13-6e91-49d3-874d-6b7109b4b338\Simulations\Analysis\
        # 2025-03-17T11-09-39-818Z
        self.__nameFile = "analysis.json"
        self.__analysisDirectory = analysis_directory + f"\\{self.__nameFile}"
        self.__datos = self.__loadJson()
        self.__horaInicio = 0
        self.__horaFinal = self.__datos[-1]["hora"]

        self.TimeChanged = Event()
        self.HoraActual = 0


    def __loadJson(self):
        """Carga los datos del archivo JSON"""
        with open(self.__analysisDirectory, "r") as file:
            return json.load(file)


    def __getValues_for_hour(self, hour)->list:
        return [item for item in self.__datos if item["hora"] == hour]


    def __loadLayer(self, items: list):
        """Carga la capa de datos del archivo CSV"""
        # Se eliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)

        for item in items:
            item_type = item.get("type")
            if item_type == "Node":
                nodeAnalysis = NodeNetworkAnalysisFile(item.get("directoryBase"), item.get("id"), item.get("datetime"), item.get("property"))
                nodeAnalysis.Execute()
            elif item_type == "Pipes":
                pipeAnalysis = PipeNetworkAnalysisFile(item.get("directoryBase"), item.get("id"), item.get("datetime"), item.get("property"))
                pipeAnalysis.Execute()


    @property
    def HoraActual(self)->int:
        return self.__horaActual
    @HoraActual.setter
    def HoraActual(self, value: int):
        self.__horaActual = max(0, min(value, self.__horaFinal))

        if (self.__horaActual == 0):
            self.TimeChanged.notify(False, True)
        elif (self.__horaActual == self.__horaFinal):
            self.TimeChanged.notify(True, False)
        else:
            self.TimeChanged.notify(True, True)

        values = self.__getValues_for_hour(self.HoraActual)
        if values is not None:
            self.__loadLayer(values)


    # @property
    # def DataAnalysis(self):
    #     return self.__dataAnalysis
    # @DataAnalysis.setter
    # def DataAnalysis(self, value: list):
    #     self.__dataAnalysis = value


    def previous_analysis(self):
        """
        ES - Método que se mueva al análisis anterior.

        EN - Method that moves to the previous analysis."""
        self.HoraActual -= 1
        if (self.HoraActual < 0):
            self.HoraActual = 0
        # values = self.__getValues_for_hour(self.HoraActual)
        # if values is not None:
        #     self.__loadLayer(values)


    def next_analysis(self):
        """
        ES - Método que se mueva proximo análisis.

        EN - Method to be moved next analysis."""
        self.HoraActual += 1
        if (self.HoraActual < 0):
            self.HoraActual = 0
        # values = self.__getValues_for_hour(self.HoraActual)
        # if values is not None:
        #     self.__loadLayer(values)


    def play(self):
        self.HoraActual += 1
        if (self.HoraActual == self.__horaFinal):
            self.HoraActual = 0