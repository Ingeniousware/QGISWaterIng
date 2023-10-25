# -*- coding: utf-8 -*-

import os
import json

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeLayer, Qgis, QgsRectangle
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QDockWidget, QLabel
from PyQt5.QtCore import Qt

from ..unitofwork.scenarioUnitOfWork import scenarioUnitOfWork
from ..watering_utils import WateringUtils

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
        self.OfflineScenarios = None
        self.myScenarioUnitOfWork = None
        self.projectPathQgsProject = None
        self.project_path = None
        self.scenario_folder = None
        self.ProjectFK = None
        self.ProjectName = None
        self.ScenarioFK = None
        self.ScenarioName = None
        self.ProjectName = None
        self.WateringFolder = WateringUtils.get_app_data_path() + "/QGISWatering/"
        self.loadProjects()
        self.newProjectBtn.clicked.connect(self.checkExistingProject)
    
    def loadProjects(self):
        url_projects = WateringUtils.getServerUrl() + "/api/v1/ProjectWaterNetworks"
        
        response_projects = WateringUtils.getResponse(url_projects, params=None)
        
        if not response_projects:
            return
        
        for i in range(0, response_projects.json()["total"]):
            self.projects_box.addItem(response_projects.json()["data"][i]["name"])
            self.listOfProjects.append((response_projects.json()["data"][i]["name"],
                                response_projects.json()["data"][i]["serverKeyId"]))
        
        self.loadScenarios(self.projects_box.currentIndex())
        self.projects_box.currentIndexChanged.connect(self.loadScenarios)
        
        #initializing procedures
        self.newShpDirectory.setFilePath(self.WateringFolder)
        #{}
        self.getOfflineScenarios()
        print(self.OfflineScenarios)
        self.setComboBoxCurrentProject()
        
    def loadScenarios(self, value):
        #Resetting scenarios box in case of changing the selected project.
        self.scenarios_box.clear()
        self.listOfScenarios = []
        self.newProjectNameInput.setPlaceholderText(self.listOfProjects[value][0])
        
        self.ProjectFK = self.listOfProjects[value][1]
        self.ProjectName = self.listOfProjects[value][0]
        showRemoved = False
        params = {'ProjectFK': "{}".format(self.ProjectFK), 'showRemoved': "{}".format(showRemoved)}
        url = WateringUtils.getServerUrl() + "/api/v1/ScenarioWaterNetwork"
        
        response_scenarios = WateringUtils.getResponse(url, params)
        
        if not response_scenarios:
            return
        
        for i in range(0, response_scenarios.json()["total"]):
            self.scenarios_box.addItem(response_scenarios.json()["data"][i]["name"])
            self.listOfScenarios.append((response_scenarios.json()["data"][i]["name"],
                                         response_scenarios.json()["data"][i]["serverKeyId"]))
        
        #length scenarioFK is 36
        self.ScenarioName = self.listOfScenarios[self.scenarios_box.currentIndex()][0]
        self.ScenarioFK = self.listOfScenarios[self.scenarios_box.currentIndex()][1]
        
    def checkExistingProject(self):
        #if there is a project opened
        if not WateringUtils.isScenarioNotOpened() or WateringUtils.isProjectOpened():
            if self.ProjectFK != WateringUtils.getProjectId():
                self.saveCurrentProject()
            else:
                #todo clear only watering layers
                QgsProject.instance().clear()
                self.createNewProject()
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
                #self.project_path = project.readEntry("watering","project_path","default text")[0]
                if WateringUtils.getProjectMetadata("project_path") != "default text":
                    if project.write():
                        iface.messageBar().pushMessage(self.tr(f"Project saved at {project.fileName()}"), level=Qgis.Success, duration=5)
                    else:
                        iface.messageBar().pushMessage(self.tr("Error"), self.tr("Failed to save the project."), level=1, duration=5)
                else:
                    iface.actionSaveProjectAs().trigger()
       
            elif response == QMessageBox.Cancel:
                return


        project.clear()
        self.createNewProject()
        
    def setWateringFolderAppData(self, path):
        #Creates directory QGISWatering inside Appdata
        folder = path + self.ProjectFK
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        self.project_path = folder
    
    def getOfflineScenarios(self):
        self.OfflineScenarios = {folder: self.getSubFolders(os.path.join(self.WateringFolder + folder)) for folder in self.getSubFolders(self.WateringFolder)}
        #self.OfflineScenarios[self.ProjectFK]["Name"] = self.ProjectName
        
        #self.OfflineScenarios = {folder: {"Name": self.ProjectName, **self.getSubFolders(os.path.join(self.WateringFolder + folder))} for folder in os.listdir(self.WateringFolder) if os.path.isdir(os.path.join(self.WateringFolder, folder))}
        #print(self.OfflineScenarios)
        
    def getSubFolders(self, path):
        #return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return {d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))}
    
    def writeOfflineData(self):
        # Ensure the directory exists
        filepath = self.WateringFolder + "metadata.json"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as file:
            json.dump(self.OfflineScenarios, file)
            
    def startProject(self):
        if (self.OfflineScenarios and 
            self.OfflineScenarios.get(self.ProjectFK) and 
            self.ScenarioFK in self.OfflineScenarios[self.ProjectFK]):
            
            self.openProjectFolder()
        else:
            
            self.createNewProject()
            
    def openProjectFolder():
        ...
            
    def createNewProject(self):
        #project name
        project = QgsProject.instance()
        name = self.newProjectNameInput.text()
        project_name = self.newProjectNameInput.placeholderText() if not name else name
        
        #creates the project folder within the chosen folder (Watering folder in appdata by default)
        self.setWateringFolderAppData(self.newShpDirectory.filePath())
        project.setFileName(project_name)
        self.projectPathQgsProject = self.project_path + "/" + project_name + ".qgz"
        project.write(self.projectPathQgsProject)
            
        WateringUtils.setProjectMetadata("local_project_name", project_name)
        WateringUtils.setProjectMetadata("project_path", self.project_path)

        #create scenario folder
        self.createScenarioFolder()
        
        #load layers
        self.CreateLayers()

    def createScenarioFolder(self):
        self.writeWateringMetadata()

        scenarioFK = WateringUtils.getProjectMetadata("scenario_id")
        print("Aqui: " + scenarioFK)
        #Create scenario folder
        self.scenario_folder = self.project_path + "/" + scenarioFK
        os.makedirs(self.scenario_folder, exist_ok=True)
       
    
    def CreateLayers(self):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.addGroup("WaterIng Network Layout")

        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        
        self.loadMap()
        self.zoomToProject()
        self.setStatusBar()
        self.close()
        
    def writeWateringMetadata(self):
        WateringUtils.setProjectMetadata("server_project_name", self.listOfProjects[self.projects_box.currentIndex()][0])
        WateringUtils.setProjectMetadata("project_id", self.listOfProjects[self.projects_box.currentIndex()][1])
        WateringUtils.setProjectMetadata("scenario_name", self.listOfScenarios[self.scenarios_box.currentIndex()][0])
        WateringUtils.setProjectMetadata("scenario_id", self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        
    def loadMap(self):
        tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms,'OSM', 'wms')
        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        root.insertChildNode(5, QgsLayerTreeLayer(layer))
    
    def setStatusBar(self):
        project_name = WateringUtils.getProjectMetadata("project_name")
        scenario_name = WateringUtils.getProjectMetadata("scenario_name")
        
        message = "Project: " + project_name + " | Scenario: " + scenario_name
        
        iface.mainWindow().statusBar().showMessage(message)   
             
        self.done(True)  #self.close()  instead of just closing we call done(true) to return 1 as result of this dialog modal execution
    
    def zoomToProject(self):
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("WaterIng Network Layout")
        if not group:
            iface.messageBar().pushMessage(self.tr("Error"), self.tr("Failed to zoom to WaterIng layers."), level=1, duration=5)
            return

        combined_extent = QgsRectangle()

        for layer in group.findLayers():
            if layer.layer():
                combined_extent.combineExtentWith(layer.layer().extent())

        if not combined_extent.isEmpty():
            iface.mapCanvas().setExtent(combined_extent)
            iface.mapCanvas().refresh()
    
    def setComboBoxCurrentProject(self):
        project_name = WateringUtils.getProjectMetadata("server_project_name")
        
        if project_name != "default text":
            index_project = -1
            
            for i in range(self.projects_box.count()):
                if self.projects_box.itemText(i) == project_name:
                    index_project = i
                    break
                
            if index_project != -1:
                self.projects_box.setCurrentIndex(index_project)
            else:
                print(f"Project: {project_name} not found!")

        self.setComboBoxCurrentScenario()
                
    def setComboBoxCurrentScenario(self):
        scenario_name = WateringUtils.getProjectMetadata("scenario_name")
        
        if scenario_name != "default text":
            index_scenario = -1
            
            for i in range(self.scenarios_box.count()):
                if self.scenarios_box.itemText(i) == scenario_name:
                    index_scenario = i
                    break
                    
            if index_scenario != -1:
                self.scenarios_box.setCurrentIndex(index_scenario)
            else:
                print(f"Scenario: {scenario_name} not found!")
        