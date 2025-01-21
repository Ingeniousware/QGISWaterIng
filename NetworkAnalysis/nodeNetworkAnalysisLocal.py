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


from ..wntr.epanet.toolkit import ENepanet
from .abstractAnalysis import AbstractAnalysis

class AbstractAnalysisLocal(AbstractAnalysis):
    """"Constructor"""
    def __init__(self, enData: ENepanet, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)
        self.__enData = enData

class NodeNetworkAnalysisLocal(AbstractAnalysisLocal):
    """
    Clase que representa los resultdos de los nodes.
    """
    def __init__(self, enData: ENepanet, analysisExecutionId, datetime):
        """Constructor of NodeNetworkAnalysisLocal"""
        super().__init__(enData, analysisExecutionId, datetime)
        
        