# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from qgis.utils import iface
from qgis.gui import QgsVertexMarker
from PyQt5.QtGui import QColor

import numpy as np
import matplotlib.pyplot as plt

import os
import requests
from ..watering_utils import WateringUtils
from ..maptools.insertSensorNodeTool import InsertSensorNodeTool

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
        self.Sensors = {}
        self.Points = []
        self.RowIndex = None
        self.SolutionId = None
        self.Url = WateringUtils.getServerUrl() + "/api/v1/OptimizationSolutions"
        self.Layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        self.canvas = iface.mapCanvas()
        self.toolInsertNode = iface.mapCanvas().mapTool()
        self.initializeRepository()
        self.BtLoadSolution.clicked.connect(self.loadSolutionSensors)
        self.BtCreateSolution.clicked.connect(self.createSolution)
        self.BtUploadSolution.clicked.connect(self.uploadSolution)
        self.BtRefreshTable.clicked.connect(self.loadSolutions)
        
    def initializeRepository(self):
        url_optimization = WateringUtils.getServerUrl() + "/api/v1/Optimization"
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        params = {'scenarioKeyId': "{}".format(self.ScenarioFK), 'showRemoved': False}
        response = requests.get(url_optimization, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})

        print(response.text)
        
        for i in range(0, response.json()["total"]):
            self.problem_box.addItem(response.json()["data"][i]["name"])
            self.Solutions.append(response.json()["data"][i]["serverKeyId"])
        
        self.loadSolutions()
        self.problem_box.currentIndexChanged.connect(self.loadSolutions)
        
        if not self.getExistingSensors():
            self.statusText.setText("-")
        else: 
            self.statusText.setText("Creating")
            self.statusText.setStyleSheet("color: yellow")
        
        self.removeInsertAction()
        self.sensorsUploadTable()
        
    def loadSolutions(self):
        index = self.problem_box.currentIndex()
        self.Sensors = {}
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
                    listOfObjectives.extend([[0] * 2])
                    
                else:
                    listOfObjectives.append([item["valueResult"] for item in data[i]["objectiveResults"]])

                matrix_table.append([data[i]["name"], 
                                     self.translateStatus(data[i]["status"]), 
                                     data[i]["solutionSource"],
                                     data[i]["serverKeyId"]] 
                                    + [item for item in listOfObjectives[0][:2]])
                
                self.Sensors.update(self.getSolutionSensors(data[i]))
                                                        
            model = TableModel(matrix_table, ["Name", "Status", "Source", "Id", "Obj1", "Obj2"])
            proxyModel = QSortFilterProxyModel()
            proxyModel.setSourceModel(model)
            
            self.tableView.setModel(proxyModel)
            self.tableView.setSortingEnabled(True)
    
        self.tableView.hideColumn(3)
        self.addParetoChart(response)
        
        self.tableView.clicked.connect(self.on_row_clicked)

    def createSolution(self):
        self.cleanMarkers()
        self.statusText.setText("Creating")
        self.statusText.setStyleSheet("color: lightyellow")
        self.toolInsertNode = InsertSensorNodeTool(self.canvas)
        self.canvas.setMapTool(self.toolInsertNode)
        self.close()
        
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
            proxyModel = QSortFilterProxyModel()
            proxyModel.setSourceModel(model)
            
            self.sensors_table.setModel(proxyModel)
            self.sensors_table.setSortingEnabled(True)
                    
    def loadSolutionSensors(self):
        if (self.RowIndex ==  None or self.SolutionId == None):
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("Select a row!"), level=1, duration=5)
        elif len(self.Sensors) == 0:
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("No solutions to load!"), level=1, duration=5)
        else:
            self.cleanMarkers()
            if self.SolutionId in self.Sensors:
                sensorDict = self.Sensors[self.SolutionId]
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
        
        variableResults = []
        for node in nodesWithSensors:
            variableResults.append(
            {
                "serverKeyId": "00000000-0000-0000-0000-000000000000",
                "fkProblemDefinition": "{}".format(problemFk),
                "fkProblemSolution": "00000000-0000-0000-0000-000000000000",
                "fkDecisionVariable": "00000000-0000-0000-0000-000000000000",
                "optimizerValue": 0,
                "comment": "string",
                "optimizerNodeKey": "{}".format(node)
            })

        post_message = {
        "serverKeyId": "",
        "name": "{}".format(name),
        "fkScenario": "{}".format(scenario_id),
        "fkProblemDefinition": "{}".format(problemFk),
        "variableResults": variableResults,
        "objectiveResults": [],
        "solutionSource": "string",
        "status": "0"}
    
        requests.post(self.Url, json=post_message,headers={'Authorization': "Bearer {}".format(self.token)})
        
        self.cleanMarkers()
        self.removeInsertAction()
        self.statusText.setText("Submitted")
        self.statusText.setStyleSheet("color: lightgreen")
        
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
        solution_id = data["serverKeyId"]
        if data["variableResults"]:
            for sensor in data["variableResults"]:
                    if sensor["optimizerNodeKey"]:
                        if solution_id not in sensorDict:
                            sensorDict[solution_id] = {}
                        sensorDict[solution_id][sensor["optimizerNodeKey"]] = 1
        return sensorDict
        
    def on_row_clicked(self, index):
        if index.isValid():
            row = index.row()
            self.tableView.selectRow(row)
            id = self.tableView.model().data(self.tableView.model().index(row, 3))
            self.SolutionId = id
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
    
    def removeInsertAction(self):
        self.canvas.unsetMapTool(self.toolInsertNode)
        self.toolInsertNode = None
        self.canvas.refresh()
    
    def addParetoChart(self, response):
        self.x_box.clear()
        self.y_box.clear()
        
        for i in range(0, 2):
            obj = "Objective " + str(i + 1)
            self.x_box.addItem(obj), self.y_box.addItem(obj)
        
        plt.close("all") #close all existing charts
        self.BtLoadPareto.clicked.connect(lambda: self.loadParetoChart(response))
        
    def loadParetoChart(self, response):
        data = response.json()["data"]   
        points = []
        labels = []
        for i in range(0, response.json()["total"]):
            if data[i]["objectiveResults"]:
                points.append((data[i]["objectiveResults"][self.x_box.currentIndex()]["valueResult"],
                            (data[i]["objectiveResults"][self.y_box.currentIndex()]["valueResult"])))
                labels.append(data[i]["name"])

        fig, ax = plt.subplots()

        # Extract x and y values from points
        x_values, y_values = zip(*points)
        ax.scatter(x_values, y_values, color="b")
        ax.set_title("Pareto Chart")
        ax.set_xlabel(self.x_box.currentText())
        ax.set_ylabel(self.y_box.currentText())

        #index_sol = self.solutions_box.currentIndex()
        #x_ = x_values[index_sol]
        #y_ = y_values[index_sol]

        # Plot the point again in a different color
        #ax.scatter(x_, y_, color='red')

        if self.label_checkBox.isChecked():
            for i, name in enumerate(labels):
                offset = 10
                ax.annotate(name, (x_values[i], y_values[i]), ha="left", va="top",
                            xytext=(x_values[i] + offset, y_values[i] + offset))

        ax.grid(True, color="lightgrey")
        fig.tight_layout()
        
        plt.show()
        
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