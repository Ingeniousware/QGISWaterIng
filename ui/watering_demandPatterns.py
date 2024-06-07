# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem
from ..watering_utils import WateringUtils

import os
import requests
import time
import json


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_demandPatterns.ui'))

class WateringDemandPatterns(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,iface,parent=None):
        """Constructor."""
        super(WateringDemandPatterns, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.token = os.environ.get('TOKEN')
        self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        self.serverKeyId = None
        self.ownerKeyId = None 
        self.loadDemandPatterns.clicked.connect(self.populate_table)
        self.uploadPatterns.clicked.connect(self.read_table_data)
        self.createNewButton.clicked.connect(self.create_pattern)
        self.newValue.setEnabled(False)
        self.removeValue.setEnabled(False)
        self.newValue.clicked.connect(lambda: self.add_or_delete_value(0))
        self.removeValue.clicked.connect(lambda: self.add_or_delete_value(1))
        self.createCheckBox.clicked.connect(self.new_pattern_checkBox)
        self.deletePattern.clicked.connect(self.delete_pattern)
        self.getValues.clicked.connect(self.get_selected_rows_values)
        self.comboBox.currentIndexChanged.connect(self.current_values_selected_comboBox)
        self.data = []
        self.fetch_data()
        self.pattern_list = []
        self.createPatternLavel.hide()
        self.newPatternLine.hide()
        self.createNewButton.hide()

    def fetch_data(self):
        time.sleep(.1)
        url = f"{WateringUtils.getServerUrl()}/api/v1/Patterns/?&scenarioKeyId={self.ScenarioFK}"
        headers = {'Authorization': "Bearer {}".format(self.token)}
        self.currentData = []
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", [])
            self.data = data
            self.comboBox.clear()
            for item in data:
                scenarioName = item.get("name")
                keyId = item.get("serverKeyId")
                description = item.get("description")
                owners = item.get("ownerKeyId")
                
                # Add scenario name to the combo box
                self.comboBox.addItem(scenarioName)

                self.currentData.append({
                    "name": scenarioName,
                    "serverKeyId": keyId,
                    "description": description,
                    "ownerKeyId": owners
                })
                #print(f"Name: {scenarioName}, KeyId: {keyId}, Description: {description}, Owners: {owners}")
        else:
            print(f"Failed to fetch data: {response.status_code}")

    def current_values_selected_comboBox(self):
        time.sleep(1)
        scenario_name = self.comboBox.currentText()
        scenario_details = next((item for item in self.currentData if item["name"] == scenario_name), None)
        if scenario_details:
            self.serverKeyId = scenario_details["serverKeyId"]
            self.ownerKeyId = scenario_details["ownerKeyId"]
            print(self.serverKeyId)
            print(self.ownerKeyId)
        else:
            print(f"No details found for {scenario_name}")

    def create_pattern(self):
        url = WateringUtils.getServerUrl() + "/api/v1/Patterns"
        data = {
                "serverKeyId": "",
                "ownerKeyId": self.ScenarioFK,
                "name": self.newPatternLine.text(),
                "description": "",
                "points": []
                }
        headers = {'Authorization': "Bearer {}".format(self.token)}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print("Pattern created successfully.")
        else:
            print("Failed to create pattern. Status code:", response.status_code)
        self.upload_new_data_to_server(['', '', 0, 0, ''])
        self.fetch_data()
        self.createPatternLavel.hide()
        self.newPatternLine.hide()
        self.createNewButton.hide()

    def add_or_delete_value(self, case):
        if case == 0:
            current_row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(current_row_count)
        elif case == 1:
            selected_rows = set(index.row() for index in self.tableWidget.selectedIndexes())
            for row in sorted(selected_rows, reverse=True):
                self.tableWidget.removeRow(row)

    def new_pattern_checkBox(self):
        if self.createCheckBox.isChecked():
            self.createPatternLavel.show()
            self.newPatternLine.show()
            self.createNewButton.show()
        else:
            self.createPatternLavel.hide()
            self.newPatternLine.hide()
            self.createNewButton.hide()

    def populate_table(self):
        section = None
        for item in self.data:
            if item['name'] == self.comboBox.currentText():
                section = item
                break
        if not section:
            return
        self.tableWidget.clearContents()
    
        points = section.get('points', [])
        if not points:
            return
        # Assuming section is a dictionary, not a list of dictionaries
        self.tableWidget.setRowCount(len(section['points']))  # Set row count based on the length of points list
        self.tableWidget.setColumnCount(len(section['points'][0].keys()))  # Set column count based on keys of the first point
        self.tableWidget.setHorizontalHeaderLabels(["ServerKeyId", "PatternFK", "Minute", "Value", "OwnerKeyId"])  
        self.tableWidget.setColumnHidden(0,True)
        self.tableWidget.setColumnHidden(1,True)
        self.tableWidget.setColumnHidden(4,True)
        # Populate the table with points data
        for row_idx, point in enumerate(section['points']):
            for col_idx, value in enumerate(point.values()):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.newValue.setEnabled(True)
        self.removeValue.setEnabled(True)

    def read_table_data(self):
        data = []
        for row in range(self.tableWidget.rowCount()):
            rowData = []
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    rowData.append(item.text())
                else:
                    rowData.append(None)
            data.append(rowData)
            self.upload_new_data_to_server(rowData)
        return data

    def upload_new_data_to_server(self, rowdata):
        serverKeyId, patternFK, timePattern, value, ownerKeyId = rowdata
        url = WateringUtils.getServerUrl() + "/api/v1/Patterns/points"
        headers = {'Authorization': "Bearer {}".format(self.token)}
        data_json = {
                    "serverKeyId": "",
                    "patternFK": self.serverKeyId,
                    "timePattern": timePattern,
                    "value": value,
                    "ownerKeyId": self.ownerKeyId
                    }
                
        response = requests.post(url, json=data_json, headers=headers)
        if response.status_code == 200:
            print("Sent")
    
    def delete_pattern(self):
        url = WateringUtils.getServerUrl() + "/api/v1/Patterns/" + self.serverKeyId
        headers = {'Authorization': "Bearer {}".format(self.token)}
        print(url)
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()  # Raise an exception for unsuccessful status codes
            self.fetch_data()
        except requests.exceptions.RequestException as e:
            # Handle network errors, server errors, etc.
            print(f"Error deleting pattern: {e}")

    def get_selected_rows_values(self):
        selected_rows = set(index.row() for index in self.tableWidget.selectedIndexes())
        rows_data = []
        for row in selected_rows:
            row_data = []
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            rows_data.append(row_data)
        print(rows_data)
        return rows_data
    
    def delete_selection_data(self):

        ...
