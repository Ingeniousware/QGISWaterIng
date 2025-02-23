# -*- coding: utf-8 -*-

"""
***************************************************************************
    abstractAnalysisLocalPipe.py
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

from pandas import Series

from .abstractAnalysisLocal import AbstractAnalysisLocal
from ..INP_Manager.inp_utils import INP_Utils
from ..INP_Manager.node_link_ResultType import LinkResultType


from wntr.sim.results import SimulationResults
from qgis.core import QgsProject # type: ignore


class AbstractAnalysisLocalPipe(AbstractAnalysisLocal):
    """
    Clase base para la visualización de lo los resultado de la modelación en QGIS de proyectos locales (Nodes).
    """
    def __init__(self, linkResult: Series, resultType: LinkResultType, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)
        self.__linkResult = linkResult
        self.__resultType = resultType


    def elementAnalysisResults(self):
        filename = self.analysisExecutionId

        elements = []
        date = self.datetime.replace(":", "")
        working_directory = INP_Utils.default_working_directory()
        date_folder_path = os.path.join(working_directory, "Analysis", date)
        date_folder_path = INP_Utils.generate_directory(date_folder_path)
        
        elements.append(["Name", self.__resultType.name])
        name = self.__linkResult.index.tolist()
        range_1 = len(name)
        resultValue = self.__linkResult.values

        for i in range(range_1):
            subdatos = [name[i], resultValue[i]]
            elements.append(subdatos)

        pipes_filepath = os.path.join(date_folder_path, f"{filename}_Pipes.csv")

        with open(pipes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]