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
        self.BtGetAnalysisResults.clicked.connect(self.getAnalysisResults)
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
        return requests.get(url, params=params, headers={'Authorization': "Bearer {}".format(self.token)})
    
    def getAnalysisResults(self):
        pipes_url = "https://dev.watering.online/api/v1/WaterAnalysisResults/pipes"
        nodes_url = "https://dev.watering.online/api/v1/WaterAnalysisResults/nodes"
        pipes_keys_api = ["pipeKey","pipeCurrentStatus", "velocity", "flow", "headLoss"]
        nodes_keys_api = ["nodeKey", "pressure", "waterDemand", "waterDemandCovered", "waterAge"]
        pipes_att = ["C Status","Velocity", "Flow","HeadLoss"]
        nodes_att = ["Pressure", "Demand","Demand C", "Age"]

        self.elementsAnalysisResults(pipes_url, pipes_keys_api, pipes_att, "watering_pipes")
        self.elementsAnalysisResults(nodes_url, nodes_keys_api, nodes_att, "watering_demand_nodes")

    def elementsAnalysisResults(self, url, keys_api, keys_att, layer_name):     
        response = self.getResponse(url)
        
        element_dict = {}
        for element in response.json()["data"]:
            element_dict[element[keys_api[0]]] = [element[keys_api[1]], element[keys_api[2]], 
                                 element[keys_api[3]], element[keys_api[4]]]
            
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]

        layer.startEditing()
        idx_pressure = layer.fields().indexOf(keys_att[0])
        idx_demand = layer.fields().indexOf(keys_att[1])
        idx_demand_covered = layer.fields().indexOf(keys_att[2])
        idx_age = layer.fields().indexOf(keys_att[3])
        
        for feature in layer.getFeatures():
            if feature['ID'] in element_dict:
                element = element_dict[feature['ID']]
                layer.changeAttributeValue(feature.id(), idx_pressure, element[0])
                layer.changeAttributeValue(feature.id(), idx_demand, element[1])
                layer.changeAttributeValue(feature.id(), idx_demand_covered, element[2])
                layer.changeAttributeValue(feature.id(), idx_age, element[3])
                
        layer.commitChanges()
        
        print(layer_name, "analysis results done")
        
        self.changeColor("watering_pipes", "Velocity", 1, QColor(135,206,250), QColor(0, 0, 139))
        self.changeColor("watering_demand_nodes", "Pressure", 3, QColor(255, 0, 0), QColor(0, 0, 139))
    
    def changeColor(self, layer_name, field_name, size, start_color, end_color):
        # Set layer name and desired paremeters
        layer_name = layer_name
        #ramp_name = 'Rocket'
        value_field = field_name
        num_classes = 10
        classification_method = QgsClassificationQuantile()

        #You can use any of these classification method classes:
        #QgsClassificationQuantile()
        #QgsClassificationEqualInterval()
        #QgsClassificationJenks()
        #QgsClassificationPrettyBreaks()
        #QgsClassificationLogarithmic()
        #QgsClassificationStandardDeviation()
        
        layer = QgsProject().instance().mapLayersByName(layer_name)[0]
        
        # change format settings as necessary
        format = QgsRendererRangeLabelFormat()
        format.setFormat("%1 - %2")
        format.setPrecision(2)
        format.setTrimTrailingZeroes(True)

        start_color = start_color  # Light Blue
        end_color = end_color  # Dark Blue

        # Create the color ramp
        default_style = QgsStyle().defaultStyle()
        #color_ramp = default_style.colorRamp(ramp_name)
        color_ramp = QgsGradientColorRamp(start_color, end_color)
        renderer = QgsGraduatedSymbolRenderer()
        renderer.setClassAttribute(value_field)
        renderer.setClassificationMethod(classification_method)
        renderer.setLabelFormat(format)
        renderer.updateClasses(layer, num_classes)
        renderer.updateColorRamp(color_ramp)
        renderer.setSymbolSizes(size, size)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        