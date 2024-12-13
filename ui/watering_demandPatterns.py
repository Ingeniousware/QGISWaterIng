# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QApplication, QMessageBox
from ..watering_utils import WateringUtils

import os
import requests
import sys
from requests.exceptions import SSLError, ConnectionError
from time import sleep


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_demandPatterns.ui"))


class WateringDemandPatterns(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(WateringDemandPatterns, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.token = os.environ.get("TOKEN")
        self.ScenarioFK = QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]
        self.serverKeyId = None
        self.ownerKeyId = None
        self.data = []
        self.fetch_data()
        self.setup_table()
        self.loadDemandPatterns.clicked.connect(self.populate_table)
        self.uploadPatterns.clicked.connect(self.read_table_data)
        self.createNewButton.clicked.connect(self.create_pattern)
        self.newValue.setEnabled(False)
        self.removeValue.setEnabled(False)
        self.newValue.clicked.connect(lambda: self.add_or_delete_value(0))
        self.removeValue.clicked.connect(lambda: self.add_or_delete_value(1))
        self.createCheckBox.clicked.connect(self.new_pattern_checkBox)
        self.deletePattern.clicked.connect(self.delete_pattern)
        self.deleteValues.clicked.connect(self.get_selected_rows_values)
        self.comboBox.currentIndexChanged.connect(self.current_values_selected_comboBox)
        self.createPatternLavel.hide()
        self.newPatternLine.hide()
        self.createNewButton.hide()

    def setup_table(self):
        # Assuming self.tableWidget is already defined and initialized
        self.tableWidget.setRowCount(1)  # Initialize with one empty row
        self.tableWidget.setColumnCount(5)  # Set the number of columns
        self.tableWidget.setHorizontalHeaderLabels(["ServerKeyId", "PatternFK", "Minute", "Value", "OwnerKeyId"])
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(1, True)
        self.tableWidget.setColumnHidden(4, True)
        # Optional: Initialize the first row with empty items
        for col_idx in range(5):
            self.tableWidget.setItem(0, col_idx, QTableWidgetItem(""))

    def fetch_data(self):
        url = f"/api/v1/Patterns/?&scenarioKeyId={self.ScenarioFK}"
        self.currentData = []
        response = WateringUtils.requests_get(url, None)
        if response == False:
            print("Error")
        elif response.status_code == 200:
            data = response.json().get("data", [])
            self.data = data
            self.comboBox.clear()
            # Add default value to the combo box
            default_value = "Select a pattern"
            self.comboBox.addItem(default_value)
            self.comboBox.setCurrentIndex(0)
            for item in data:
                scenarioName = item.get("name")
                keyId = item.get("serverKeyId")
                description = item.get("description")
                owners = item.get("ownerKeyId")

                # Add scenario name to the combo box
                self.comboBox.addItem(scenarioName)

                self.currentData.append(
                    {"name": scenarioName, "serverKeyId": keyId, "description": description, "ownerKeyId": owners}
                )
        else:
            print(f"Failed to fetch data: {response.status_code}")

    def current_values_selected_comboBox(self):
        scenario_name = self.comboBox.currentText()
        scenario_details = next((item for item in self.currentData if item["name"] == scenario_name), None)
        if scenario_details:
            self.serverKeyId = scenario_details["serverKeyId"]
            self.ownerKeyId = scenario_details["ownerKeyId"]
            print(self.serverKeyId)
            print(self.ownerKeyId)
        else:
            print(f"No details found for {scenario_name}")
        self.tableWidget.clearContents()

    def create_pattern(self):
        url = "/api/v1/Patterns"
        data = {
            "serverKeyId": "",
            "ownerKeyId": self.ScenarioFK,
            "name": self.newPatternLine.text(),
            "description": "",
            "points": [],
        }
        response = WateringUtils.requests_post(url, json=data)
        if response == False:
            print("Failed to create pattern.")
        elif response.status_code == 200:
            print("Pattern created successfully.")

        self.fetch_data()
        self.createPatternLavel.hide()
        self.newPatternLine.hide()
        self.createNewButton.hide()

    def add_or_delete_value(self, case):
        if case == 0:  # ADD
            current_row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(current_row_count)
        elif case == 1:  # DELETE
            selected_rows = set(index.row() for index in self.tableWidget.selectedIndexes())

            if not selected_rows:
                last_row = self.tableWidget.rowCount() - 1
                if last_row >= 0:
                    has_values = any(
                        self.tableWidget.item(last_row, column) is not None
                        and self.tableWidget.item(last_row, column).text() != ""
                        for column in range(self.tableWidget.columnCount())
                    )
                    if not has_values:
                        self.tableWidget.removeRow(last_row)
            else:
                for row in sorted(selected_rows, reverse=True):
                    # Check if the row has any values
                    has_values = any(
                        self.tableWidget.item(row, column) is not None
                        and self.tableWidget.item(row, column).text() != ""
                        for column in range(self.tableWidget.columnCount())
                    )
                    if not has_values:
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
        self.newValue.setEnabled(True)
        self.removeValue.setEnabled(True)

        section = None
        for item in self.data:
            if item["name"] == self.comboBox.currentText():
                section = item
                break
        if not section:
            return
        self.tableWidget.clearContents()

        points = section.get("points", [])
        if not points:
            return
        # Assuming section is a dictionary, not a list of dictionaries
        self.tableWidget.setRowCount(len(section["points"]))  # Set row count based on the length of points list
        self.tableWidget.setColumnCount(
            len(section["points"][0].keys())
        )  # Set column count based on keys of the first point
        self.tableWidget.setHorizontalHeaderLabels(["ServerKeyId", "PatternFK", "Minute", "Value", "OwnerKeyId"])
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(1, True)
        self.tableWidget.setColumnHidden(4, True)
        # Populate the table with points data
        for row_idx, point in enumerate(section["points"]):
            for col_idx, value in enumerate(point.values()):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

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
            response = self.upload_new_data_to_server(rowData)
        if response.status_code == 200:
            QMessageBox.information(None, "Success", "The new values were updated successfully.")
            self.close()
        return data

    def upload_new_data_to_server(self, rowdata):
        serverKeyId, patternFK, timePattern, value, ownerKeyId = rowdata
        if not timePattern or not value:
            print("Incomplete data, cannot upload.")
            return
        url = WateringUtils.getServerUrl() + "/api/v1/Patterns/points"
        headers = {"Authorization": "Bearer {}".format(self.token)}
        data_json = {
            "serverKeyId": "",
            "patternFK": self.serverKeyId,
            "timePattern": timePattern,
            "value": value,
            "ownerKeyId": self.ownerKeyId,
        }
        print(data_json)
        response = self.make_post_request(url, data_json, headers)
        return response

    def delete_pattern(self):
        url = f"{WateringUtils.getServerUrl()}/api/v1/Patterns/{self.serverKeyId}"
        headers = {"Authorization": "Bearer {}".format(self.token)}
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            self.fetch_data()
        except requests.exceptions.RequestException as e:
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
                    row_data.append("")
            self.delete_selection_data(row_data)
            rows_data.append(row_data)
        print(rows_data)

        selected_rows = set(index.row() for index in self.tableWidget.selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.tableWidget.removeRow(row)
        return rows_data

    def delete_selection_data(self, pointToDelete):
        if not pointToDelete:
            print("No point selected for deletion.")
            return
        pointId = pointToDelete[0]
        url = f"{WateringUtils.getServerUrl()}/api/v1/Patterns/points/{pointId}"
        headers = {"Authorization": "Bearer {}".format(self.token)}
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error deleting point: {e}")

    def make_post_request(self, url, data, headers=None, max_retries=5, backoff_factor=0.3):
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()  # Raise HTTPError for bad responses
                return response  # Assuming you want to return the JSON response
            except SSLError as ssl_err:
                print(f"SSLError occurred: {ssl_err}")
            except ConnectionError as conn_err:
                print(f"ConnectionError occurred: {conn_err}")
            except requests.HTTPError as http_err:
                print(f"HTTPError occurred: {http_err}")
            except requests.RequestException as req_err:
                print(f"RequestException occurred: {req_err}")

            sleep_time = backoff_factor * (2**attempt)
            print(f"Retrying in {sleep_time} seconds...")
            sleep(sleep_time)

        raise Exception("Max retries exceeded")
