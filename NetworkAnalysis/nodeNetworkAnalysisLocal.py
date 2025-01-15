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


from .abstractAnalysis import AbstractAnalysis


class NodeNetworkAnalysisLocal(AbstractAnalysis):
    """
    Clase que representa los resultdos de los nodes.
    """
    def __init__(self, analysisExecutionId, datetime, nodeProperty):
        """Constructor of NodeNetworkAnalysisLocal"""
        super().__init__(analysisExecutionId, datetime)
        