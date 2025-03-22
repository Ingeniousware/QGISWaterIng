# -*- coding: utf-8 -*-

"""
***************************************************************************
    nodeNetworkAnalysisLocal.py
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
from wntr.sim.results import SimulationResults


from qgis.PyQt.QtGui import QColor # type: ignore

from ..INP_Manager.node_link_ResultType import NodeResultType
from .abstractAnalysisLocalNode import AbstractAnalysisLocalNode
from .abstractAnalysis import AbstractAnalysis_1
from ..INP_Manager.inp_utils import INP_Utils

# class NodeNetworkAnalysisLocal(AbstractAnalysisLocalNode):
#     """
#     Clase que representa los resultados de los nodes.
#     """
#     def __init__(self, nodeResult, analysisExecutionId, datetime, resultType = NodeResultType.pressure):
#         """Constructor of NodeNetworkAnalysisLocal."""
#         super().__init__(nodeResult, resultType, analysisExecutionId, datetime)
#         self.UrlGet = ""
#         self.KeysApi = ""
#         self.Attributes = ""
#         self.LayerName = "watering_demand_nodes"

#         self.Field = f"Nodes_{datetime.replace(':', '_')}_{resultType.name}"
#         self.StartColor = QColor(55, 148, 255)
#         self.EndColor = QColor(255, 47, 151)
#         self.Size = 3
#         self.join_field = "nodeKey"
#         self.fields_to_add = [resultType.name]

#         self.elementAnalysisResults()
#         self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime.replace(':', '_')}")
#         self.joinLayersAttributes(f"Nodes_{datetime.replace(':', '_')}", self.LayerName, self.join_field, self.fields_to_add)


class NodeNetworkAnalysisLocal(AbstractAnalysis_1):
    """Clase que representa los resultados de los nodes locales."""
    def __init__(self, nodeResult, directoryBase, analysisExecutionId, datetime, resultType = NodeResultType.pressure):
        """Constructor of NodeNetworkAnalysisLocal."""
        super().__init__(directoryBase, analysisExecutionId, datetime)
        self.LayerName = "watering_demand_nodes"
        self.JoinField = "nodeKey"
        self.FieldsToAdd = [resultType.name]
        self.Size = 3
        self.__resultSimulation = nodeResult
        self.__resultType = resultType
        self.Field = f"{self.LayerNameCsv}_{self.__resultType.name}"
        self.__hora = 0


    def elementAnalysisResultsDisplayed(self):
        elements = []

        elements.append([self.JoinField, self.__resultType.name])
        name = self.__resultSimulation.index.tolist()
        range_1 = len(name)
        resultValue = self.__resultSimulation.values

        nodeKey = []
        for i in range(range_1):
            nodeKey.append(INP_Utils.get_key_element(name[i]))

        for i in range(range_1):
            subdatos = [nodeKey[i], round(resultValue[i], 4)]
            elements.append(subdatos)

        nodes_filepath = os.path.join(self.CsvDirectory, self.CsvFileName)

        with open(nodes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]

        self.updateData(self.AnalysisExecutionId, 0)


    def elementAnalysisResults(self, result_csv, analysisExecutionId):
        elements = []
        elements.append([self.JoinField, self.__resultType.name])
        name = result_csv.index.tolist()
        range_1 = len(name)
        resultValue = result_csv.values

        nodeKey = []
        for i in range(range_1):
            nodeKey.append(INP_Utils.get_key_element(name[i]))

        for i in range(range_1):
            subdatos = [nodeKey[i], round(resultValue[i], 4)]
            elements.append(subdatos)

        nodes_filepath = os.path.join(self.CsvDirectory, (analysisExecutionId + "_Node.csv"))

        with open(nodes_filepath, 'w', newline='') as csvfile:
            writer_csv = csv.writer(csvfile)
            [writer_csv.writerow(fila) for fila in elements]


        self.__hora += 1
        self.updateData(analysisExecutionId, self.__hora)