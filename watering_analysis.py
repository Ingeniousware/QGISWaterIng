# -*- coding: utf-8 -*-

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsProject
from qgis.utils import iface

import os
import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_analysis_dialog.ui'))


class WateringAnalysis(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WateringAnalysis, self).__init__(parent)
        self.setupUi(self)
        self.token = os.environ.get('TOKEN')
        self.ScenarioFK = None
        self.listOfAnalysis = []
        self.initializeRepository()

    def initializeRepository(self):
        
        url_analysis = "https://dev.watering.online/api/v1/WaterAnalysis"
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        params = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        response_analysis = requests.get(url_analysis, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.analysis_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfAnalysis.append((response_analysis.json()["data"][i]["name"],
                                         response_analysis.json()["data"][i]["serverKeyId"]))