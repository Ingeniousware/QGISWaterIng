# -*- coding: utf-8 -*-

"""
***************************************************************************
    nodeNetworkAnalysisLocal.py
    ---------------------
    Date                 : Enero 2025
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


import csv
import os
from qgis.PyQt.QtGui import QColor # type: ignore
from wntr.sim.results import SimulationResults

from .abstractAnalysisLocalPipe import AbstractAnalysisLocalPipe
from ..INP_Manager.node_link_ResultType import LinkResultType
from .abstractAnalysis import AbstractAnalysis_1
from ..INP_Manager.inp_utils import INP_Utils


class PipeNetworkAnalysisLocal(AbstractAnalysis_1):
    """Clase que representa los resultados de las tuberías locales."""

    def __init__(self, linkResult, directoryBase, analysisExecutionId, datetime, flow_unit: str, resultType = LinkResultType.flowrate):
        """Constructor of PipeNetworkAnalysisLocal."""
        super().__init__(directoryBase, analysisExecutionId, datetime)
        self.LayerName = "watering_pipes"
        self.JoinField = "pipeKey"
        self.FieldsToAdd = [resultType.name]
        # self.Size = 3
        self.__resultSimulation = linkResult
        self.__resultType = resultType
        self.Field = f"{self.LayerNameCsv}_{self.__resultType.name}"
        self.__flow_unit = flow_unit
        self.__hora = 0


    def elementAnalysisResultsDisplayed(self):
        # return super().elementAnalysisResultsDisplayed()
        elements = []

        elements.append([self.JoinField, self.__resultType.name])
        name = self.__resultSimulation.index.tolist()
        range_1 = len(name)
        if (self.__flow_unit == "LPS"):
            resultValue = [v * 1000 for v in self.__resultSimulation.values]
        else:
            resultValue = self.__resultSimulation.values

        pipeKey = []
        for i in range(range_1):
            pipeKey.append(INP_Utils.get_key_element(name[i]))

        for i in range(range_1):
            subdatos = [pipeKey[i], resultValue[i]]
            elements.append(subdatos)

        pipes_filepath = os.path.join(self.CsvDirectory, self.CsvFileName)

        with open(pipes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]

        self.updateData(self.AnalysisExecutionId, 0)


    def elementAnalysisResults(self, result_csv, analysisExecutionId, flow_unit: str):
        """ES - Método donde se implementa la lógica para generar el archivo CSV.

        EN - Method where the logic to generate the CSV file is implemented.

        Parameters
        ----------
        analysisExecutionId : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        result_csv : any
            ES - Resulatos que se van a guardar en un archivo CSV.

            EN - Results to be saved in a CSV file.

        flow_unit : str
            ES - Unidad de medida del flujo.

            EN - Unit of flow measurement.
        """
        elements = []

        elements.append([self.JoinField, self.__resultType.name])
        name = result_csv.index.tolist()
        range_1 = len(name)
        if (flow_unit == "LPS"):
            resultValue = [v * 1000 for v in result_csv.values]
        else:
            resultValue = result_csv.values

        pipeKey = []
        for i in range(range_1):
            pipeKey.append(INP_Utils.get_key_element(name[i]))

        for i in range(range_1):
            subdatos = [pipeKey[i], resultValue[i]]
            elements.append(subdatos)

        pipes_filepath = os.path.join(self.CsvDirectory, f"{analysisExecutionId}_Pipes.csv")

        with open(pipes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]

        self.__hora += 1
        self.updateData(analysisExecutionId, self.__hora)
