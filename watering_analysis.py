# -*- coding: utf-8 -*-

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsProject, edit, QgsGraduatedSymbolRenderer, QgsRendererRangeLabelFormat, QgsClassificationEqualInterval
from qgis.core import QgsStyle, QgsSymbol, QgsClassificationLogarithmic, QgsClassificationQuantile, QgsLineSymbol, QgsGradientColorRamp
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

import os
import requests
from .NetworkAnalysis.nodeNetworkAnalysisRepository import NodeNetworkAnalysisRepository
from .NetworkAnalysis.pipeNetworkAnalysisRepository import PipeNetworkAnalysisRepository


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
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getAnalysisResults(0))
        self.BtGetAnalysisResultsBackward.clicked.connect(lambda: self.getAnalysisResults(1))
        self.BtGetAnalysisResultsForward.clicked.connect(lambda: self.getAnalysisResults(2))
        
    def initializeRepository(self):
        url_analysis = "https://dev.watering.online/api/v1/WaterAnalysis"
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        params = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        response_analysis = requests.get(url_analysis, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.analysis_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfAnalysis.append((response_analysis.json()["data"][i]["serverKeyId"],
                                         response_analysis.json()["data"][i]["simulationStartTime"]))

    def getAnalysisResults(self, behavior):
        analysisExecutionId = self.listOfAnalysis[self.analysis_box.currentIndex()][0]
        datetime = self.listOfAnalysis[self.analysis_box.currentIndex()][1]
        pipeNodeRepository = PipeNetworkAnalysisRepository(self.token, analysisExecutionId, datetime, behavior)    
        waterDemandNodeRepository = NodeNetworkAnalysisRepository(self.token, analysisExecutionId, datetime, behavior)                
        