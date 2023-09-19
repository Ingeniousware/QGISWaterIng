# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject

import os
import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_optimization_dialog.ui'))


class WaterOptimization(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WaterOptimization, self).__init__(parent)
        self.setupUi(self)
        self.token = os.environ.get('TOKEN')
        self.ScenarioFK = None
        self.Solutions = []
        self.initializeRepository()
        
    def initializeRepository(self):
        url_optimization = "https://dev.watering.online/api/v1/Optimization"
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        params = {'scenarioKeyId': "{}".format(self.ScenarioFK), 'showRemoved': False}
        response = requests.get(url_optimization, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response.json()["total"]):
            self.problem_box.addItem(response.json()["data"][i]["name"])
            self.Solutions.append(response.json()["data"][i]["objectives"])
        
        self.loadSolutions(self.problem_box.currentIndex())
        self.problem_box.currentIndexChanged.connect(self.loadSolutions)
        
    def loadSolutions(self, index):
        self.solution_box.clear()
        
        for item in self.Solutions[index]:
            self.solution_box.addItem(item["name"])
        