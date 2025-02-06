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
import enum
import os
import stat
from wntr.sim.results import SimulationResults


from qgis.PyQt.QtGui import QColor # type: ignore

# from ..wntr.epanet.toolkit import ENepanet
from .abstractAnalysisLocal import AbstractAnalysisLocal
from .analysisEmentType import AnalysisEmentType
from ..INP_Manager.inp_utils import NodeLinkResultType

class NodeNetworkAnalysisLocal(AbstractAnalysisLocal):
    """
    Clase que representa los resultados de los nodes.
    """
    def __init__(self, results: SimulationResults, analysisExecutionId, datetime, analysisElemntType = AnalysisEmentType.NODE, resultType = NodeLinkResultType.pressure):
        """Constructor of NodeNetworkAnalysisLocal."""
        super().__init__(results, analysisElemntType, resultType, analysisExecutionId, datetime)
        self.UrlGet = ""
        self.KeysApi = ""#["Name", "pressure", "waterDemand", "waterDemandCovered", "waterAge"]
        self.Attributes = ""#["Pressure", "Demand", "Demand C", "Age"]
        self.LayerName = "watering_demand_nodes"

        self.Field = f"Nodes_{datetime.replace(':', '_')}_{resultType.name}"
        self.StartColor = QColor(55, 148, 255)
        self.EndColor = QColor(255, 47, 151)
        self.Size = 3
        self.join_field = "Name"
        self.fields_to_add = [resultType.name]

        self.elementAnalysisResults()
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime.replace(':', '_')}")
        self.joinLayersAttributes(f"Nodes_{datetime.replace(':', '_')}", self.LayerName, self.join_field, self.fields_to_add)

