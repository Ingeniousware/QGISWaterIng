# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QTimer

import os
import requests
from time import time, gmtime, strftime
from ..watering_utils import WateringUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_analysis_dialog.ui'))


class WateringAddDemandNode(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WateringAddDemandNode, self).__init__(parent)
        self.setupUi(self)