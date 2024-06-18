# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5 import uic
import os
from ..watering_utils import WateringUtils
import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_pumpModels_dialog.ui'))

class WateringPumpModels(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(WateringPumpModels, self).__init__(parent)
        self.setupUi(self)
        self.ScenarioFK = WateringUtils.getScenarioId()
        self.token = os.environ.get('TOKEN')

        self.initUI()
        self.testButton.clicked.connect(self.addNewPump)

    def loadPumpModels(self):
        url = f'/api/v1/PumpModel/getlist?&scenarioFK={self.ScenarioFK}'
        response = WateringUtils.requests_get(url, None)
        data = response.json()
        return data

    def initUI(self):
        layout = QVBoxLayout()
        data = self.loadPumpModels()
        
        self.pump_widgets = []
        
        for pump in data['data']:
            pump_layout = QHBoxLayout()
            
            pump_name_label = QLabel(pump['name'])
            pump_layout.addWidget(pump_name_label)
            
            edit_button = QPushButton('Edit')
            edit_button.clicked.connect(self.create_edit_handler(pump))
            pump_layout.addWidget(edit_button)
            
            delete_button = QPushButton('Delete')
            delete_button.clicked.connect(self.create_delete_handler(pump))
            pump_layout.addWidget(delete_button)
            
            layout.addLayout(pump_layout)
            
            self.pump_widgets.append({
                'pump': pump,
                'layout': pump_layout,
                'edit_button': edit_button,
                'delete_button': delete_button,
                'pump_name_label': pump_name_label
            })
        
        container_widget = QWidget()
        container_widget.setLayout(layout)
        self.scrollArea.setWidget(container_widget)
        self.setWindowTitle('Pump Models')
        self.show()

    def create_edit_handler(self, pump):
        def handler():
            self.edit_pump(pump)
        return handler

    def create_delete_handler(self, pump):
        def handler():
            self.delete_pump(pump)
        return handler
    
    def edit_pump(self, pump):
        pump_widget = None
        
        for widget in self.pump_widgets:
            if widget['pump'] == pump:
                pump_widget = widget
                break
        
        if not pump_widget:
            return
        
        edit_button = pump_widget['edit_button']
        delete_button = pump_widget['delete_button']
        pump_name_label = pump_widget['pump_name_label']

        # Hide existing widgets
        edit_button.hide()
        delete_button.hide()
        pump_name_label.hide()
        
        # Remove existing widgets
        pump_widget['layout'].removeWidget(edit_button)
        pump_widget['layout'].removeWidget(delete_button)
        pump_widget['layout'].removeWidget(pump_name_label)
        
        # Create line edit and save/cancel buttons
        pump_name_edit = QtWidgets.QLineEdit(pump['name'])
        pump_widget['layout'].addWidget(pump_name_edit)
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda: self.save_pump(pump, pump_name_edit))
        pump_widget['layout'].addWidget(save_button)
        
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(lambda: self.cancel_edit(pump, pump_name_edit))
        pump_widget['layout'].addWidget(cancel_button)
        
        # Update widget dictionary
        pump_widget['pump_name_edit'] = pump_name_edit
        pump_widget['save_button'] = save_button
        pump_widget['cancel_button'] = cancel_button
        
        # Update UI
        self.scrollArea.update()

    def save_pump(self, pump, pump_name_edit):
        new_name = pump_name_edit.text()
        print(f"Saving changes for pump: {pump['name']} to {new_name}")
        
        # Perform save operation (update API, database, etc.)
        # Example: You will need to implement the actual update logic here.
        # Once updated, update pump name label and reset UI
        pump['name'] = new_name
        self.initUI()

    def cancel_edit(self, pump, pump_name_edit):
        print(f"Cancelling edit for pump: {pump['name']}")
        
        # Remove edit widgets and restore original view
        self.initUI()

    def create_pump_handler(self, pump, handler):
        return lambda: handler(pump)

    def delete_pump(self, pump):
        print(f"Deleting pump: {pump['name']}")
        url = f"{WateringUtils.getServerUrl()}/api/v1/PumpModel/{pump['serverKeyId']}"
        headers = {'Authorization': "Bearer {}".format(self.token)}
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("Pump deleted successfully.")
            self.initUI()

    def addNewPump(self):
        print("Its Working")
        #The json to add a new pump check with Idel
