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


from wntr.sim.results import SimulationResults


from ..INP_Manager.node_link_ResultType import NodeResultType
from qgis.PyQt.QtGui import QColor # type: ignore

from .abstractAnalysisLocalNode import AbstractAnalysisLocalNode

class NodeNetworkAnalysisLocal(AbstractAnalysisLocalNode):
    """
    Clase que representa los resultados de los nodes.
    """
    def __init__(self, nodeResult, analysisExecutionId, datetime, resultType = NodeResultType.pressure):
        """Constructor of NodeNetworkAnalysisLocal."""
        super().__init__(nodeResult, resultType, analysisExecutionId, datetime)
        self.UrlGet = ""
        self.KeysApi = ""
        self.Attributes = ""
        self.LayerName = "watering_demand_nodes"

        self.Field = f"Nodes_{datetime.replace(':', '_')}_{resultType.name}"
        self.StartColor = QColor(55, 148, 255)
        self.EndColor = QColor(255, 47, 151)
        self.Size = 3
        self.join_field = "nodeKey"
        self.fields_to_add = [resultType.name]

        self.elementAnalysisResults()
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime.replace(':', '_')}")
        self.joinLayersAttributes(f"Nodes_{datetime.replace(':', '_')}", self.LayerName, self.join_field, self.fields_to_add)

