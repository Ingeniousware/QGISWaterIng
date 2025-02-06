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

from qgis.PyQt.QtGui import QColor # type: ignore

# from ..wntr.epanet.toolkit import ENepanet
from .analysisEmentType import AnalysisEmentType
from .abstractAnalysisLocal import AbstractAnalysisLocal
from ..INP_Manager.inp_utils import NodeLinkResultType
from wntr.sim.results import SimulationResults

class PipeNetworkAnalysisLocal(AbstractAnalysisLocal):
    """
    Clase que representa los resultados de las tuberías.
    """
    def __init__(self, results: SimulationResults, analysisExecutionId, datetime, analysisElemntType = AnalysisEmentType.PIPE, resultType = NodeLinkResultType.flowrate):
        """Constructor of PipeNetworkAnalysisLocal."""
        super().__init__(results, analysisElemntType, resultType, analysisExecutionId, datetime)
        self.UrlGet = ""
        self.KeysApi = ""
        self.Attributes = ""
        self.LayerName = "watering_pipes"

        self.Field = f"Pipes_{datetime.replace(':', '_')}_{resultType.name}"
        self.StartColor = QColor(55, 148, 255)
        self.EndColor = QColor(255, 47, 151)
        self.Size = 1
        self.join_field = "Name"
        self.fields_to_add = [resultType.name]

        self.elementAnalysisResults()
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Pipes.csv", f"Pipes_{datetime.replace(':', '_')}")
        self.joinLayersAttributes(f"Pipes_{datetime.replace(':', '_')}", self.LayerName, self.join_field, self.fields_to_add)