# -*- coding: utf-8 -*-

"""
***************************************************************************
    nodeNetworkAnalysisFile.py
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

from .abstractAnalysis import AbstractAnalysis_1


class NodeNetworkAnalysisFile(AbstractAnalysis_1):
    """"""
    def __init__(self, directoryBase, analysisExecutionId, datetime, propertyNode):
        """Constructor of NodeNetworkAnalysisFile."""
        super().__init__(directoryBase, analysisExecutionId, datetime)
        self.LayerName = "watering_demand_nodes"
        self.JoinField = "nodeKey"
        self.Size = 3

        self.__propertyNode = propertyNode
        self.FieldsToAdd = [self.__propertyNode]
        self.Field = f"{self.LayerNameCsv}_{self.__propertyNode}"


    # def __LoadCSVFirstElement(self, fileName: str):
    #     # Abrir el archivo CSV
    #     if (fileName is not None or fileName != ""):
    #         with open(fileName, mode='r', encoding='utf-8') as archivo:
    #             lector = csv.reader(archivo)
    #             return next(lector)

    #     return None


    def elementAnalysisResultsDisplayed(self):
        pass


    def elementAnalysisResults(self, result_csv, analysisExecutionId):
        pass