# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QAbstractTableModel
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from qgis.utils import iface
from qgis.gui import QgsVertexMarker, QgsMapCanvas
from qgis.core import QgsProject
from PyQt5.QtGui import QColor

import os
import requests
from ..watering_utils import WateringUtils
import json
import numpy as np

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_optimization_dialog.ui'))


class WaterOptimization(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(WaterOptimization, self).__init__(parent)
        self.setupUi(self)
        self.token = os.environ.get('TOKEN')
        self.ScenarioFK = None
        self.Solutions = []
        self.Sensors = []
        self.RowIndex = None
        self.Url = "https://dev.watering.online/api/v1/OptimizationSolutions"
        self.Layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        self.canvas = iface.mapCanvas()
        self.initializeRepository()
        self.BtLoadSolution.clicked.connect(self.loadSolutionSensors)
        self.BtUploadSolution.clicked.connect(self.uploadSolution)
        
    def initializeRepository(self):
        url_optimization = "https://dev.watering.online/api/v1/Optimization"
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        params = {'scenarioKeyId': "{}".format(self.ScenarioFK), 'showRemoved': False}
        response = requests.get(url_optimization, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        for i in range(0, response.json()["total"]):
            self.problem_box.addItem(response.json()["data"][i]["name"])
            self.Solutions.append(response.json()["data"][i]["serverKeyId"])
        
        self.loadSolutions(self.problem_box.currentIndex())
        self.problem_box.currentIndexChanged.connect(self.loadSolutions)
        self.sensorsUploadTable()
        
    def loadSolutions(self, index):

        problemFK = self.Solutions[index]
        params = {'problemKeyId': "{}".format(problemFK)}
        response = requests.get(self.Url, params=params,
                   headers={'Authorization': "Bearer {}".format(self.token)})
        
        data = response.json()["data"]
        total = response.json()["total"]

        if total > 0:
            matrix_table = []
            for i in range(0, total):
                
                listOfObjectives = []
                if not data[i]["objectiveResults"]:
                    listOfObjectives.extend([[np.nan] * 4])
                else:
                    listOfObjectives.append([item["valueResult"] for item in data[i]["objectiveResults"]])

                matrix_table.append([data[i]["name"], 
                                     self.translateStatus(data[i]["status"]), 
                                     data[i]["solutionSource"]] 
                                    + [item for item in listOfObjectives[0][:4]])
                
                self.Sensors.append(self.getSolutionSensors(data[i]))
                                                        
            model = TableModel(matrix_table, ["Name", "Status", "Source", "Obj1", "Obj2", "Obj3", "Obj4"])
            self.tableView.setModel(model)
            
        self.tableView.clicked.connect(self.on_row_clicked)

    def sensorsUploadTable(self):
        existingSensors = self.getExistingSensors()
        if existingSensors:
            matrix_table = []
            for node in self.Layer.getFeatures():
                if node.geometry().asPoint() in existingSensors:
                    matrix_table.append([node["Name"],
                                        node["ID"],
                                        node["Descriptio"]])
                        
            model = TableModel(matrix_table, ["Name", "ID", "Description"])
            self.sensors_table.setModel(model)
            
                    
    def loadSolutionSensors(self):
        if self.RowIndex ==  None:
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("Select a row!"), level=1, duration=5)
        elif len(self.Sensors) == 0:
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("No solutions to load!"), level=1, duration=5)
        else:
            self.cleanMarkers()
            sensorDict = self.Sensors[self.RowIndex]
            for feature in self.Layer.getFeatures():
                if feature['ID'] in sensorDict:
                    self.insertSensor(feature.geometry().asPoint())
            self.canvas.refresh()
    
    def uploadSolution(self):
        nodesWithSensors = []
        existingSensors = self.getExistingSensors()
        for feature in self.Layer.getFeatures():
            if feature.geometry().asPoint() in existingSensors:
                nodesWithSensors.append(feature["ID"])
                
        if not nodesWithSensors: iface.messageBar().pushMessage(self.tr("Error"), 
                                 self.tr("No sensors to send!"), level=1, duration=5); return 
        
        name = self.newSolutionInputName.text() or "Solution Test"
        scenario_id = WateringUtils.getScenarioId()
        problemFk = self.Solutions[self.problem_box.currentIndex()]

        post_message = {
        "serverKeyId": "",
        "name": "{}".format(name),
        "fkScenario": "{}".format(scenario_id),
        "fkProblemDefinition": "{}".format(problemFk),
        "variableResults": [],
        "objectiveResults": [],
        "solutionSource": "string",
        "status": "0"}
    
        requests.post(self.Url, json=post_message,headers={'Authorization': "Bearer {}".format(self.token)})
        
    def insertSensor(self, coord):
        m = QgsVertexMarker(self.canvas)
        m.setCenter(coord)
        m.setColor(QColor(0,255,0))
        m.setIconSize(20)
        m.setIconType(QgsVertexMarker.ICON_CIRCLE)
        m.setPenWidth(4)
        self.canvas.scene().addItem(m)
                
    def translateStatus(self, status):
        conditions = {0:"Created", 
                      1:"Evaluating",
                      2:"Evaluated",
                      3:"ErrorsOnEvaluation"}
        
        return conditions.get(status)

    def getSolutionSensors(self, data):
        sensorDict = {}
        for sensor in data["variableResults"]:
            sensorDict[sensor["optimizerNodeKey"]] = sensor["comment"]
        return sensorDict
        
    def on_row_clicked(self, index):
        if index.isValid():
            row = index.row()
            self.tableView.selectRow(row)
            self.RowIndex = row

    def getExistingSensors(self):
        existingSensors = {}
        vertex_items = [i for i in self.canvas.scene().items() if isinstance(i, QgsVertexMarker)]
        for vertex in vertex_items:
            existingSensors[vertex.center()] = 1
        return existingSensors
            
    def cleanMarkers(self):
        vertex_items = [i for i in self.canvas.scene().items() if isinstance(i, QgsVertexMarker)]
        for vertex in vertex_items:
            self.canvas.scene().removeItem(vertex)
        self.canvas.refresh()  
        
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, headers):
        super(TableModel, self).__init__()
        self._data = data
        self.headers = headers
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)
    
    
    