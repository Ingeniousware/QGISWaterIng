# -*- coding: utf-8 -*-

"""
***************************************************************************
    metricsAnalysisTool.py
    ---------------------
    Date                 : Marzo 2025
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

from ..INP_Manager.INPManager import INPManager
from qgis.PyQt.QtWidgets import QFileDialog # type: ignore
from qgis.core import QgsProject

from ..watering_utils import WateringUtils

class MetricsAnalysisTool:
    def __init__(self, iface):
        self.iface = iface


    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        else:
            print("0001: Metrics Analysis")