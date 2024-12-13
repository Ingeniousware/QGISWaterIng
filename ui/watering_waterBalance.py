from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from PyQt5 import uic
import os
from ..watering_utils import WateringUtils
import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_waterBalance_dialog.ui"))


class WateringWaterBalance(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(WateringWaterBalance, self).__init__(parent)
        self.setupUi(self)
        self.ScenarioFK = WateringUtils.getScenarioId()
        self.ProjectFK = WateringUtils.getProjectId()
        self.token = os.environ.get("TOKEN")
        self.fetch_data()

    def fetch_data(self):
        url = f"/api/v1/WaterBalanceCalculationRequest?&projectFK={self.ProjectFK}"
        self.currentData = []

        response = WateringUtils.requests_get(url, None)
        if not response:
            print("Error in request. See logs for details.")
            return

        if response.status_code != 200:
            print(f"Unexpected response status code: {response.status_code}")
            return
        data = response.json().get("data", [])
        self.data = data

        self.update_table_widget(data, 0)

    def update_table_widget(self, data, case):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)

        headers = []
        if case == 0:
            headers = ["Requested Date Time", "Initial Date Time", "End Date Time", "Description", "Open", "Delete"]
        elif case == 1:
            headers = [
                "Name",
                "Water Meter Key",
                "Read Before Period",
                "Read Start Period",
                "Read End Period",
                "Read After Period",
                "Consumption Estimated",
            ]

        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        add_row_method = self.add_table_row if case == 0 else self.add_table_row2
        for item in data:
            add_row_method(item)

        self.tableWidget.resizeColumnsToContents()

    def create_button_rows(self, name):
        # Create a QPushButton and set its properties
        openButton = QPushButton(name)

        # Create a QWidget to place the button inside it
        buttonWidget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(openButton)
        layout.setContentsMargins(0, 0, 0, 0)
        buttonWidget.setLayout(layout)

        return buttonWidget, openButton

    def add_table_row(self, item):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        requestedDateTime = item.get("requestedDateTime")
        initialDateTime = item.get("periodInitialDateTime")
        endDateTime = item.get("periodEndDateTime")
        description = item.get("description")
        keyId = item.get("serverKeyId")

        self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(requestedDateTime))
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(initialDateTime))
        self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(endDateTime))
        self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(description))

        buttonWidgetOpen, open = self.create_button_rows("Open")
        buttonWidgetDelete, delete = self.create_button_rows("Delete")
        # Add the QWidget to the table at column 4
        self.tableWidget.setCellWidget(rowPosition, 4, buttonWidgetOpen)
        self.tableWidget.setCellWidget(rowPosition, 5, buttonWidgetDelete)

        self.currentData.append(
            {
                "serverKeyId": keyId,
                "requestedDateTime": requestedDateTime,
                "periodInitialDateTime": initialDateTime,
                "periodEndDateTime": endDateTime,
                "description": description,
            }
        )

        # Connect the button click event to a method
        open.clicked.connect(lambda: self.open_item(keyId))
        delete.clicked.connect(lambda: self.delete_item(keyId))

    def open_item(self, keyId):
        url = f"/api/v1/WaterConsumption/getfromrequest?&projectKeyId={self.ProjectFK}&calculationRequestFK={keyId}"
        response = WateringUtils.requests_get(url, params=None)
        data = response.json().get("data", [])
        self.update_table_widget(data, 1)
        print(f"Open button clicked for item with serverKeyId: {keyId}")

    def delete_item(self, keyId):
        url = f"/api/v1/WaterBalanceCalculationRequest/{keyId}"
        response = WateringUtils.requests_delete(url)
        self.fetch_data()
        print(f"Delete button clicked for item with serverKeyId: {keyId}")

    def add_table_row2(self, item):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        name = item.get("name")
        waterMeterKey = item.get("waterMeterKey")
        readBeforePeriodDateTime = item.get("readBeforePeriodDateTime")
        readStartPeriodDateTime = item.get("readStartPeriodDateTime")
        readEndPeriodDateTime = item.get("readEndPeriodDateTime")
        readAfterPeriodDateTime = item.get("readAfterPeriodDateTime")
        consumptionEstimated = item.get("consumptionEstimated")

        if isinstance(waterMeterKey, int):
            waterMeterKey = str(waterMeterKey)
        if isinstance(consumptionEstimated, float):
            consumptionEstimated = str(consumptionEstimated)

        self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(name))
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(waterMeterKey))
        self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(readBeforePeriodDateTime))
        self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(readStartPeriodDateTime))
        self.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(readEndPeriodDateTime))
        self.tableWidget.setItem(rowPosition, 5, QTableWidgetItem(readAfterPeriodDateTime))
        self.tableWidget.setItem(rowPosition, 6, QTableWidgetItem(consumptionEstimated))
