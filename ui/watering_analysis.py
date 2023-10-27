# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsExpression, QgsField, QgsExpressionContext
from PyQt5.QtCore import QTimer, QVariant
from PyQt5.QtWidgets import QDockWidget, QAction
from PyQt5.QtGui import QIcon

import os
import requests
from time import time, gmtime, strftime
from ..watering_utils import WateringUtils

from ..NetworkAnalysis.nodeNetworkAnalysisRepository import NodeNetworkAnalysisRepository
from ..NetworkAnalysis.pipeNetworkAnalysisRepository import PipeNetworkAnalysisRepository

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_analysis_dialog.ui'))


class WateringAnalysis(QDockWidget, FORM_CLASS):
    def __init__(self,iface):
        """Constructor."""
        super(WateringAnalysis, self).__init__(iface.mainWindow())
        self.setupUi(self)
        self.ScenarioFK = None
        self.listOfAnalysis = []
        self.hide_progress_bar()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getAnalysisResults(0))
        self.BtGetAnalysisResultsBackward.clicked.connect(lambda: self.getAnalysisResults(1))
        self.BtGetAnalysisResultsForward.clicked.connect(lambda: self.getAnalysisResults(2))
        self.BtGetAnalysisResultsPlayPause.clicked.connect(lambda: self.playbutton(0))
        self.analysis_box2.hide()
        self.compareCheckBox.clicked.connect(self.checkUserControlState)
        self.is_playing = False
        self.BtGetAnalysisResultsPlayPause.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/icon_play.png"))
        self.BtGetAnalysisResultsPlayPause.clicked.connect(self.switch_icon_play_pause)
        self.BtGetAnalysisResultsBackward.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/icon_backward.png"))
        self.BtGetAnalysisResultsForward.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/icon_forward.png"))

    
    def initializeRepository(self):
        self.token = os.environ.get('TOKEN')
        url_analysis = WateringUtils.getServerUrl() + "/api/v1/WaterAnalysis"
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        params = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        response_analysis = requests.get(url_analysis, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response_analysis.json()["total"]):
            self.analysis_box.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfAnalysis.append((response_analysis.json()["data"][i]["serverKeyId"],
                                         response_analysis.json()["data"][i]["simulationStartTime"]))
        for i in range(0, response_analysis.json()["total"]):
            self.analysis_box2.addItem(response_analysis.json()["data"][i]["name"])
            self.listOfAnalysis.append((response_analysis.json()["data"][i]["serverKeyId"],
                                         response_analysis.json()["data"][i]["simulationStartTime"]))
            
    def checkUserControlState(self):
        if self.compareCheckBox.isChecked():
            self.analysis_box2.show()
        else:
            self.analysis_box2.hide()
           

    def getAnalysisResults(self, behavior):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)
    
        self.show_progress_bar()
        analysisExecutionId = self.listOfAnalysis[self.analysis_box.currentIndex()][0]
        datetime = self.listOfAnalysis[self.analysis_box.currentIndex()][1]
        analysisExecutionId2 = self.listOfAnalysis[self.analysis_box2.currentIndex()][0]
        datetime2 = self.listOfAnalysis[self.analysis_box2.currentIndex()][1]
        self.set_progress(20)
            
        pipeNodeRepository = PipeNetworkAnalysisRepository(self.token, analysisExecutionId, datetime, behavior) 
        self.set_progress(50)  
        waterDemandNodeRepository = NodeNetworkAnalysisRepository(self.token, analysisExecutionId, datetime, behavior) 

        if self.compareCheckBox.isChecked():
            self.set_progress(60)  
            pipeNodeRepository2 = PipeNetworkAnalysisRepository(self.token, analysisExecutionId2, datetime2, behavior)
            self.set_progress(80)
            waterDemandNodeRepository2 = NodeNetworkAnalysisRepository(self.token, analysisExecutionId2, datetime2, behavior)

        self.set_progress(100)  
        self.timer_hide_progress_bar()


    def switch_icon_play_pause(self):
        if self.is_playing:
            icon_path = ":/plugins/QGISPlugin_WaterIng/images/icon_play.png"
        else:
            icon_path = ":/plugins/QGISPlugin_WaterIng/images/icon_stop.png"
        self.BtGetAnalysisResultsPlayPause.setIcon(QIcon(icon_path))
        self.is_playing = not self.is_playing

    def playbutton(self, behavior):
       """  # Load the 'watering_demand_node' layer
        layerDest = 'watering_demand_nodes'
        layer = QgsProject.instance().mapLayersByName(layerDest)[0]

        # Define the columns you want to subtract
        column_a = "Nodes_2023-01-16T18:47:47.742Z_pressure"  # Replace with the name of the first column
        column_b = "Nodes_2023-01-18T13:07:06.187Z_pressure"  # Replace with the name of the second column
        # Define the new field name for the result
        new_field_name = "difference1"
        # Check if the field already exists
        if layer.fields().indexFromName(new_field_name) == -1:
            # If not, add a new field to store the result
            layer.dataProvider().addAttributes([QgsField(new_field_name, QVariant.Double)])
            layer.updateFields()
        # Create an expression for the subtraction
        expression = QgsExpression(f'"{column_b}" - "{column_a}"')

        # Start editing the layer
        layer.startEditing()

        # Create a basic expression context
        context = QgsExpressionContext()

        # Iterate over each feature (row) in the layer
        for feature in layer.getFeatures():
            # Set the feature to the expression context
            context.setFeature(feature)
            
            # Evaluate the expression for the current feature
            result = expression.evaluate(context)
            
            # Update the feature with the result
            feature[new_field_name] = result
            layer.updateFeature(feature)

        # Commit the changes
        layer.commitChanges() """
        
    def set_progress(self, progress_value):
        t = time() - self.start
        hms = strftime("%H:%M:%S", gmtime(t))
        self.progressBar.setValue(progress_value)
        self.progressBar.setFormat(f"{hms} - %p%")

    def timer_hide_progress_bar(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_progress_bar)
        self.timer.start(6000)
        self.progressBar.setFormat("Loading completed")
        
    def hide_progress_bar(self):
        self.progressBar.setVisible(False)

    def show_progress_bar(self):
        self.progressBar.setVisible(True)
        self.start = time()