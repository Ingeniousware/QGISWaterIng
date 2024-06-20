# -*- coding: utf-8 -*-
from ..unitofwork.scenarioUnitOfWork import scenarioUnitOfWork
from ..watering_utils import WateringUtils

import os, json, requests, glob, uuid, shutil, processing

import os
import geopandas as gpd
import pandas as pd
import time

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeLayer, Qgis, QgsRectangle, QgsVectorLayer
from qgis.core import  QgsWkbTypes, QgsLayerTreeGroup, QgsFeature,  QgsVectorFileWriter
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox, QLabel, QDockWidget
from PyQt5.QtCore import Qt
from functools import partial
from osgeo import ogr

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_load_dialog.ui'))

class WateringLoad(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        """Constructor."""
        super(WateringLoad, self).__init__(parent)
        self.setupUi(self)
        
        self.token = os.environ.get('TOKEN')
        self.online_projects_list = []
        self.offline_projects_list = []
        self.load_scenarios_list = []
        self.offline_scenarios_list = []
        self.clone_projects_list = []
        self.clone_scenarios_list = []
        self.merge_scenarios_list = []
        self.load_offline_scenarios = []
        self.current_project_fk = None
        self.current_project_name = None
        self.current_scenario_fk = None
        self.current_scenario_name = None
        self.response = None
        self.offline_mode = False
        self.main_watering_folder = WateringUtils.get_watering_folder()
        self.projects_json_file = WateringUtils.get_projects_json_path()
        self.projects_json_data = None
        
        self.initialize_repository()
        self.hide_ui_elements()
        self.set_buttons_and_checkboxes()

    def initialize_repository(self):
        self.response = WateringUtils.requests_get("/api/v1/ProjectWaterNetworks", {})
        if not self.response:
            self.run_offline_procedures()
        else:
            self.set_online_projects_list()
            self.set_combo_boxes()
            
        self.set_clone_projects_combo_box()
        self.set_merge_projects_combo_box()
        self.initialize_progress_bar()
        self.newShpDirectory.setFilePath(self.main_watering_folder)
        
    def set_buttons_and_checkboxes(self):
        self.new_project_checkBox.clicked.connect(self.handle_new_tab_ui_elements)
        self.merge_new_scenario_checkBox.clicked.connect(self.handle_merge_tab_ui_elements)
        self.new_button.clicked.connect(self.create_new_scenario_procedures)
        self.load_button.clicked.connect(self.checkExistingProject)
        self.load_projects_box.currentIndexChanged.connect(self.handle_load_scenarios_box)
        self.clone_button.clicked.connect(self.clone_scenario)
        self.merge_button.clicked.connect(self.initialize_merge)
    
    def set_online_projects_list(self):
        self.online_projects_list = []

        for i in range(0, self.response.json()["total"]):
            self.online_projects_list.append((self.response.json()["data"][i]["name"],
                                       self.response.json()["data"][i]["serverKeyId"]))

    def set_offline_projects_list(self, combo_box, scenarios_box, scenarios_list):
        if os.path.exists(self.projects_json_file):
            with open(self.projects_json_file, 'r') as json_file:
                self.projects_json_data = json.load(json_file)
        
            if self.projects_json_data:
                self.offline_projects_list = self.get_offline_projects()
                for i in range(0, len(self.offline_projects_list)):
                    combo_box.addItem(self.offline_projects_list[i][1])
                
                print("scenarios_box", scenarios_box)
                if scenarios_box is not None or scenarios_list is not None:
                    print("True")
                    self.set_offline_scenarios(combo_box, scenarios_box, scenarios_list)
                    combo_box.currentIndexChanged.connect(lambda : self.set_offline_scenarios(combo_box, scenarios_box, scenarios_list))
        else:
            WateringUtils.error_message("No projects found locally. Connect to WaterIng and load a project from server.")
            
    def run_offline_procedures(self):
        self.offline_mode = True
        self.offline_scenarios_list_load = []
        self.set_offline_projects_list(self.load_projects_box, self.load_scenarios_box, self.offline_scenarios_list_load)

    def hide_ui_elements(self):
        self.handle_new_tab_ui_elements()
        self.handle_merge_tab_ui_elements()

    def set_clone_projects_combo_box(self):
        self.offline_scenarios_list_clone = []
        self.set_offline_projects_list(self.clone_projects_box, self.clone_scenarios_box, self.offline_scenarios_list_clone)
        self.set_offline_projects_list(self.clone_box, None, None)
        
    def handle_new_tab_ui_elements(self):
        checked = self.new_project_checkBox.isChecked()
        self.new_project_label.setVisible(checked)
        self.new_project_name.setVisible(checked)
        self.new_projects_box.setVisible(not checked)
        self.new_source_project_label.setVisible(not checked)

    def handle_merge_tab_ui_elements(self):
        checked = self.merge_new_scenario_checkBox.isChecked()
        self.merge_new_scenario_label.setVisible(checked)
        self.merge_box.setVisible(checked)
        self.merge_name_scenario_label.setVisible(checked)
        self.merged_scenario_name.setVisible(checked)

    def initialize_progress_bar(self):
        self.progressBar.hide()
        self.progressBar.setRange(0, 100)
        
    def set_combo_boxes(self):
        self.set_project_combo_box(self.new_projects_box)
        self.set_project_combo_box(self.load_projects_box)
        self.set_scenario_combo_box(self.load_projects_box, self.load_scenarios_box, self.load_scenarios_list)
        
    def set_project_combo_box(self, combo_box):
        combo_box.clear()
        if self.online_projects_list:
            for project in self.online_projects_list:
                combo_box.addItem(project[0])

    def set_scenario_combo_box(self, projects_box, scenarios_box, scenarios_list):
        project_index = projects_box.currentIndex()
        scenarios_box.clear()
        scenarios_list.clear()

        if 0 <= project_index < len(self.online_projects_list):
            self.current_project_name, self.current_project_fk = self.online_projects_list[project_index]
            params = {'ProjectFK': "{}".format(self.current_project_fk), 'showRemoved': "{}".format(False)}

            response = WateringUtils.requests_get("/api/v1/ScenarioWaterNetwork", params)

            if not response:
                return

            for i in range(0, response.json()["total"]):
                scenarios_box.addItem(response.json()["data"][i]["name"])
                scenarios_list.append((response.json()["data"][i]["name"],
                                       response.json()["data"][i]["serverKeyId"]))

    def handle_load_scenarios_box(self):
        if not self.offline_mode:
            self.set_scenario_combo_box(self.load_projects_box, self.load_scenarios_box, self.load_scenarios_list)

    def set_offline_scenarios(self, projects_box, scenarios_box, scenarios_list):
        scenarios_box.clear()
        scenarios_list.clear()
        current_index = projects_box.currentIndex()

        self.current_project_fk = self.offline_projects_list[current_index][0]
        self.current_project_name = self.offline_projects_list[current_index][1]
        scenarios_list.extend(self.get_offline_scenarios(self.current_project_fk))

        print("offline_scenarios_list", scenarios_list)
        for i in range(0, len(scenarios_list)):
            scenarios_box.addItem(scenarios_list[i][0])

    def get_offline_projects(self):
        return [(key, value["name"]) for key, value in self.projects_json_data.items()]

    def get_offline_scenarios(self, project_key):
        if project_key in self.projects_json_data:
            scenario_data = self.projects_json_data[project_key].get("scenarios", {})
            return [(scenario["name"], scenario_key) for scenario_key, scenario in scenario_data.items()]
        return []

    def create_new_scenario_procedures(self):
        newProjectKeyId = str(uuid.uuid4())
        newScenarioKeyId = str(uuid.uuid4())
        newScenarioName = self.new_scenario_name.text() or "My Project Scenario"
        projectName = self.new_project_name.text() or "My Project"
        successfullyCreated = False
        currentProjectsList = self.offline_projects_list if self.offline_mode else self.online_projects_list
        
        if self.new_project_checkBox.isChecked():
            successfullyCreated = self.create_new_project_and_scenario(newProjectKeyId, newScenarioKeyId, projectName)
            if successfullyCreated:
                self.current_project_fk = currentProjectsList[self.new_projects_box.currentIndex()][0]
                self.current_scenario_fk = newScenarioKeyId
                self.current_project_name = currentProjectsList[self.new_projects_box.currentIndex()][1]
                self.current_scenario_name = newScenarioName
        else:   
            successfullyCreated = self.create_new_scenario(newScenarioKeyId, None, newScenarioName)
            if successfullyCreated:
                self.current_project_fk = newProjectKeyId
                self.current_scenario_fk = newScenarioKeyId
                self.current_project_name = projectName
                self.current_scenario_name = newScenarioName

        if successfullyCreated:
            self.create_scenario_folder()
            #load layers
            self.CreateLayers()
            
            self.open_watering_project(True)
            
    def create_new_project_and_scenario(self, projectKeyId, scenarioKeyId, projectName):
        project_creation_success, createdProjectData = self.create_new_project(projectKeyId, projectName)
        if not project_creation_success:
            WateringUtils.error_message("Project creation failed. Please try again.")
            return False

        serverProjectKeyId = createdProjectData.json()["serverKeyId"]
        scenarioName = self.new_scenario_name.text() or "My Project Scenario"

        scenario_creation_success = self.create_new_scenario(scenarioKeyId, serverProjectKeyId, scenarioName)
        if not scenario_creation_success:
            WateringUtils.error_message("Scenario creation failed. Please try again.")
            return False

        WateringUtils.success_message("Project and scenario created successfully!")
        return True

    def create_new_project(self, keyId, projectName):
        description = "Project created in QGIS WaterIng Plugin"

        newProjectJson = {
            "keyId": "{}".format(keyId),
            "name": "{}".format(projectName),
            "description": "{}".format(description)
        }

        url = WateringUtils.getServerUrl() + "/api/v1/ProjectWaterNetworks"
        headers = {'Authorization': "Bearer {}".format(self.token)} 

        error_message = "Failed to create new project. Try again later."
        response = WateringUtils.send_post_request(url, None, newProjectJson, headers, error_message)
        
        if response and response.status_code == 200:
            WateringUtils.success_message("Project created successfully!")
            return True, response

        WateringUtils.error_message("Project creation failed. Please try again.")
        return False

    def create_new_scenario(self, keyId, projectKeyId, scenarioName):
        if not self.online_projects_list:
            WateringUtils.error_message(self.tr("Functionality not available offline. Connect to Watering and try again."))
            return
        if not projectKeyId:
            current_index = self.new_projects_box.currentIndex()
            projectId = self.online_projects_list[current_index][1]
            print("current index: ", current_index)
            print("projectID: ", projectId)
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
        print("response.text: ", response.text)
        if response.status_code == 200:
            WateringUtils.success_message("Scenario created successfully!")
            return True

        WateringUtils.error_message("Scenario creation failed. Please try again.")
        return False

    def checkExistingProject(self):
        project = QgsProject.instance()
        should_start_project = not WateringUtils.isScenarioNotOpened() or WateringUtils.isProjectOpened()

        if should_start_project:
            current_project_id = WateringUtils.getProjectId()
            if self.current_project_fk != current_project_id:
                self.save_current_project()
            else:
                project.clear()
                self.start_project()
        else:
            self.start_project()

        for dock_widget in iface.mainWindow().findChildren(QDockWidget):
            if iface.mainWindow().dockWidgetArea(dock_widget) == Qt.RightDockWidgetArea:
                dock_widget.close()

    def save_current_project(self):
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(None,
                                            "Save Project",
                                            "The current project has unsaved changes. Do you want to save it before creating a new project?",
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                if WateringUtils.getProjectMetadata("project_path") != "default text":
                    if project.write():
                        WateringUtils.success_message(self.tr(f"Project saved at {project.fileName()}"))
                    else:
                        WateringUtils.success_message(self.tr("Failed to save the project."))
                else:
                    iface.actionSaveProjectAs().trigger()

            elif response == QMessageBox.Cancel:
                return

        project.clear()
        self.start_project()

    def start_project(self):
        self.progressBar.show()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        
        current_index = self.load_scenarios_box.currentIndex()
        scenarios = self.offline_scenarios_list if self.offline_mode else self.load_scenarios_list
        print("scenarios: ", scenarios)
        
        if scenarios and 0 <= current_index < len(scenarios):
            self.current_scenario_name, self.current_scenario_fk = scenarios[current_index][0], scenarios[current_index][1]
            self.open_scenario()
            self.progressBar.setValue(10)
        else:
            self.handle_failed_project_load()
        
        self.done(True)
        self.progressBar.hide()
        self.close()

    def open_scenario(self):
        justCreated = False
        WateringUtils.setProjectMetadata("project_path", self.main_watering_folder + self.current_project_fk)

        existScenarioOffline = self.is_offline_scenario_version()

        if (not existScenarioOffline): 
            existScenarioOffline = self.create_new_project_from_server()
            justCreated = True

        if existScenarioOffline: self.open_watering_project(justCreated)
        else: 
            self.handle_failed_project_load()
            return

    def is_offline_scenario_version(self):
        folder_project = os.path.join(self.main_watering_folder, self.current_project_fk)
        scenario_folder = os.path.join(folder_project, self.current_scenario_fk)

        if not os.path.exists(self.projects_json_file):
            with open(self.projects_json_file, 'w') as json_file:
                json.dump({}, json_file)
            self.projects_json_data = {}
        else:
            with open(self.projects_json_file, 'r') as json_file:
                self.projects_json_data = json.load(json_file)

        scenario_in_metadata = (self.current_project_fk in self.projects_json_data and 
                                self.current_scenario_fk in self.projects_json_data[self.current_project_fk].get("scenarios", {}))
        scenario_in_folder = os.path.exists(folder_project) and os.path.exists(scenario_folder)

        return scenario_in_metadata and scenario_in_folder

    def create_new_project_from_server(self):
        self.progressBar.setValue(20)
        if self.offline_mode: return False

        #project name
        project = QgsProject.instance()
        name = self.new_project_name.text()
        project_name = "test project " #self.new_project_name.placeholderText() if not name else name

        #self.setWateringFolderAppData(self.newShpDirectory.filePath())
        project.setFileName(project_name)
        self.projectPathQgsProject = self.get_project_folder() + "/" + project_name + ".qgz"
        project.write(self.projectPathQgsProject)

        WateringUtils.setProjectMetadata("local_project_name", project_name)

        #create scenario folder
        self.create_scenario_folder()
        self.progressBar.setValue(30)
        
        #load layers
        self.CreateLayers()

        WateringUtils.update_last_updated(self.current_scenario_fk)
        return True

    def get_project_folder(self):
        folder = self.main_watering_folder + self.current_project_fk

        if not os.path.exists(folder):
            os.makedirs(folder)

        return folder

    def create_scenario_folder(self):
        self.scenario_folder = self.get_project_folder() + "/" + self.current_scenario_fk
        os.makedirs(self.scenario_folder, exist_ok=True)

    def open_watering_project(self, justCreated):
        self.scenario_folder = self.main_watering_folder + self.current_project_fk + "/" + self.current_scenario_fk + '/'
        self.progressBar.setValue(45)
        self.openProjectFromFolder()
        self.progressBar.setValue(60)
        if not self.offline_mode:
            self.updateProject(justCreated)
        else: 
            self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.offline_scenarios_list[self.load_scenarios_box.currentIndex()][1])
        self.zoomToProject()
        self.progressBar.setValue(70)
        self.writeWateringMetadata()
        self.progressBar.setValue(90)
        self.done(True)

    def CreateLayers(self):
        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.current_scenario_fk)
        self.myScenarioUnitOfWork.loadAll(self.progressBar)

        self.write_scenario_in_projects_file()
        self.progressBar.setValue(100)
        self.done(True)
        self.close()

    def write_scenario_in_projects_file(self):
        if not os.path.exists(self.projects_json_file):
            data = {}  
            with open(self.projects_json_file, 'w') as json_file:
                json.dump(data, json_file)

        with open(self.projects_json_file, 'r') as json_file:
            data = json.load(json_file)

        if not self.current_project_fk in data:
            data[self.current_project_fk] = {
            "name": self.current_project_name,
            "scenarios": {}
            }
            
        data[self.current_project_fk]["scenarios"][self.current_scenario_fk] = {"name": self.current_scenario_name}

        with open(self.projects_json_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def openProjectFromFolder(self):
        # Load the project
        project_path = self.main_watering_folder + self.current_project_fk + "/" + self.current_project_name + '.qgz'
        scenario_path = self.main_watering_folder + self.current_project_fk + "/" + self.current_scenario_fk + '/'

        self.loadOfflineScenario(project_path, scenario_path)  
        iface.mapCanvas().refresh()

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

        all_layers_valid = True

        self.openGroup(shp_element_files, group_elements, scenario_path)
        self.openGroup(shp_filesMonitoring, group_sensors, scenario_path)
        self.openLayerGroupFalseVisibility(shp_backupFiles, scenario_path)
        
        for layer in QgsProject.instance().mapLayers().values():
            if not layer.isValid():
                all_layers_valid = False
                print(f"Layer {layer.name()} is not valid and cannot be added.")
                break

        if all_layers_valid:
            self.loadOpenStreetMapLayer()
        else:
            print("Some layers were invalid, delaying the loading of the Open Street Maps layer.")
        

    def openGroup(self, group_list, group, scenario_path):
        print("OPENING LAYERS OPENING LAYERS")
        for element_layer in group_list:
            layer_path = os.path.join(scenario_path, element_layer)
            layer_name = os.path.splitext(element_layer)[0]
            layer = QgsVectorLayer(layer_path, layer_name, "ogr")

            if layer.isValid():
                QgsProject.instance().addMapLayer(layer, False)
                group.addLayer(layer)
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
    
    def writeWateringMetadata(self):
        WateringUtils.setProjectMetadata("server_project_name", self.current_project_name)
        WateringUtils.setProjectMetadata("project_id", self.current_project_fk)
        WateringUtils.setProjectMetadata("scenario_name", self.current_scenario_name)
        WateringUtils.setProjectMetadata("scenario_id", self.current_scenario_fk)
    
    def updateProject(self, justCreated):
        self.myScenarioUnitOfWork = scenarioUnitOfWork(self.token, self.scenario_folder, self.current_scenario_fk)
        
    def handle_failed_project_load(self):
        WateringUtils.error_message(self.tr(f"Cannot open {self.current_project_name}-{self.current_scenario_name} offline."))

        if self.current_project_fk in self.projects_json_data:
            if self.projects_json_data[self.current_project_fk]["scenarios"] != {}:
                if self.current_scenario_fk in self.projects_json_data[self.current_project_fk]["scenarios"]:
                    del self.projects_json_data[self.current_project_fk]["scenarios"][self.current_scenario_fk]
            # If there is no scenario in projects.json[ProjectFK], delete this project
            else:
                del self.projects_json_data[self.current_project_fk]
                
        with open(self.projects_json_file, 'w') as file:
            json.dump(self.projects_json_data, file)
            
        self.run_offline_procedures()
    
    def clone_scenario(self):
        folder_path = WateringUtils.get_watering_folder()
        fromProjectKeyID = self.offline_projects_list[self.clone_projects_box.currentIndex()][0]
        fromProjectName = self.offline_projects_list[self.clone_projects_box.currentIndex()][1]
        fromProjectKeyScenario = self.offline_scenarios_list_clone[self.clone_scenarios_box.currentIndex()][1]
        clonedScenarioName = self.offline_scenarios_list_clone[self.clone_scenarios_box.currentIndex()][0]
        toProjectKeyID = self.offline_projects_list[self.clone_box.currentIndex()][0]
        toProjectKeyScenario = str(uuid.uuid4())
        scenarioName = self.cloned_scenario_name.text() or clonedScenarioName + " Cloned Version"
        
        scenario_created = self.create_new_scenario(toProjectKeyScenario, toProjectKeyID, scenarioName)
        
        if scenario_created:
            self.clone_scenario_procedures(folder_path, fromProjectName, fromProjectKeyID, fromProjectKeyScenario, 
                                toProjectKeyID, toProjectKeyScenario, scenarioName)
        else:
            WateringUtils.error_message("Couldn’t clone the scenario. Please try again.")
    
    def clone_scenario_procedures(self, folder_path, fromProjectName, fromProjectKeyID, 
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
    
    def set_merge_projects_combo_box(self):
        self.offline_scenarios_list_sourceA = []
        self.offline_scenarios_list_sourceB = []
        
        self.set_offline_projects_list(self.merge_projects_box_sourceA, self.merge_scenarios_box_sourceA, self.offline_scenarios_list_sourceA)
        self.set_offline_projects_list(self.merge_projects_box_sourceB, self.merge_scenarios_box_sourceB, self.offline_scenarios_list_sourceB)
        self.set_offline_projects_list(self.merge_box, None, None)
    
    def initialize_merge(self):
        print("self.projects: ", self.offline_projects_list)
        print(" ----- ")
        
        self.current_project_sourceA_fk = self.offline_projects_list[self.merge_projects_box_sourceA.currentIndex()][0]
        self.current_scenario_sourceA_fk = self.offline_scenarios_list_sourceA[self.merge_scenarios_box_sourceA.currentIndex()][1]
        self.current_project_sourceB_fk = self.offline_projects_list[self.merge_scenarios_box_sourceB.currentIndex()][0]
        self.current_scenario_sourceB_fk = self.offline_scenarios_list_sourceB[self.merge_scenarios_box_sourceB.currentIndex()][1]
        shps_list = ['watering_demand_nodes.shp', 
                    'watering_reservoirs.shp', 
                    'watering_tanks.shp', 
                    'watering_pumps.shp', 
                    'watering_valves.shp',                   
                    'watering_pipes.shp']
        
        print("RESULT : ")
        print( self.merge_and_replace_shapefiles(self.current_project_sourceA_fk,
                                          self.current_scenario_sourceA_fk,
                                          self.current_project_sourceB_fk,
                                          self.current_scenario_sourceB_fk,
                                          shps_list) )
        
    # NEW MERGE SHPS METHODS #
    
    def get_shapefile_path(self, project_fk, scenario_fk, shp_name):
        return os.path.join(self.main_watering_folder, project_fk, scenario_fk, shp_name)
    
    def load_shapefile(self, shapefile_path):
        if os.path.exists(shapefile_path):
            return gpd.read_file(shapefile_path)
        else:
            raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
    
    def save_shapefile(self, gdf, path):
        gdf.to_file(path)
    
    def merge_and_replace_shapefiles(self, projA_fk, scenA_fk, projB_fk, scenB_fk, shpsList):
        for shp_name in shpsList:
            shapefile_A_path = self.get_shapefile_path(projA_fk, scenA_fk, shp_name)
            shapefile_B_path = self.get_shapefile_path(projB_fk, scenB_fk, shp_name)
            shapefile_A = self.load_shapefile(shapefile_A_path)
            shapefile_B = self.load_shapefile(shapefile_B_path)
            if not shapefile_A.empty and not shapefile_B.empty:
                #merged_shapefile = shapefile_A.append(shapefile_B, ignore_index=True)
                merged_shapefile = gpd.GeoDataFrame(pd.concat([shapefile_A, shapefile_B], ignore_index=True)).drop_duplicates(subset='geometry')
                self.save_shapefile(merged_shapefile, shapefile_B_path)
        
        return f"Shapefiles in {projB_fk}/{scenB_fk} have been replaced with merged shapefiles."