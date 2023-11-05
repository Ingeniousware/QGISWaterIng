# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsExpression, QgsField, QgsExpressionContext
from PyQt5.QtCore import QTimer, QVariant, QDateTime
from PyQt5.QtWidgets import QDockWidget, QMessageBox
from PyQt5.QtGui import QIcon

import os
import requests
import uuid
from datetime import datetime
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
        self.listOfSimulators = []
        self.hide_progress_bar()
        self.BtGetAnalysisResultsCurrent.clicked.connect(lambda: self.getAnalysisResults(0))
        self.BtGetAnalysisResultsBackward.clicked.connect(lambda: self.getAnalysisResults(1))
        self.BtGetAnalysisResultsForward.clicked.connect(lambda: self.getAnalysisResults(2))
        self.BtGetAnalysisResultsPlayPause.clicked.connect(lambda: self.playbutton(0))
        self.analysis_box2.hide()
        self.compareCheckBox.clicked.connect(self.checkUserControlState)
        self.is_playing = False
        self.new_field_name = None
        self.BtGetAnalysisResultsPlayPause.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/start.png"))
        self.BtGetAnalysisResultsPlayPause.clicked.connect(self.switch_icon_play_pause)
        self.BtGetAnalysisResultsBackward.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/Backward.png"))
        self.BtGetAnalysisResultsForward.setIcon(QIcon(":/plugins/QGISPlugin_WaterIng/images/Forward.png"))
        self.BoxSelectType.addItem("What If")
        self.BoxSelectType.addItem("Replay")
        self.BoxSelectType.addItem("Look Ahead")
        self.BoxSelectType.addItem("Distribution Spectrum")
        self.BoxSelectType.addItem("Mark Upstream Line to Source")
        self.BoxSelectType.addItem("Mark Dowstream Line from Source")
        self.BoxSelectType.addItem("Leak Sensitivity")
        self.BoxSelectType.addItem("Leak Impact")
        self.BoxSelectType.addItem("Transient Analysis")
        self.BoxSelectType.addItem("Sectorization")
        self.BoxSelectType.addItem("Model Review")
        self.BoxSelectType.addItem("Connectivity")
        self.BoxSelectType.addItem("Graph Decomposition")
        self.BoxSelectType.addItem("Sector Identification")
        
        self.BTExecute.clicked.connect(self.requestAnalysisExecution)
        self.startDateTime.setDateTime(QDateTime.currentDateTime())
        print("Project path (at init WateringAnalysis):  ", WateringUtils.getProjectPath())

    
    def initializeRepository(self):
        # Clear combo boxes and lists
        self.analysis_box.clear()
        self.analysis_box2.clear()
        self.BoxSimulator.clear()
        self.listOfAnalysis = []
        self.listOfSimulators = []

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
            
        #For simulator combo box in executions    
        url_simulators = url_analysis + "/simulators"
        response_simulators = requests.get(url_simulators, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})
        for i in range(0, response_simulators.json()["total"]):
            self.BoxSimulator.addItem(response_simulators.json()["data"][i]["name"])
            self.listOfSimulators.append((response_simulators.json()["data"][i]["name"], 
                                          response_simulators.json()["data"][i]["serverKeyId"]))
        
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
            self.createNewColumns(pipeNodeRepository2.LayerName, "velocity")
            self.fieldCalculator(pipeNodeRepository, pipeNodeRepository2)
            
            self.set_progress(80)
            waterDemandNodeRepository2 = NodeNetworkAnalysisRepository(self.token, analysisExecutionId2, datetime2, behavior)
            self.createNewColumns(waterDemandNodeRepository2.LayerName, "pressure")
            self.set_progress(90)
            self.fieldCalculator(waterDemandNodeRepository, waterDemandNodeRepository2)
            
        self.set_progress(100)  
        self.timer_hide_progress_bar()


    def switch_icon_play_pause(self):
        if self.is_playing:
            icon_path = ":/plugins/QGISPlugin_WaterIng/images/start.png"
        else:
            icon_path = ":/plugins/QGISPlugin_WaterIng/images/stop.png"
        self.BtGetAnalysisResultsPlayPause.setIcon(QIcon(icon_path))
        self.is_playing = not self.is_playing

    def playbutton(self, behavior):
        print("pause...still need code")

    def createNewColumns(self, layerDest, name):
        layer = QgsProject.instance().mapLayersByName(layerDest)[0]
        if not layer:
            raise Exception(f"Layer '{layerDest}' not found in the project.")
        self.new_field_name = "d_" + name
        field_index = layer.fields().indexFromName(self.new_field_name)
        if field_index != -1:                                   
            layer.dataProvider().deleteAttributes([field_index])
            layer.updateFields()
            layer.commitChanges()
        layer.dataProvider().addAttributes([QgsField(self.new_field_name, QVariant.Double)])
        layer.updateFields()                
        layer.commitChanges()
  

    def fieldCalculator(self, repository, repository2):
        layerDest = repository.LayerName
        column_a = repository.Field
        column_b = repository2.Field

        layer = QgsProject.instance().mapLayersByName(layerDest)[0]
        if not layer:
            raise Exception(f"Layer '{layerDest}' not found in the project.")

        expression = QgsExpression(f'"{column_a}" - "{column_b}"')
        if expression.hasParserError():
            raise Exception(expression.parserErrorString())

        layer.startEditing()
        context = QgsExpressionContext()
        field_index = layer.fields().indexFromName(self.new_field_name)
        if field_index == -1:
            raise Exception(f"Field '{self.new_field_name}' not found in the layer. Ensure it's added correctly.")
        for feature in layer.getFeatures():
            context.setFeature(feature)
            result = expression.evaluate(context)
            feature.setAttribute(field_index, result)
            layer.updateFeature(feature)
        layer.commitChanges()
    
        repository.changeColor(self.new_field_name)

    def requestAnalysisExecution(self):
        # Fetch values from ComboBox and other widgets
        selectedAnalysisTypeIndex = self.BoxSelectType.currentIndex()

        if (selectedAnalysisTypeIndex < 11):
                selectedSimulator = self.BoxSimulator.currentText()
                simulatorIndex = self.BoxSimulator.currentIndex()
                simulatorFK = self.listOfSimulators[simulatorIndex][1]        
                duration = int(self.durationSpinBox.value())
                timeStep = int(self.timeStepSpinBox.value())
                
                # Format date and time from QDateTimeEdit widget
                dateTime = self.startDateTime.dateTime()
                formatted_date = dateTime.toString("yyyy-MM-ddTHH:mm:ss.zzzZ")
                
                # Get current date and time in different formats
                now_utc = datetime.utcnow()
                formatted_now_utc = now_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                dateForName = datetime.now().strftime('%d.%m.%Y, %H:%M:%S')
                name = f"Execution - {dateForName}"
                
                # Generate a new GUID
                new_guid = str(uuid.uuid4())
                
                # Post the collected data to the API
                self.postToAnalysisAPI(name, formatted_date, duration, formatted_now_utc, new_guid, selectedSimulator, simulatorFK, timeStep)
        elif (selectedAnalysisTypeIndex == 12):            
                self.show_message("Water Analysis", "Connectivity and topological analysis are currently being connected to our plugin but not ready to use", QMessageBox.Warning)
        else:             
                self.show_message("Water Analysis", "This type of analysis hasnt been implemented", QMessageBox.Warning)



    def show_message(self, title, text, icon):
            """Display a QMessageBox with given attributes."""
            message_box = QMessageBox()
            message_box.setIcon(icon)
            message_box.setWindowTitle(title)
            message_box.setText(text)
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()


    def postToAnalysisAPI(self, name, startDate, duration, formatted_now, new_guid, selectedSimulator, simulatorFK, timeStep):
                 
        data_json = {
            "serverKeyId": new_guid,
            "scenarioKeyId": self.ScenarioFK,
            "name": name,
            "description": "example",
            "clientRequestDateTime": formatted_now,
            "simulationStartTime": startDate,
            "duration": duration,
            "timeStep": timeStep,
            "simulatorFK": simulatorFK,
            "simulatorName": selectedSimulator,
            "executionState": 0
        }
        
        url = f"{WateringUtils.getServerUrl()}/api/v1/WaterAnalysis"
        params = {'scenarioFK': self.ScenarioFK}
        headers = {'Authorization': f"Bearer {self.token}"}
        
        try:
            response = requests.post(url, params=params, headers=headers, json=data_json)
            if response.status_code == 200:
                print("Anañysis uploaded successfully!")
                self.show_message("Water Analysis", "Analysis Executed Correctly", QMessageBox.Information)
            else:
                self.show_message("Water Analysis", "Analysis Not Executed", QMessageBox.Warning)
                
        except requests.RequestException as e:  # Catch specific exception related to requests.
            print(f"Error: {e}")
            self.show_message("Water Analysis", "Analysis Not Executed", QMessageBox.Warning)
        
        
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