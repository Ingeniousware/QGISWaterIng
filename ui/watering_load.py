# -*- coding: utf-8 -*-

import os
import requests
import pickle

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeLayer
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox, QFileDialog

from ..unitofwork.scenarioUnitOfWork import scenarioUnitOfWork

from ..watering_utils import WateringUtils
from ..repositories.reservoirNodeRepository import ReservoirNodeRepository
from ..repositories.tankNodeRepository import TankNodeRepository
from ..repositories.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositories.pipeNodeRepository import PipeNodeRepository
from ..repositories.waterMeterNodeRepository import WaterMeterNodeRepository
from ..repositories.valveNodeRepository import ValveNodeRepository
from ..repositories.pumpNodeRepository import PumpNodeRepository

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
        self.myScenarioUnitOfWork = None
        self.projectPathQgsProject = None
        self.project_path = None
        self.scenario_folder = None
        self.loadProjects()
        self.newProjectBtn.clicked.connect(self.checkExistingProject)
    
    def loadProjects(self):
        url_projects = WateringUtils.getServerUrl() + "/api/v1/ProjectWaterNetworks"
        
        #response_projects = requests.get(url_projects,
        #                        headers={'Authorization': "Bearer {}".format(self.token)})

        response_projects = WateringUtils.getResponse(url_projects, params=None)
        
        if not response_projects:
            return
        
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
        url = WateringUtils.getServerUrl() + "/api/v1/ScenarioWaterNetwork"
        #response_scenarios = requests.get(url, params=params,
        #                        headers={'Authorization': "Bearer {}".format(self.token)})
        
        response_scenarios = WateringUtils.getResponse(url, params)
        
        if not response_scenarios:
            return
        
        for i in range(0, response_scenarios.json()["total"]):
            self.scenarios_box.addItem(response_scenarios.json()["data"][i]["name"])
            self.listOfScenarios.append((response_scenarios.json()["data"][i]["name"],
                                         response_scenarios.json()["data"][i]["serverKeyId"]))
    
    def checkExistingProject(self):
        if self.newShpDirectory.filePath() == "":
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("Select a folder!"), level=1, duration=5)
        elif not WateringUtils.isScenarioNotOpened() or WateringUtils.isProjectOpened():
            self.saveCurrentProject()
        else:
            self.createNewProject()

    def saveCurrentProject(self):
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(None, 
                                            "Save Project", 
                                            "The current project has unsaved changes. Do you want to save it before creating a new project?", 
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                project_path = project.readEntry("watering","project_path","default text")[0]
                if project_path != "default text":
                    project.write(project_path)
                else:
                    iface.actionSaveProjectAs().trigger()
                    
                if project.write():
                    print(f"Project saved at {project.fileName()}")
                    iface.messageBar().pushMessage(self.tr("Error"), self.tr(f"Project saved at {project.fileName()}"), level=1, duration=5)
                else:
                    print("Failed to save the project.")
                    iface.messageBar().pushMessage(self.tr("Error"), self.tr("Failed to save the project."), level=1, duration=5)

            elif response == QMessageBox.Cancel:
                return

        project.clear()
        self.createNewProject()
            
    def createNewProject(self):
        #project name
        project = QgsProject.instance()
        name = self.newProjectNameInput.text()
        project_name = "My WaterIng Project" if not name else name
        self.project_path = self.newShpDirectory.filePath()
        project.setFileName(project_name)
        self.projectPathQgsProject = self.project_path + "/" + project_name + ".qgz"
        project.write(self.projectPathQgsProject)
        QgsProject.instance().writeEntry("watering", "project_path", self.projectPathQgsProject)
        
        #create scenario folder
        self.createScenarioFolder()
        #load layers
        self.CreateLayers()
        

    def createScenarioFolder(self):
        self.writeWateringMetadata(self.project_path)
        scenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        print("Aqui: " + scenarioFK)
        #Create scenario folder
        self.scenario_folder = self.project_path + "/" + scenarioFK
        os.makedirs(self.scenario_folder, exist_ok=True)
       
    
    def CreateLayers(self):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.addGroup("WaterIng Network Layout")

        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        #print(myScenarioUnitOfWork)
        #pickle
        #serialized_obj = pickle.dumps(myScenarioUnitOfWork)
        #os.environ['SCENARIO'] = serialized_obj.hex()
        
        self.loadMap()

        
        self.setStatusBar()
        self.close()
        
    def writeWateringMetadata(self, projectPath):
        QgsProject.instance().writeEntry("watering", "project_name", self.listOfProjects[self.projects_box.currentIndex()][0])
        QgsProject.instance().writeEntry("watering", "project_id", self.listOfProjects[self.projects_box.currentIndex()][1])
        QgsProject.instance().writeEntry("watering", "scenario_name", self.listOfScenarios[self.scenarios_box.currentIndex()][0])
        QgsProject.instance().writeEntry("watering", "scenario_id", self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        QgsProject.instance().writeEntry("watering", "project_path", projectPath)
        
        
    def loadMap(self):
        tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms,'OSM', 'wms')
        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        root.insertChildNode(5, QgsLayerTreeLayer(layer))
    
    def setStatusBar(self):
        project = QgsProject.instance()
        project_name = project.readEntry("watering","project_name","default text")[0]
        scenario_name = project.readEntry("watering", "scenario_name","default text")[0]
        
        message = "Project: " + project_name + " | Scenario: " + scenario_name
        iface.mainWindow().statusBar().showMessage(message)        
        self.done(True)  #self.close()  instead of just closing we call done(true) to return 1 as result of this dialog modal execution
        
    