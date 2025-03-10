# -*- coding: utf-8 -*-

"""
***************************************************************************
    abstractAnalysisLocalNode.py
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


import csv
import os

from pandas import Series

from .abstractAnalysisLocal import AbstractAnalysisLocal
from ..INP_Manager.inp_utils import INP_Utils
from ..INP_Manager.node_link_ResultType import NodeResultType


from wntr.sim.results import SimulationResults
from qgis.core import QgsProject, QgsVectorLayer, QgsLayerTreeLayer # type: ignore


class AbstractAnalysisLocalNode(AbstractAnalysisLocal):
    """
    Clase base para la visualización de lo los resultado de la modelación en QGIS de proyectos locales (Nodes).
    """
    def __init__(self, nodeResult: Series, resultType: NodeResultType, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)
        self.__nodeResult = nodeResult
        self.__resultType = resultType


    def elementAnalysisResults(self):
        filename = self.analysisExecutionId

        elements = []
        date = self.datetime.replace(":", "")
        working_directory = INP_Utils.default_working_directory()
        date_folder_path = os.path.join(working_directory, "Analysis", date)
        date_folder_path = INP_Utils.generate_directory(date_folder_path)

        elements.append(["nodeKey", self.__resultType.name])
        name = self.__nodeResult.index.tolist()
        range_1 = len(name)
        resultValue = self.__nodeResult.values

        nodeKey = []
        for i in range(range_1):
            nodeKey.append(INP_Utils.get_key_element(name[i]))

        for i in range(range_1):
            subdatos = [nodeKey[i], round(resultValue[i], 4)]
            elements.append(subdatos)

        nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")

        with open(nodes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]