# -*- coding: utf-8 -*-
from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeLayer, Qgis, QgsRectangle, QgsVectorLayer
from qgis.core import  QgsWkbTypes, QgsLayerTreeGroup, QgsFeature,  QgsVectorFileWriter
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QDockWidget, QLabel
from PyQt5.QtCore import Qt

import os
import json
import requests
import glob
import uuid
import shutil
import processing
from functools import partial

from ..unitofwork.scenarioUnitOfWork import scenarioUnitOfWork
from ..watering_utils import WateringUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_load_dialog.ui'))

class WateringLoad(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WateringLoad, self).__init__(parent)
        self.setupUi(self)
        # Ui elements
        self.new_project_name.hide()
        self.create_scenario.hide()
        self.clone_title.hide()
        self.clone_box.hide()
        self.cloned_scenario_name.hide()
        self.cloneScenarioBtn.hide()
        self.newProjectCheckBox.clicked.connect(self.checkUserControlStateProject)
        self.newScenarioCheckBox.clicked.connect(self.checkUserControlStateScenario)
        self.cloneCheckBox.clicked.connect(self.checkUserControlState)
        self.scenarios_box.currentIndexChanged.connect(self.setCloningScenarioName)
        
        #Variables 
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
        self.WateringFolder = WateringUtils.get_watering_folder()
        self.ProjectsJSON= WateringUtils.get_projects_json_path()
        self.ProjectsJSON_data = None
        self.block = False
        self.Offline = False
        self.initializeRepository()
        self.newProjectBtn.clicked.connect(self.checkAction)
        self.cloneScenarioBtn.clicked.connect(self.cloneScenario)
        self.mergeScenariosBtn.clicked.connect(self.mergeScenarios)
    
    def initializeRepository(self):
        print("OS TOKEN TIMER: ", os.environ.get('TOKEN_TIMER'))
        if os.environ.get('TOKEN') == None or os.environ.get('TOKEN_TIMER') == "False":
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
        self.initializeMergeSection()
        self.newShpDirectory.setFilePath(self.WateringFolder)
        
    def loadProjects(self):
        self.projects_box.clear()
        self.listOfProjects = []
        
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
        
        if 0 <= value < len(self.listOfProjects):
            self.ProjectName, self.ProjectFK = self.listOfProjects[value]
        
            self.new_project_name.setPlaceholderText(self.ProjectName)
            
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
        else:
            self.scenarios_box.clear()

    def offlineProcedures(self):
        self.projects_box.clear()
        self.Offline = True
        if os.path.exists(self.ProjectsJSON):
            with open(self.ProjectsJSON, 'r') as json_file:
                self.ProjectsJSON_data = json.load(json_file)
        
            if self.ProjectsJSON_data:
                self.OfflineProjects = self.getOfflineProjects()
                for i in range(0, len(self.OfflineProjects)):
                    self.projects_box.addItem(self.OfflineProjects[i][1])
                    self.listOfProjects.append((self.OfflineProjects[i][1],
                                                self.OfflineProjects[i][0]))
                    

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
            self.listOfScenarios.append((self.OfflineScenarios[i][0],
                                         self.OfflineScenarios[i][1]))
    
    def checkAction(self):
        if not self.newProjectCheckBox.isChecked() and not self.newScenarioCheckBox.isChecked():
            self.checkExistingProject(); return 
            
        newProjectKeyId = uuid.uuid4()
        newScenarioKeyId = uuid.uuid4()
        newScenarioName  = self.create_scenario.text() or "My Project Scenario"
        
        if self.newProjectCheckBox.isChecked() and self.newScenarioCheckBox.isChecked():
            self.createNewProjectAndScenario(newProjectKeyId, newScenarioKeyId)
            self.newProjectCheckBox.setChecked(False)
            self.newScenarioCheckBox.setChecked(False)
            self.checkUserControlStateProject()
            self.checkUserControlStateScenario()
            self.initializeRepository(); return
        
        if self.newProjectCheckBox.isChecked():
            self.createNewProject(newProjectKeyId)
            self.newProjectCheckBox.setChecked(False)
            self.checkUserControlStateProject()
            self.initializeRepository(); return
            
        if self.newScenarioCheckBox.isChecked():
            self.createNewScenario(newScenarioKeyId, None, newScenarioName)
            self.newScenarioCheckBox.setChecked(False)
            self.checkUserControlStateScenario()
            self.initializeRepository(); return
            
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
            
        for dock_widget in iface.mainWindow().findChildren(QDockWidget):
            if iface.mainWindow().dockWidgetArea(dock_widget) == Qt.RightDockWidgetArea:
                dock_widget.close()

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
            self.openProjectScenario()
        else:
            self.handleCanNotOpenProjectScenario()
        
        isThereConnectionAtDialog = self.Offline
        self.done(True) #instead of just closing we call done(true) to return 1 as result of this dialog modal execution
        self.close()
        

    def openProjectScenario(self):
        justCreated = False
        self.writeWateringMetadata()
        WateringUtils.setProjectMetadata("project_path", self.WateringFolder + self.ProjectFK)

        existScenarioOffline = self.isOfflineScenarioVersion()
        
        if (not existScenarioOffline): 
            existScenarioOffline = self.createNewProjectFromServer()
            justCreated = True
        
        if existScenarioOffline: self.openExistingWaterIngProject(justCreated)
        else: 
            self.handleCanNotOpenProjectScenario()
            return



    def handleCanNotOpenProjectScenario(self):
        iface.messageBar().pushMessage(self.tr("Error"), self.tr(f"Cannot open {self.ProjectName}-{self.ScenarioName} offline."), level=1, duration=5)
        
        if self.ProjectFK in self.ProjectsJSON_data:
            if self.ProjectsJSON_data[self.ProjectFK]["scenarios"] != {}:
                if self.ScenarioFK in self.ProjectsJSON_data[self.ProjectFK]["scenarios"]:
                    del self.ProjectsJSON_data[self.ProjectFK]["scenarios"][self.ScenarioFK]
            # If there is no scenario in projects.json[ProjectFK], delete this project
            else:
                del self.ProjectsJSON_data[self.ProjectFK]
                
        with open(self.ProjectsJSON, 'w') as file:
            json.dump(self.ProjectsJSON_data, file)
            
        self.offlineProcedures()
                
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

    def openExistingWaterIngProject(self, justCreated):
        self.scenario_folder = self.WateringFolder + self.ProjectFK + "/" + self.ScenarioFK + '/'
        
        self.OfflineProjects = self.getOfflineProjects()
        self.OfflineScenarios = self.getOfflineScenarios(self.ProjectFK)
        self.openProjectFromFolder()
        if not self.Offline:
            self.updateProject(justCreated)
        else: 
            WateringUtils.setProjectMetadata("scenario_folder", str(self.scenario_folder))
            WateringUtils.setProjectMetadata("scenario_fk", str(self.listOfScenarios[self.scenarios_box.currentIndex()][1]))
            self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        self.loadOpenStreetMapLayer()
        self.zoomToProject()
        self.done(True)
    
    def updateProject(self, justCreated):
        #self.scenario_folder = self.WateringFolder + self.ProjectFK + "/" + self.ScenarioFK + '/'
        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        # Re-established for testings
        #if (not justCreated): self.myScenarioUnitOfWork.updateAll()
        
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
        project_path = self.WateringFolder + self.ProjectFK + "/" + self.ProjectName + '.qgz'
        scenario_path = self.WateringFolder + self.ProjectFK + "/" + self.ScenarioFK + '/'
        
        self.loadOfflineScenario(project_path, scenario_path)  
        iface.mapCanvas().refresh()
    
    def checkCreateInitializeGroup(self, project, groupName):
        root = project.layerTreeRoot()

        # Find the root group by name
        group = root.findGroup(groupName)

        # If the group doesn't exist, create it
        if not group:
            group = root.addGroup(groupName)

        # Remove all layers from the group
        for child in group.children():
            if isinstance(child, QgsLayerTreeGroup):
                group.removeChildNode(child)
            else:
                project.removeMapLayer(child.layerId())

        return group
    
    def loadOfflineScenario(self, project_path, scenario_path):
        project = QgsProject.instance()

        success = project.read(project_path)
        
        if success:
            print(f"Project {project_path} successfully loaded.")
        else:
            print(f"Failed to load project {project_path}.")

        self.createAndOpenGroups(scenario_path)

    def createAndOpenGroups(self, scenario_path):
        project = QgsProject.instance()
        
        group_elements = self.checkCreateInitializeGroup(project, "WaterIng Network Layout")
        group_sensors = self.checkCreateInitializeGroup(project, "Sensors")
        #group_backup = self.checkCreateInitializeGroup(project, "Backup")

        shp_element_files = ['watering_demand_nodes.shp', 
                            'watering_reservoirs.shp', 
                            'watering_tanks.shp', 
                            'watering_pumps.shp', 
                            'watering_valves.shp',                   
                            'watering_pipes.shp']
        
        shp_filesMonitoring = ['watering_waterMeter.shp',
                               'watering_sensors.shp']
        
        shp_backupFiles = ['watering_demand_nodes_backup.shp', 
                           'watering_reservoirs_backup.shp', 
                           'watering_tanks_backup.shp', 
                           'watering_pumps_backup.shp', 
                           'watering_valves_backup.shp',
                           'watering_pipes_backup.shp',
                           'watering_waterMeter_backup.shp',
                           'watering_sensors_backup.shp']

        self.openGroup(shp_element_files, group_elements, scenario_path)
        self.openGroup(shp_filesMonitoring, group_sensors, scenario_path)
        self.openLayerGroupFalseVisibility(shp_backupFiles, scenario_path)
        
    def openGroup(self, group_list, group, scenario_path):
        for element_layer in group_list:
            layer_path = os.path.join(scenario_path, element_layer)
            layer_name = os.path.splitext(element_layer)[0]
            layer = QgsVectorLayer(layer_path, layer_name, "ogr")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer, False)
                group.addLayer(layer)

                layer.editingStarted.connect(partial(self.layerEditionStarted, layer_name))        
                
            else: 
                print("Layer not valid: ", element_layer)
        
    def openLayerGroupFalseVisibility(self, group_list, scenario_path):
        for element_layer in group_list:
            layer_path = os.path.join(scenario_path, element_layer)
            layer_name = os.path.splitext(element_layer)[0]
            layer = QgsVectorLayer(layer_path, layer_name, "ogr")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer, False)    
            else: 
                print("Layer not valid: ", element_layer)
        
    def layerEditionStarted(self, layer_name):
        print("Edition started at layer ", layer_name)
    
    def createNewProjectFromServer(self):
        if self.Offline: return False

        #project name
        project = QgsProject.instance()
        name = self.new_project_name.text()
        project_name = self.new_project_name.placeholderText() if not name else name
        
        #creates the project folder within the chosen folder (Watering folder in appdata by default)
        self.setWateringFolderAppData(self.newShpDirectory.filePath())
        project.setFileName(project_name)
        self.projectPathQgsProject = self.project_path + "/" + project_name + ".qgz"
        project.write(self.projectPathQgsProject)
            
        WateringUtils.setProjectMetadata("local_project_name", project_name)

        #create scenario folder
        self.createScenarioFolder()
        
        #load layers
        self.CreateLayers()
        
        #here A
        # scenarioName = WateringUtils.getProjectMetadata("scenario_name")
        # scenarioFK = WateringUtils.getProjectMetadata("scenario_id")
        # projectKey = WateringUtils.getProjectMetadata("project_id")
        # keyUpdate = scenarioFK + "last_general_update"
        # date = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
        # WateringUtils.setProjectMetadata(keyUpdate, date)
        
        WateringUtils.update_last_updated(self.ScenarioFK)
        
        # print("SAVING LAST UPDATED")
        # print(scenarioName)
        # print(scenarioFK)
        # print("key update: ", keyUpdate)
        # print("Date: ", date)
        
        return True
    
    

    def createScenarioFolder(self):
        scenarioFK = WateringUtils.getProjectMetadata("scenario_id")
        
        #Create scenario folder
        self.scenario_folder = self.project_path + "/" + scenarioFK
        os.makedirs(self.scenario_folder, exist_ok=True)


    
    def CreateLayers(self):
        scenarioFK = self.listOfScenarios[self.scenarios_box.currentIndex()][1]
        
        
        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        self.myScenarioUnitOfWork.loadAll()
        
        self.loadOpenStreetMapLayer()
        self.setStatusBar()
        self.writeScenarioInProjectsJSON()
        self.done(True) #instead of just closing we call done(true) to return 1 as result of this dialog modal execution
        self.close()
        
    def writeWateringMetadata(self):
        WateringUtils.setProjectMetadata("server_project_name", self.listOfProjects[self.projects_box.currentIndex()][0])
        WateringUtils.setProjectMetadata("project_id", self.listOfProjects[self.projects_box.currentIndex()][1])
        WateringUtils.setProjectMetadata("scenario_name", self.listOfScenarios[self.scenarios_box.currentIndex()][0])
        WateringUtils.setProjectMetadata("scenario_id", self.listOfScenarios[self.scenarios_box.currentIndex()][1])
        
    def loadOpenStreetMapLayer(self):
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
                
    def checkUserControlState(self):
        #Clone Scenario
        if self.cloneCheckBox.isChecked():
            if not self.Offline:
                self.clone_title.show()
                self.clone_box.show()
                self.cloned_scenario_name.show()
                self.cloneScenarioBtn.show()
                self.loadProjectsToClone()
        else:
            self.clone_title.hide()
            self.clone_box.hide()
            self.cloned_scenario_name.hide()
            self.cloneScenarioBtn.hide()
    
    def checkUserControlStateScenario(self):
        # Scenarios
        if self.newScenarioCheckBox.isChecked():
            self.scenarios_box.hide()
            self.create_scenario.show()
            self.create_scenario.setPlaceholderText("My New Scenario") 
            self.newProjectBtn.setText("Create new WaterIng Scenario") 
        else:
            self.newProjectBtn.setText("Load WaterIng Data") 
            self.scenarios_box.show()
            self.create_scenario.hide()
    
    def checkUserControlStateProject(self):
        # Projects
        if self.newProjectCheckBox.isChecked():
            self.projects_box.hide()
            self.new_project_name.show()
            self.new_project_name.setPlaceholderText("My New Project") 
            self.newProjectBtn.setText("Create new WaterIng Project") 
        else:
            self.newProjectBtn.setText("Load WaterIng Data") 
            self.projects_box.show()
            self.new_project_name.hide()
            
    def setCloningScenarioName(self):
        self.cloned_scenario_name.setPlaceholderText(self.scenarios_box.currentText() + " Cloned version")
        
    def loadProjectsToClone(self):
        for item in self.listOfProjects:
            self.clone_box.addItem(item[0])
    
    def cloneScenario(self):
        folder_path = WateringUtils.get_watering_folder()
        fromProjectKeyID = self.listOfProjects[self.projects_box.currentIndex()][1]
        fromProjectName = self.listOfProjects[self.projects_box.currentIndex()][0]
        fromProjectKeyScenario = self.listOfScenarios[self.scenarios_box.currentIndex()][1]
        clonedScenarioName = self.listOfScenarios[self.scenarios_box.currentIndex()][0]
        toProjectKeyID = self.listOfProjects[self.clone_box.currentIndex()][1]
        toProjectKeyScenario = str(uuid.uuid4())
        scenarioName = self.cloned_scenario_name.text() or clonedScenarioName + " Cloned Version"
        
        scenario_created = self.createNewScenario(toProjectKeyScenario, toProjectKeyID, scenarioName)
        
        if scenario_created:
            self.clone_scenario(folder_path, fromProjectName, fromProjectKeyID, fromProjectKeyScenario, 
                                toProjectKeyID, toProjectKeyScenario, clonedScenarioName)
        else:
            WateringUtils.error_message("Couldn’t clone the scenario. Please try again.")

    def update_last_updated(self):
        # Open and load the JSON file
        json_file_path = self.ProjectsJSON
        project_key = self.ProjectFK
        scenario_key = self.ScenarioFK
        
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Check if the project key and scenario key exist
        if project_key in data and "scenarios" in data[project_key] and scenario_key in data[project_key]["scenarios"]:
            # Update the 'lastUpdated' field with the current datetime in ISO format
            data[project_key]["scenarios"][scenario_key]["lastUpdated"] = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
        else:
            print("Project or Scenario key not found in the provided JSON.")
            return
        
        # Write the updated data back to the JSON file
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def createNewProjectAndScenario(self, projectKeyId, scenarioKeyId):
        project_creation_success, createdProjectData = self.createNewProject(projectKeyId)
        if not project_creation_success:
            WateringUtils.error_message("Project creation failed. Please try again.")
            return False

        serverProjectKeyId = createdProjectData.json()["serverKeyId"]
        scenarioName = self.create_scenario.text() or "My Project Scenario"
        
        scenario_creation_success = self.createNewScenario(scenarioKeyId, serverProjectKeyId, scenarioName)
        if not scenario_creation_success:
            WateringUtils.error_message("Scenario creation failed. Please try again.")
            return False

        WateringUtils.success_message("Project and scenario created successfully!")
        return True

    def createNewProject(self, keyId):
        projectName = self.new_project_name.text()
        description = "Project created in QGIS WaterIng Plugin"
        
        newProjectJson = {
            "keyId": "{}".format(keyId),
            "name": "{}".format(projectName),
            "description": "{}".format(description)
        }
        
        url = WateringUtils.getServerUrl() + "/api/v1/ProjectWaterNetworks"
        headers = {'Authorization': "Bearer {}".format(self.token)} 
        response = requests.post(url, headers=headers, json=newProjectJson)
        
        if response.status_code == 200:
            WateringUtils.success_message("Project created successfully!")
            return True, response
        
        WateringUtils.success_message("Project creation failed. Please try again.")
        return False
        
    def createNewScenario(self, keyId, projectKeyId, scenarioName):
        if not projectKeyId:
            current_index = self.projects_box.currentIndex()
            projectId = self.listOfProjects[current_index][1]
        else:
            projectId = projectKeyId
            
        description =  "Scenario created in QGIS WaterIng Plugin"
        
        newScenarioJson = {
            "keyId": "{}".format(keyId),
            "serverKeyId": "{}".format(keyId),
            "fkWaterProject": "{}".format(projectId),
            "name": "{}".format(scenarioName),
            "description": "{}".format(description)
        }
        
        url = WateringUtils.getServerUrl() + "/api/v1/ScenarioWaterNetwork"
        headers = {'Authorization': "Bearer {}".format(self.token)} 
        response = requests.post(url, headers=headers, json=newScenarioJson)
        
        if response.status_code == 200:
            WateringUtils.success_message("Scenario created successfully!")
            return True
        
        WateringUtils.error_message("Scenario creation failed. Please try again.")
        return False
    
    def clone_scenario(self, folder_path, fromProjectName, fromProjectKeyID, 
                       fromProjectKeyScenario, toProjectKeyID, 
                       toProjectKeyScenario, clonedScenarioName):
        
        source_path = os.path.join(folder_path, fromProjectKeyID, fromProjectKeyScenario)
        target_path = os.path.join(folder_path, toProjectKeyID, toProjectKeyScenario)

        os.makedirs(target_path, exist_ok=True)

        for item in os.listdir(source_path):
            s = os.path.join(source_path, item)
            d = os.path.join(target_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        creation_time = '1800-11-29T10:28:46.2756439Z' #WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
        
        projects_json_path = os.path.join(folder_path, 'projects.json')
        
        with open(projects_json_path, 'r+') as f:
            projects = json.load(f)

            if toProjectKeyID not in projects:
                projects[toProjectKeyID] = {"name": "{}".format(fromProjectName),
                                            "scenarios": {}}

            projects[toProjectKeyID]["scenarios"][toProjectKeyScenario] = {
                "name": "{}".format(clonedScenarioName),
                "lastUpdated": "{}".format(creation_time)
            }

            f.seek(0)
            json.dump(projects, f, indent=4)
            f.truncate()
        
        return target_path
    
    # Merge methods

    def feature_signature(self, feature):
        return feature.geometry().asWkt()

    def load_layer(self, layer_path):
        layer = QgsProject.instance().mapLayersByName(layer_path)
        return layer[0] if layer else QgsVectorLayer(layer_path, "Layer", "ogr")

    def copy_features(self, source_layer, dest_dp):
        signatures = set()
        for feature in source_layer.getFeatures():
            signature = self.feature_signature(feature)
            if signature not in signatures:
                new_feature = QgsFeature(feature)
                dest_dp.addFeature(new_feature)
                signatures.add(signature)

    def merge_layers(self, layer_path1, layer_path2, merged_layer_name):
        layer1 = self.load_layer(layer_path1)
        layer2 = self.load_layer(layer_path2)

        if layer1.geometryType() != layer2.geometryType():
            raise ValueError("Mismatched geometry types.")

        crs = layer1.crs().authid()
        geom_type = QgsWkbTypes.displayString(layer1.wkbType())
        merged_layer = QgsVectorLayer(f"{geom_type}?crs={crs}", merged_layer_name, "memory")

        dp = merged_layer.dataProvider()
        dp.addAttributes(layer1.fields())
        merged_layer.updateFields()

        self.copy_features(layer1, dp)
        self.copy_features(layer2, dp)

        merged_layer.updateExtents()
        QgsProject.instance().addMapLayer(merged_layer)

        return merged_layer
    
    def initializeMergeSection(self):
        self.loadProjectsToMerge()
        self.loadScenariosToMerge()
        self.loadMergedScenarioProjectDestination()
        
        self.merge_projects_box.currentIndexChanged.connect(self.loadScenariosToMerge)
        
    def loadProjectsToMerge(self):
        for item in self.listOfProjects:
            self.merge_projects_box.addItem(item[0])

    def loadScenariosToMerge(self):
        for item in self.listOfScenarios:
            self.merge_scenarios_box.addItem(item[0])
    
    def loadMergedScenarioProjectDestination(self):
        for item in self.listOfProjects:
            self.merge_box.addItem(item[0])
    
    def mergeScenarios(self):
        folder_path = WateringUtils.get_watering_folder()
        
        # Scenario A
        fromProjectAKeyID = self.listOfProjects[self.projects_box.currentIndex()][1]
        fromProjectAName = self.listOfProjects[self.projects_box.currentIndex()][0]
        fromProjectAKeyScenario = self.listOfScenarios[self.scenarios_box.currentIndex()][1]
        clonedScenarioAName = self.listOfScenarios[self.scenarios_box.currentIndex()][0]
        
        # Scenario B
        fromProjectBKeyID = self.listOfProjects[self.merge_projects_box.currentIndex()][1]
        fromProjecBtName = self.listOfProjects[self.merge_projects_box.currentIndex()][0]
        fromProjectBKeyScenario = self.listOfScenarios[self.merge_scenarios_box.currentIndex()][1]
        clonedScenarioBName = self.listOfScenarios[self.merge_projects_box.currentIndex()][0]
        
        # Merged Scenario - Scenario C
        toProjectKeyID = self.listOfProjects[self.merge_box.currentIndex()][1]
        toProjectKeyScenario = str(uuid.uuid4())
        
        defaultMergedScenarioName = "Merged: " + clonedScenarioAName + " & " + clonedScenarioBName 
        scenarioName = self.merged_scenario_name.text() or defaultMergedScenarioName
        scenario_created = self.createNewScenario(toProjectKeyScenario, toProjectKeyID, scenarioName)
        
        if scenario_created:
            merged_project_path = self.clone_scenario(folder_path, fromProjectAName, fromProjectAKeyID, fromProjectAKeyScenario, 
                                                      toProjectKeyID, toProjectKeyScenario, clonedScenarioAName)
        else:
            WateringUtils.error_message("Couldn’t clone the scenario. Please try again."); return
        
        scenarioB_path = os.path.join(folder_path, fromProjectBKeyID, fromProjectBKeyScenario)
        merged = self.merge_shapefiles(merged_project_path, scenarioB_path)
        
        print("Merged: ", merged)
        
    def merge_shapefiles(self, folderA, folderB):
        for filename in os.listdir(folderA):
            if filename.endswith(".shp"):
                filePathA = os.path.join(folderA, filename)
                filePathB = os.path.join(folderB, filename)

                if os.path.exists(filePathB):
                    layerA = QgsVectorLayer(filePathA, "layerA", "ogr")
                    layerB = QgsVectorLayer(filePathB, "layerB", "ogr")
                    
                    if not layerA.isValid() or not layerB.isValid():
                        print(f"Failed to load layers for {filename}.")
                        continue
                    
                    merged_layer = processing.run("native:mergevectorlayers", {
                        'LAYERS': [layerA, layerB],
                        'CRS': layerA.crs(), 
                        'OUTPUT': 'memory:' 
                    })['OUTPUT']

                    merged_filepath = os.path.join(folderA, f"merged_{filename}")
                    
                    QgsVectorFileWriter.writeAsVectorFormat(merged_layer, merged_filepath, "utf-8", driverName="ESRI Shapefile")
                    print(f"Merged shapefile saved as: {merged_filepath}")
                    return True
                else:
                    print(f"Shapefile {filename} in folder A does not have a corresponding file in folder B.")
