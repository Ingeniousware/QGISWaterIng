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

from .abstractAnalysisLocal import AbstractAnalysisLocal
from ..INP_Manager.inp_utils import INP_Utils
from ..INP_Manager.node_link_ResultType import NodeResultType


from wntr.sim.results import SimulationResults
from qgis.core import QgsProject # type: ignore


class AbstractAnalysisLocalNode(AbstractAnalysisLocal):
    """
    Clase base para la visualización de lo los resultado de la modelación en QGIS de proyectos locales (Nodes).
    """
    def __init__(self, results: SimulationResults, resultType: NodeResultType, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)
        self.__results = results
        self.__resultType = resultType


    def elementAnalysisResults(self):
        filename = self.analysisExecutionId

        elements = []
        date = self.datetime.replace(":", "")
        working_directory = INP_Utils.default_working_directory()
        date_folder_path = os.path.join(working_directory, "Analysis", date)
        date_folder_path = INP_Utils.generate_directory(date_folder_path)
        
        elements.append(["Name", self.__resultType.name])
                            #  NodeLinkResultType.demand.name,
                            #  NodeLinkResultType.head.name,
                            #  NodeLinkResultType.pressure.name,
                            #  NodeLinkResultType.quality.name])
        range_1 = len(self.__results.node[self.__resultType.name].columns)

        resultValue = self.__results.node[self.__resultType.name].values.tolist()
            
        # headValue = self.__results.node[NodeLinkResultType.head.name].values.tolist()
        # pressureValue = self.__results.node[NodeLinkResultType.pressure.name].values.tolist()
        # qualityValue = self.__results.node[NodeLinkResultType.quality.name].values.tolist()

        name = self.__results.node[self.__resultType.name].columns.tolist()

        for i in range(range_1):
            subdatos = [name[i], resultValue[0][i]]
                        # demandValue[0][i],
                        # headValue[0][i],
                        # pressureValue[0][i],
                        # qualityValue[0][i]]
            elements.append(subdatos)

        nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")

        with open(nodes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]