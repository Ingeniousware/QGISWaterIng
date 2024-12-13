from qgis.PyQt import uic, QtWidgets
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsExpression,
    QgsFeatureRequest,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsMarkerSymbol,
    QgsSvgMarkerSymbolLayer,
)
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import uic
import os
from ..watering_utils import WateringUtils
from enum import Enum

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_getlastmeasurement_dialog.ui"))


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
        self.token = os.environ.get("TOKEN")
        self.fetch_data()

    def fetch_data(self):
        url = f"/api/v1/MeasurementChannels"
        params = {"projectKeyId": "{}".format(self.ProjectFK)}

        self.currentData = []

        response = WateringUtils.requests_get(url, params)
        if not response:
            print("Error in request. See logs for details.")
            return

        if response.status_code != 200:
            print(f"Unexpected response status code: {response.status_code}")
            return

        data = response.json().get("data", [])
        self.data = data

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

        self.update_sensor_symbols()

    def add_table_row(self, item):
        rowPosition = self.tv_getLastOnlineMeasurement.rowCount()
        self.tv_getLastOnlineMeasurement.insertRow(rowPosition)

        sensorId = str(item.get("sensorStationFK"))
        sensorName = str(self.find_feature_by_sensor_name(sensorId))
        channelStateInt = item.get("channelState")
        channelState = str(self.convert_channel_state(channelStateInt))
        dataChannelName = str(item.get("name"))
        lastValue = str(item.get("lastValue"))
        lastChanged = str(item.get("lastChange"))

        if channelStateInt == ChannelState.DISCONNECTED.value:
            self.disconnectedSensors.append(sensorId)
        elif channelStateInt in ChannelState.WARNING.value:
            self.warningSensors.append(sensorId)
        elif channelStateInt in ChannelState.CRITICAL.value:
            self.criticalSensors.append(sensorId)
        else:
            self.normalSensors.append(sensorId)

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
            7: "Value Outlier",
        }
        return channel_state_mapping.get(channelState, "Unknown State")

    def find_feature_by_sensor_name(self, sensorId):
        layer = QgsProject.instance().mapLayersByName("watering_sensors")[0]

        if not layer:
            print("Layer not found.")
            return None

        request = QgsFeatureRequest()
        request.setFilterExpression(f"\"ID\" = '{sensorId}'")

        features = layer.getFeatures(request)

        for feature in features:
            return feature["Name"]

        print(f"No feature found with sensor name: {sensorId}")
        return ""

    def update_sensor_symbols(self):
        if not (self.normalSensors or self.criticalSensors or self.warningSensors or self.disconnectedSensors):
            return

        selectedLayer = QgsProject.instance().mapLayersByName("watering_sensors")
        if not selectedLayer:
            return

        selectedLayer = selectedLayer[0]
        expression_parts = []

        status_order = ["disconnected", "warning", "critical", "normal"]
        status_values = {"disconnected": 1, "warning": 2, "critical": 3, "normal": 4}
        sensor_lists = {
            "disconnected": [str(sid) for sid in self.disconnectedSensors if sid],
            "warning": [str(sid) for sid in self.warningSensors if sid],
            "critical": [str(sid) for sid in self.criticalSensors if sid],
            "normal": [str(sid) for sid in self.normalSensors if sid],
        }

        for status in status_order:
            sensor_list = sensor_lists[status]
            if sensor_list:
                expression_parts.append(
                    f'WHEN "ID" IN ({", ".join(map(repr, sensor_list))}) THEN {status_values[status]}'
                )

        if not expression_parts:
            return

        expression = "CASE\n" + "\n".join(expression_parts) + "\nELSE 4\nEND"
        status_styles = {
            1: {
                "name": ":/plugins/QGISPlugin_WaterIng/images/Icon_pressureSensor_GT_Disconnected.svg",
                "label": "Disconnected",
            },
            2: {"name": ":/plugins/QGISPlugin_WaterIng/images/Icon_pressureSensor_GT_Warning.svg", "label": "Warning"},
            3: {
                "name": ":/plugins/QGISPlugin_WaterIng/images/Icon_pressureSensor_GT_Critical.svg",
                "label": "Critical",
            },
            4: {"name": ":/plugins/QGISPlugin_WaterIng/images/Icon_pressureSensor_GT.svg", "label": "Normal"},
        }

        categories = []
        for value, style in status_styles.items():
            symbol = QgsMarkerSymbol.createSimple({})
            svgStyle = {"name": style["name"], "size": "10"}
            symbol_layer = QgsSvgMarkerSymbolLayer.create(svgStyle)
            if symbol_layer is not None:
                symbol.changeSymbolLayer(0, symbol_layer)
            category = QgsRendererCategory(value, symbol, style["label"])
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer("ID", categories)
        renderer.setClassAttribute(expression)

        if renderer is not None:
            selectedLayer.setRenderer(renderer)

        selectedLayer.triggerRepaint()
