# -*- coding: utf-8 -*-

import os
import json
import requests
import glob

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeLayer, Qgis, QgsRectangle, QgsVectorLayer, QgsLayerTreeGroup
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
        self.OfflineProjects = None
        self.responseProjects = None
        self.WateringFolder = WateringUtils.get_app_data_path() + "/QGISWatering/"
        self.ProjectsJSON= self.WateringFolder + 'projects.json'
        self.ProjectsJSON_data = None
        self.Offline = False
        self.initializeRepository()
        self.newProjectBtn.clicked.connect(self.checkExistingProject)
    
    def initializeRepository(self):
        if os.environ.get('TOKEN') == None:
            iface.messageBar().pushMessage(("Running Offline."), level=1, duration=5)
            self.offlineProcedures()
        else:
            url_projects = WateringUtils.getServerUrl() + "/api/v1/ProjectWaterNetworks"
            try:
                self.responseProjects = requests.get(url_projects, params=None,
                                        headers={'Authorization': "Bearer {}".format(os.environ.get('TOKEN'))})
                if self.responseProjects.status_code == 200: 
                    self.loadProjects()
                    
            except requests.ConnectionError:
                iface.messageBar().pushMessage(("Error"), ("No connection. Running offline."), level=1, duration=5)
                self.offlineProcedures()
            except requests.Timeout:
                iface.messageBar().pushMessage(("Error"), ("Request timed out. Running offline."), level=1, duration=5)
                self.offlineProcedures()
            except:
                iface.messageBar().pushMessage(("Error"), ("Unable to connect to WaterIng. Running offline."), level=1, duration=5)
                self.offlineProcedures()
                
        #initializing procedures
        self.setComboBoxCurrentProject()
        self.newShpDirectory.setFilePath(self.WateringFolder)
        
    def loadProjects(self):
        if not self.responseProjects:
            return
        
        for i in range(0, self.responseProjects.json()["total"]):
            self.projects_box.addItem(self.responseProjects.json()["data"][i]["name"])
            self.listOfProjects.append((self.responseProjects.json()["data"][i]["name"],
                                self.responseProjects.json()["data"][i]["serverKeyId"]))
        
        self.loadScenarios(self.projects_box.currentIndex())
        self.projects_box.currentIndexChanged.connect(self.loadScenarios)
        
    def loadScenarios(self, value):
        #Resetting scenarios box in case of changing the selected project.
        self.scenarios_box.clear()
        self.listOfScenarios = []

        self.ProjectName = self.listOfProjects[value][0]
        self.ProjectFK = self.listOfProjects[value][1]
        
        self.newProjectNameInput.setPlaceholderText(self.ProjectName)
        
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

    def offlineProcedures(self):
        self.Offline = True
        if os.path.exists(self.ProjectsJSON):
            with open(self.ProjectsJSON, 'r') as json_file:
                self.ProjectsJSON_data = json.load(json_file)
        
            if self.ProjectsJSON_data:
                self.OfflineProjects = self.getOfflineProjects()
                for i in range(0, len(self.OfflineProjects)):
                    self.projects_box.addItem(self.OfflineProjects[i][1])

                self.setOfflineScenarios()
                self.projects_box.currentIndexChanged.connect(self.setOfflineScenarios)
        else:
            iface.messageBar().pushMessage(("Error"), ("No projects found locally. Connect to WaterIng and load a project from server."), level=1, duration=5)
                   
    def setOfflineScenarios(self):
        self.scenarios_box.clear()
        self.ProjectFK = self.OfflineProjects[self.projects_box.currentIndex()][0]
        self.ProjectName = self.OfflineProjects[self.projects_box.currentIndex()][1]
        self.OfflineScenarios = self.getOfflineScenarios(self.ProjectFK)
        
        for i in range(0, len(self.OfflineScenarios)):
            self.scenarios_box.addItem(self.OfflineScenarios[i][0])
            
    def checkExistingProject(self):
        #if there is a project opened
        if not WateringUtils.isScenarioNotOpened() or WateringUtils.isProjectOpened():
            if self.ProjectFK != WateringUtils.getProjectId():
                self.saveCurrentProject()
            else:
                #todo clear only watering layers
                QgsProject.instance().clear()
                self.startProject()
        else:
            self.startProject()

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
        self.startProject()
    
    def startProject(self):
        current_index = self.scenarios_box.currentIndex()
        scenarios = self.OfflineScenarios if self.Offline else self.listOfScenarios

        if scenarios and 0 <= current_index < len(scenarios):
            self.ScenarioName, self.ScenarioFK = scenarios[current_index][0], scenarios[current_index][1]
            
            if self.Offline:
                self.handleOfflineScenario()
            else:
                self.handleOnlineScenario()
        else:
            self.handleInvalidScenario()

    def handleOfflineScenario(self):
        if self.isOfflineScenarioVersion():
            self.openProjectFromFolder()
        else:
            self.handleInvalidScenario()

    def handleOnlineScenario(self):
        if self.isOfflineScenarioVersion():
            self.openAndUpdate()
        else:
            self.createNewProjectFromServer()

    def handleInvalidScenario(self):
        iface.messageBar().pushMessage(self.tr("Error"), self.tr(f"Cannot open {self.ProjectName}-{self.ScenarioName} offline."), level=1, duration=5)
        
        if self.ProjectFK in self.ProjectsJSON_data:
            
            if "scenarios" in self.ProjectsJSON_data[self.ProjectFK] is not None:
                
                if self.ScenarioFK in self.ProjectsJSON_data[self.ProjectFK]["scenarios"]:
                    
                    self.ProjectsJSON_data.pop(self.ProjectFK["scenarios"][self.ScenarioFK]) 
                
            else:
                
                del self.ProjectsJSON_data[self.ProjectFK]
                
        with open(self.ProjectsJSON, 'w') as file:
            json.dump(self.ProjectsJSON_data, file)
                
    def isOfflineScenarioVersion(self):
        scenarioInMetadata = False
        scenarioInFolder = False
        folder_project = os.path.join(self.WateringFolder, self.ProjectFK)
        scenario_folder = os.path.join(folder_project, self.ScenarioFK)
        
        if not os.path.exists(self.ProjectsJSON):
            with open(self.ProjectsJSON, 'w') as json_file:
                json.dump({}, json_file)
            self.ProjectsJSON_data = {}
        else:
            with open(self.ProjectsJSON, 'r') as json_file:
                self.ProjectsJSON_data = json.load(json_file)

        # Check scenario in metadata
        if self.ProjectFK in self.ProjectsJSON_data:
            if self.ScenarioFK in self.ProjectsJSON_data[self.ProjectFK]["scenarios"]:
                scenarioInMetadata = True
        
        # Check scenario in folder
        if os.path.exists(folder_project) and os.path.exists(scenario_folder):
            scenarioInFolder = True

        if scenarioInMetadata and scenarioInFolder:
            return True

        return False

    def openAndUpdate(self):
        self.OfflineProjects = self.getOfflineProjects()
        self.OfflineScenarios = self.getOfflineScenarios(self.ProjectFK)
        self.openProjectFromFolder()
        self.updateProject()
        self.loadMap()
        self.zoomToProject()
    
    def updateProject(self):
        self.scenario_folder = self.WateringFolder + self.ProjectFK + "/" + self.ScenarioFK + '/'
        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        self.myScenarioUnitOfWork.updateAll()
        
    def setWateringFolderAppData(self, path):
        #Creates directory QGISWatering inside Appdata
        folder = path + self.ProjectFK
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        self.project_path = folder

    def writeScenarioInProjectsJSON(self):
        #Creates the json file if it does not exists
        if not os.path.exists(self.ProjectsJSON):
            data = {}  
            with open(self.ProjectsJSON, 'w') as json_file:
                json.dump(data, json_file)

        #Load the current content of the JSON file
        with open(self.ProjectsJSON, 'r') as json_file:
            data = json.load(json_file)

        if not self.ProjectFK in data:
            data[self.ProjectFK] = {
            "name": self.ProjectName,
            "scenarios": {}
            }
            
        data[self.ProjectFK]["scenarios"][self.ScenarioFK] = {"name": self.ScenarioName}

        with open(self.ProjectsJSON, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def getOfflineProjects(self):
        return [(key, value["name"]) for key, value in self.ProjectsJSON_data.items()]
    
    def getOfflineScenarios(self, project_key):
        if project_key in self.ProjectsJSON_data:
            scenario_data = self.ProjectsJSON_data[project_key].get("scenarios", {})
            return [(scenario["name"], scenario_key) for scenario_key, scenario in scenario_data.items()]
    
        return []
        
    def openProjectFromFolder(self):
        # Load the project
        self.loadOfflineScenario()  
        iface.mapCanvas().refresh()
    
    def loadOfflineScenario(self):
        project = QgsProject.instance()
        
        project_path = self.WateringFolder + self.ProjectFK + "/" + self.ProjectName + '.qgz'

        success = project.read(project_path)
        if success:
            print(f"Project {project_path} successfully loaded.")
        else:
            print(f"Failed to load project {project_path}.")
        root = project.layerTreeRoot()

        # Find the root group by name
        group = root.findGroup("WaterIng Network Layout")
        
        # If the group doesn't exist, create it
        if not group:
            group = root.addGroup("WaterIng Network Layout")

        # Remove all layers from the group
        for child in group.children():
            if isinstance(child, QgsLayerTreeGroup):
                group.removeChildNode(child)
            else:
                project.removeMapLayer(child.layerId())

        # Get Scenario Data
        scenario_path = self.WateringFolder + self.ProjectFK + "/" + self.ScenarioFK + '/'
        
        # Shp files in the order they are going to be loaded
        shp_files = ['watering_demand_nodes.shp', 
                     'watering_waterMeter.shp', 
                     'watering_reservoirs.shp', 
                     'watering_tanks.shp', 
                     'watering_pumps.shp', 
                     'watering_valves.shp',                   
                     'watering_pipes.shp']
        
        # Load all .shp files from the directory and add them to WaterIng root group
        for element_layer in shp_files:
            layer_path = os.path.join(scenario_path, element_layer)
            layer_name = os.path.splitext(element_layer)[0]
            layer = QgsVectorLayer(layer_path, layer_name, "ogr")

            if layer.isValid():
                project.addMapLayer(layer, False)
                group.addLayer(layer)

    def createNewProjectFromServer(self):
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
        
        #Create scenario folder
        self.scenario_folder = self.project_path + "/" + scenarioFK
        os.makedirs(self.scenario_folder, exist_ok=True)
    
    def CreateLayers(self):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.addGroup("WaterIng Network Layout")

        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        self.myScenarioUnitOfWork.loadAll()
        
        self.loadMap()
        self.zoomToProject()
        self.setStatusBar()
        self.writeScenarioInProjectsJSON()
        self.done(True) #instead of just closing we call done(true) to return 1 as result of this dialog modal execution
        self.close()
        
    def writeWateringMetadata(self):
        WateringUtils.setProjectMetadata("server_project_name", self.listOfProjects[self.projects_box.currentIndex()][0])
        WateringUtils.setProjectMetadata("project_id", self.listOfProjects[self.projects_box.currentIndex()][1])
        WateringUtils.setProjectMetadata("scenario_name", self.listOfScenarios[self.scenarios_box.currentIndex()][0])
        WateringUtils.setProjectMetadata("scenario_id", self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        
    def loadMap(self):
        map_layer = "Open Street Maps"
        if not any(layer.name() == map_layer for layer in QgsProject.instance().mapLayers().values()):
            tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            layer = QgsRasterLayer(tms,'Open Street Maps', 'wms')
            QgsProject.instance().addMapLayer(layer, False)
            root = QgsProject.instance().layerTreeRoot()
            root.insertChildNode(5, QgsLayerTreeLayer(layer))
        else:
            print("Map already loaded")
    
    def setStatusBar(self):
        project_name = WateringUtils.getProjectMetadata("project_name")
        scenario_name = WateringUtils.getProjectMetadata("scenario_name")
        
        message = "Project: " + project_name + " | Scenario: " + scenario_name
        
        iface.mainWindow().statusBar().showMessage(message)  
    
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
        