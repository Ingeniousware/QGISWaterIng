# -*- coding: utf-8 -*-

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsProject, edit
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
        self.BtGetAnalysisResults.clicked.connect(self.demandNodesAnalysisResults)
        self.analysisExecutionId = self.listOfAnalysis[self.analysis_box.currentIndex()][0]
        self.datetime = self.listOfAnalysis[self.analysis_box.currentIndex()][1]
        self.behavior = 0
        
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
    
    def getResponse(self, url):
        params = {'analysisExecutionId': "{}".format(self.analysisExecutionId), 'datetime': "{}".format(self.datetime),
                          'behavior': "{}".format(self.behavior)}
        response = requests.get(url, params=params,
                           headers={'Authorization': "Bearer {}".format(self.token)})
        return response
    
    def demandNodesAnalysisResults(self):     
        url_node_results = "https://dev.watering.online/api/v1/WaterAnalysisResults/nodes"
        response_results = self.getResponse(url_node_results)
        
        test_dict = {}
        for node in response_results.json()["data"]:
            test_dict[node["nodeKey"]] = [node["pressure"], node["waterDemand"], 
                                 node["waterDemandCovered"], node["waterAge"]]
        
        print(test_dict)
        
        layers = QgsProject.instance().mapLayersByName('watering_demand_nodes')
        layer = layers[0]

        layer.startEditing()
        idx_pressure = layer.fields().indexOf('Pressure')
        idx_demand = layer.fields().indexOf('Demand')
        idx_demand_covered = layer.fields().indexOf('Demand C')
        idx_age = layer.fields().indexOf('Age')
        
        for feature in layer.getFeatures():
            if feature['Demand Nod'] in test_dict:
                node = test_dict[feature['Demand Nod']]
                layer.changeAttributeValue(feature.id(), idx_pressure, node[0])
                layer.changeAttributeValue(feature.id(), idx_demand, node[1])
                layer.changeAttributeValue(feature.id(), idx_demand_covered, node[2])
                layer.changeAttributeValue(feature.id(), idx_age, node[3])
                
        layer.commitChanges()