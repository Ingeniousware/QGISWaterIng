# -*- coding: utf-8 -*-
from ..unitofwork.scenarioUnitOfWork import scenarioUnitOfWork
from ..watering_utils import WateringUtils

import os, json, requests, glob, uuid, shutil, processing

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
        # Ui elements
        self.initialize_repository()
        self.hide_ui_elements()
        self.set_buttons_and_checkboxes()
        
        #Variables 
        self.token = os.environ.get('TOKEN')
        self.online_projects_list = []
        self.scenarios_list = []
        self.current_project_fk = None
        self.current_scenario_fk = None
        self.response = None

    def initialize_repository(self):
        self.response = WateringUtils.requests_get("/api/v1/ProjectWaterNetworks")
        if not self.response:
            self.run_offline_procedures()
            
        self.set_online_projects_list()
        self.set_combo_boxes()
        
    def set_buttons_and_checkboxes(self):
        self.new_project_checkBox.clicked.connect(self.handle_new_tab_ui_elements)
        self.new_button.clicked.connect(self.create_new_scenario)
        self.load_button.clicked.connect(self.load_existing_scenario)
        self.new_projects_box.currentIndexChanged.connect(self.load_online_scenarios)
        
    def hide_ui_elements(self):
        self.handle_new_tab_ui_elements()
    
    def handle_new_tab_ui_elements(self):
        checked = self.new_project_checkBox.isChecked()
        self.new_project_label.setVisible(checked)
        self.new_project_name.setVisible(checked)
        self.new_projects_box.setVisible(not checked)
        self.new_source_project_label.setVisible(not checked)
    
    def create_new_scenario(self):
        ...
    
    def load_existing_scenario(self):
        ...
    
    def run_offline_procedures(self):
        ...
    
    def set_online_projects_list(self):
        self.online_projects_list = []

        for i in range(0, self.response.json()["total"]):
            self.online_projects_list.append((self.response.json()["data"][i]["name"],
                                       self.response.json()["data"][i]["serverKeyId"]))

    def load_online_scenarios(self):
        ...
        
    def set_online_projects_list(self):
        ...
        # self.online_projects_list = []

        # for i in range(0, self.response.json()["total"]):
        #     self.online_projects_list.append((self.response.json()["data"][i]["name"],
        #                                self.response.json()["data"][i]["serverKeyId"]))
            
    def set_combo_boxes(self):
        self.set_combo_box(self.new_projects_box)
        self.set_combo_box(self.load_projects_box)
        
    def set_combo_box(self, combo_box):
        combo_box.clear()
        ...
        # if self.online_projects_list:
        #     for project in self.online_projects_list:
        #             combo_box.addItem(project[0])