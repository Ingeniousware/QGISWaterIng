# -*- coding: utf-8 -*-

"""
***************************************************************************
    analysisOptionsTool.py
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

from qgis.PyQt.QtWidgets import QFileDialog # type: ignore
from qgis.core import QgsProject

from ..watering_utils import WateringUtils

from ..INP_Manager.inp_options import INPOptions
from ..INP_Manager.INPManager import INPManager
from ..ui.watering_inp_options import WateringINPOptionsDialog

class AnalysisOptionsTool:
    def __init__(self, iface):
        self.iface = iface


    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        else:
            options: INPOptions = INPOptions(None)
            options.load()
            optionsDialog = WateringINPOptionsDialog(options)
            optionsDialog.show()