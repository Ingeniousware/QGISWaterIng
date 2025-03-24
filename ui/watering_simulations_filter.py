# -*- coding: utf-8 -*-

"""
***************************************************************************
    watering_simulations_filter.py
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


import os

from qgis.PyQt import uic # type: ignore
from PyQt5 import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_simulations_filter_dialog.ui"))


class WateringSimulationsFilter(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        
        self.__data = data