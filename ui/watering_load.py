# -*- coding: utf-8 -*-

import os
import requests

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeLayer
from qgis.utils import iface

from ..watering_utils import WateringUtils
from ..repositories.reservoirNodeRepository import ReservoirNodeRepository
from ..repositories.tankNodeRepository import TankNodeRepository
from ..repositories.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositories.pipeNodeRepository import PipeNodeRepository


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_load_dialog.ui'))

class WateringLoad(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WateringLoad, self).__init__(parent)
        self.setupUi(self)
        self.token = os.environ.get('TOKEN')
        self.listOfProjects = []
        self.listOfScenarios = []
        self.loadProjects()
        self.newProjectBtn.clicked.connect(self.checkExistingProject)
        
    def loadProjects(self):
        url_projects = "https://dev.watering.online/api/v1/ProjectWaterNetworks"
        response_projects = requests.get(url_projects,
                                headers={'Authorization': "Bearer {}".format(self.token)})
            
        for i in range(0, response_projects.json()["total"]):
            self.projects_box.addItem(response_projects.json()["data"][i]["name"])
            self.listOfProjects.append((response_projects.json()["data"][i]["name"],
                                response_projects.json()["data"][i]["serverKeyId"]))
                
        self.loadScenarios(self.projects_box.currentIndex())
        self.projects_box.currentIndexChanged.connect(self.loadScenarios)
        
    def loadScenarios(self, value):
        #Resetting scenarios box in case of changing the selected project.
        self.scenarios_box.clear()
        self.listOfScenarios = []
            
        ProjectFK = self.listOfProjects[value][1]
        showRemoved = False
        params = {'ProjectFK': "{}".format(ProjectFK), 'showRemoved': "{}".format(showRemoved)}
        url = "https://dev.watering.online/api/v1/ScenarioWaterNetwork"
        response_scenarios = requests.get(url, params=params,
                                headers={'Authorization': "Bearer {}".format(self.token)})
            
        for i in range(0, response_scenarios.json()["total"]):
            self.scenarios_box.addItem(response_scenarios.json()["data"][i]["name"])
            self.listOfScenarios.append((response_scenarios.json()["data"][i]["name"],
                                         response_scenarios.json()["data"][i]["serverKeyId"]))
    
    def checkExistingProject(self):
        scenario_id, type_conversion_ok = QgsProject.instance().readEntry("watering","scenario_id","default text")
    
        if scenario_id != "default text":
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("You already have a project opened!"), level=1, duration=5)
        elif self.newShpDirectory.filePath() == "":
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("Select a folder!"), level=1, duration=5)
        else:
            self.createNewProject()
            
    def createNewProject(self):
        #project name
        project = QgsProject.instance()
        project_name = self.newProjectNameInput.text()
        project.setFileName("My WaterIng Project" if project_name == "" else project_name)
        project.write()
        #load layers
        self.CreateLayers()
    
    def CreateLayers(self):
        project_path = self.newShpDirectory.filePath()

        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.addGroup("WaterIng Network Layout")

        waterDemandNodeRepository = WateringDemandNodeRepository(self.token, project_path, self.listOfScenarios[self.scenarios_box.currentIndex()][1])                
        tankNodeRepository = TankNodeRepository(self.token, project_path, self.listOfScenarios[self.scenarios_box.currentIndex()][1])    
        reservoirNodeRepository = ReservoirNodeRepository(self.token, project_path, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        pipeNodeRepository = PipeNodeRepository(self.token, project_path, self.listOfScenarios[self.scenarios_box.currentIndex()][1])    
        self.loadMap()

        self.writeWateringMetadata()
        self.setStatusBar()
        
    def writeWateringMetadata(self):
        QgsProject.instance().writeEntry("watering", "project_name", self.listOfProjects[self.projects_box.currentIndex()][0])
        QgsProject.instance().writeEntry("watering", "project_id", self.listOfProjects[self.projects_box.currentIndex()][1])
        QgsProject.instance().writeEntry("watering", "scenario_name", self.listOfScenarios[self.scenarios_box.currentIndex()][0])
        QgsProject.instance().writeEntry("watering", "scenario_id", self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        
    def loadMap(self):
        tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms,'OSM', 'wms')
        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        root.insertChildNode(5, QgsLayerTreeLayer(layer))
    
    def setStatusBar(self):
        project = QgsProject.instance()
        project_name, type_conversion_ok = project.readEntry("watering",
                                            "project_name",
                                            "default text")
        
        scenario_name, type_conversion_ok = project.readEntry("watering",
                                            "scenario_name",
                                            "default text")
        
        message = "Project: " + project_name + " | Scenario: " + scenario_name
        
        iface.mainWindow().statusBar().showMessage(message)        
        self.done(True)  #self.close()  instead of just closing we call done(true) to return 1 as result of this dialog modal execution
        
    