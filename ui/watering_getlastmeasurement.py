from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeatureRequest
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from PyQt5 import uic
import os
from ..watering_utils import WateringUtils
from enum import Enum

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_getlastmeasurement_dialog.ui'))

class ChannelState(Enum):
    DISCONNECTED = 0
    WARNING = (3, 4)
    CRITICAL = (5, 6, 7)

class WateringOnlineMeasurements(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(WateringOnlineMeasurements, self).__init__(parent)
        self.setupUi(self)
        self.ScenarioFK = WateringUtils.getScenarioId()
        self.ProjectFK = WateringUtils.getProjectId()
        self.normalSensors = []
        self.disconnectedSensors = []
        self.criticalSensors = []
        self.warningSensors = []
        self.token = os.environ.get('TOKEN')
        self.fetch_data()
    
    def fetch_data(self):
        url = f"/api/v1/MeasurementChannels"
        params = {'projectKeyId': "{}".format(self.ProjectFK)}

        self.currentData = []

        response = WateringUtils.requests_get(url, params)
        if not response:
            print('Error in request. See logs for details.')
            return

        if response.status_code != 200:
            print(f"Unexpected response status code: {response.status_code}")
            return
        
        data = response.json().get("data", [])
        self.data = data
        print(data)
        
        if data is not None: 
            self.update_table_widget(data)

    def update_table_widget(self, data):
        self.tv_getLastOnlineMeasurement.clear()
        self.tv_getLastOnlineMeasurement.setRowCount(0)

        headers = ["Sensor", "Channel State", "Data channel", "Last Value", "Last Changed"]

        self.tv_getLastOnlineMeasurement.setColumnCount(len(headers))
        self.tv_getLastOnlineMeasurement.setHorizontalHeaderLabels(headers)

        header = self.tv_getLastOnlineMeasurement.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        for item in data:
            self.add_table_row(item)

    def add_table_row(self, item):
        rowPosition = self.tv_getLastOnlineMeasurement.rowCount()
        self.tv_getLastOnlineMeasurement.insertRow(rowPosition)
        
        sensorId = item.get("sensorStationFK")
        sensorName = self.find_feature_by_sensor_name(sensorId)
        channelStateInt = item.get("channelState")
        channelState = self.convert_channel_state(channelStateInt)
        dataChannelName = item.get("name")
        lastValue = item.get("lastValue")
        lastChanged = item.get("lastChange")

        if channelStateInt == ChannelState.DISCONNECTED.value:
            self.disconnectedSensors.append(sensorId)
        elif channelStateInt in ChannelState.WARNING.value:
            self.warningSensors.append(sensorId)
        elif channelStateInt in ChannelState.CRITICAL.value:
            self.criticalSensors.append(sensorId)
        
        self.tv_getLastOnlineMeasurement.setItem(rowPosition, 0, QTableWidgetItem(sensorName))
        self.tv_getLastOnlineMeasurement.setItem(rowPosition, 1, QTableWidgetItem(channelState))
        self.tv_getLastOnlineMeasurement.setItem(rowPosition, 2, QTableWidgetItem(dataChannelName))
        self.tv_getLastOnlineMeasurement.setItem(rowPosition, 3, QTableWidgetItem(lastValue))
        self.tv_getLastOnlineMeasurement.setItem(rowPosition, 4, QTableWidgetItem(lastChanged))
    
    def convert_channel_state(self, channelState):
        channel_state_mapping = {
            0: "Disconnected",
            2: "Transmitting OK",
            3: "Transmission Stopped",
            4: "Value Warning",
            5: "Value Anomaly",
            6: "Value Critical",
            7: "Value Outlier"
        }
        return channel_state_mapping.get(channelState, "Unknown State")
    
    def find_feature_by_sensor_name(self, sensorId):
        layer = QgsProject.instance().mapLayersByName("watering_sensors")[0]
        
        if not layer:
            print("Layer not found.")
            return None

        request = QgsFeatureRequest()
        request.setFilterExpression(f'"id" = \'{sensorId}\'') 

        # Search for the feature
        features = layer.getFeatures(request)
        
        for feature in features:
            # Return the feature if found
            return feature['Name']
        
        # If no feature is found, return None
        print(f"No feature found with sensor name: {sensorId}")
        return None
    