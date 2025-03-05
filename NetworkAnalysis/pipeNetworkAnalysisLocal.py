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


from .abstractAnalysisLocalPipe import AbstractAnalysisLocalPipe
from ..INP_Manager.node_link_ResultType import LinkResultType
from wntr.sim.results import SimulationResults

class PipeNetworkAnalysisLocal(AbstractAnalysisLocalPipe):
    """
    Clase que representa los resultados de las tuberías.
    """
    def __init__(self, linkResult, analysisExecutionId, datetime, resultType = LinkResultType.flowrate, flow_unit = "LPS"):
        """Constructor of PipeNetworkAnalysisLocal."""
        super().__init__(linkResult, resultType, analysisExecutionId, datetime, flow_unit)
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