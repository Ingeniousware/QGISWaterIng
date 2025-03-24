# -*- coding: utf-8 -*-

"""
***************************************************************************
    pipesNetworkAnalysisFile.py
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


class PipeNetworkAnalysisFile(AbstractAnalysis_1):
    """Clase que representa los resultados de las tuberías en periodo extendido."""
    def __init__(self, directoryBase, analysisExecutionId, datetime, propertyPipes):
        """Constructor of PipeNetworkAnalysisLocal."""
        super().__init__(directoryBase, analysisExecutionId, datetime)
        self.LayerName = "watering_pipes"
        self.JoinField = "pipeKey"

        self.__propertyPipes = propertyPipes
        self.FieldsToAdd = [self.__propertyPipes]
        self.Field = f"{self.LayerNameCsv}_{self.__propertyPipes}"


    def elementAnalysisResultsDisplayed(self):
        pass


    def elementAnalysisResults(self, result_csv, analysisExecutionId):
        pass
