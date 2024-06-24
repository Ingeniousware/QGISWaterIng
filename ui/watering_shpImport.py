# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QInputDialog, QLineEdit
import os
import json
import uuid
import datetime
import time
from ..watering_utils import WateringUtils
import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_shpImport_dialog.ui'))


class WateringShpImport(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self,iface,parent=None):
        """Constructor."""
        super(WateringShpImport, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.TabWidget.setTabVisible(0, False)
        self.TabWidget.setTabVisible(1, False)
        self.TabWidget.setTabVisible(2, False)
        self.TabWidget.hide()
        self.LayerTypeCBox.setPlaceholderText("Please select the layer type you wish to import")
        self.LayerTypeCBox.addItem("Demand Nodes")
        self.LayerTypeCBox.addItem("Water DMA")
        self.LayerTypeCBox.addItem("Tanks")
        self.LayerTypeCBox.addItem("Sensors")
        self.LayerTypeCBox.currentIndexChanged.connect(self.checkUserControlState)
        self.uploadShpFile.setEnabled(False)
        self.loadLayerButton.clicked.connect(self.addSelected_Layer)
        self.uploadShpFile.clicked.connect(self.get_cBox_index)
        self.token = os.environ.get('TOKEN')
        self.UrlPost = None
        

    def addSelected_Layer(self):
        self.file_path = self.newSHPDirectory.filePath()
        if self.file_path.lower().endswith('.shp'):
            vlayer = QgsVectorLayer(self.file_path, "New Layer", "ogr")
            if not vlayer.isValid():
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Warning)
                message_box.setWindowTitle("Error")
                message_box.setText("Layer failed to load!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec_()
            else:
                QgsProject.instance().addMapLayer(vlayer)
                self.TabWidget.show()
                self.LayerTypeCBox.setEnabled(False)
                self.attribute_matcher()
                self.uploadShpFile.setEnabled(True)
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Error")
            message_box.setText("Selected file is not a shapefile (.shp)")
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()

    def attribute_matcher(self):
        layer = QgsProject.instance().mapLayersByName("New Layer")[0]
        fields = layer.fields()
        index = self.LayerTypeCBox.currentIndex()
        if index == 0:  # Demand Nodes
            comboBoxes = [
                (self.nameComboBox),
                (self.descriptionComboBox),
                (self.zComboBox),
                (self.demandComboBox),
                (self.emitterComboBox)
            ]
        elif index == 1: # Water DMA
            comboBoxes = [
                (self.nameDMAcomboBox),
                (self.descriptionDMAcomboBox)
            ]
        elif index == 2: # Tanks
            comboBoxes = [
                (self.nameTankscomboBox),
                (self.descriptionTankscomboBox),
                (self.zTankscomboBox),
                (self.initTankscomboBox),
                (self.minTankscomboBox),
                (self.maxTankscomboBox),
                (self.minVTankscomboBox),
                (self.diameterTankscomboBox)
            ]
        elif index == 3: # Water Sensors
            comboBoxes = [
                (self.sensorNameCBox),
                (self.sensorDescriptCBox),
                (self.sensorZCBox)
            ]
        else:
            return
        for cBox in comboBoxes:
            cBox.clear()
            cBox.addItem("No match")
            for field in fields:
                cBox.addItem(field.name())

    def checkUserControlState(self):
        index = self.LayerTypeCBox.currentIndex()
        for i in range(self.TabWidget.count()):
            self.TabWidget.setTabVisible(i, False)
        if index == 0:
            self.TabWidget.setTabVisible(0, True)
        elif index == 1:
            self.TabWidget.setTabVisible(1, True)
        elif index == 2:
            self.TabWidget.setTabVisible(2, True)
        elif index == 3:
            self.TabWidget.setTabVisible(3, True)

    def get_cBox_index(self):
        cBox_index = self.LayerTypeCBox.currentIndex()
        if cBox_index == 0:
            self.UrlPost = WateringUtils.getServerUrl() + "/api/v1/DemandNode"
            print("The layer imported is of demand nodes")
            self.convert_node_to_json("New Layer")
        elif cBox_index == 1: 
            self.UrlPost = WateringUtils.getServerUrl() + "/api/v1/WaterDMA/withcoordinates"
            print("The layer imported is of water DMA")
            self.convert_polygon_to_json("New Layer")
        elif cBox_index == 2: 
            self.UrlPost = WateringUtils.getServerUrl() + "/api/v1/TankNode"
            print("The layer imported is of Tanks")
            self.convert_tank_to_json("New Layer")
        elif cBox_index == 3: 
            self.UrlPost = WateringUtils.getServerUrl() + "/api/v1/SensorStation"
            print("The layer imported is of Sensors")
            self.convert_sensor_to_json("New Layer")
        self.close()

    def convert_polygon_to_json(self, layer_name):
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        features = []

        for feature in layer.getFeatures():
            geom = feature.geometry()
            polygon = geom.asMultiPolygon()
            vertices = []
            n = len(polygon[0])
            for i in range(n):
                coordinateList = polygon[0][i]
                for point in coordinateList:
                    vertices.append({
                        "vertexFK": str(uuid.uuid4()),
                        "lng": point.x(),
                        "lat": point.y(),
                        "order": 0
                    })

            server_key_id = str(uuid.uuid4())
            fk_scenario = WateringUtils.getScenarioId() 
            ###Optimize later
            if self.nameDMAcomboBox.currentText() == "No match":
                name = "Demand Node"
            else:
                name = feature.attribute(self.nameDMAcomboBox.currentText())
                
            if self.descriptionDMAcomboBox.currentText() == "No match":
                description = ""
            else:
                description = feature.attribute(self.descriptionDMAcomboBox.currentText())
            ##### 
            sector_index = 0
            element_count = 0
            total_demand = 0

            print("Name:", name)
            print("Description:", description)

            feature_json = {
                "serverKeyId": server_key_id,
                "fkScenario": fk_scenario,
                "name": name,
                "description": description,
                "sectorIndex": sector_index,
                "elementCount": element_count,
                "totalDemand": total_demand,
                "vertices": vertices
            }
            self.post_to_server(feature_json, name)
            #print(feature_json)
            features.append(feature_json)

        QgsProject.instance().removeMapLayer(layer)
        return features
    
    def convert_node_to_json(self, layer_name):
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        features = []
        # Define the source and destination coordinate reference systems
        crs_source = layer.crs()
        crs_destination = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84
        transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())

        for feature in layer.getFeatures():
            geom = feature.geometry()
            point = geom.asPoint()
            transformed_point = transform.transform(point)

            server_key_id = str(uuid.uuid4())
            scenario_fk = WateringUtils.getScenarioId()

            ###Optimize later
            if self.nameComboBox.currentText() == "No match":
                name = "Demand Node"
            else:
                name = feature.attribute(self.nameComboBox.currentText())
                
            if self.descriptionComboBox.currentText() == "No match":
                description = ""
            else:
                description = feature.attribute(self.descriptionComboBox.currentText())

            if self.zComboBox.currentText() == "No match":
                z = 0
            else:
                z = feature.attribute(self.zComboBox.currentText())
            if self.demandComboBox.currentText() == "No match":
                baseDemand = 0
            else:
                baseDemand = feature.attribute(self.demandComboBox.currentText())
            if self.emitterComboBox.currentText() == "No match":
                emitterCoefficient = 0
            else:
                emitterCoefficient = feature.attribute(self.emitterComboBox.currentText())
            ####

            feature_json = {
                "serverKeyId": server_key_id,
                "scenarioFK": scenario_fk,
                "name": name,
                "description": description,
                "lng": transformed_point.x(),
                "lat": transformed_point.y(),
                "z": z,
                "baseDemand": baseDemand,
                "emitterCoeff": emitterCoefficient,
                "removed": False
            }
            self.post_to_server(feature_json, name)
            #print(feature_json)
            features.append(feature_json)
        print(features)
        QgsProject.instance().removeMapLayer(layer)
        return features
    
    def convert_tank_to_json(self, layer_name):
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        features = []
        # Define the source and destination coordinate reference systems
        crs_source = layer.crs()
        crs_destination = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84
        transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())

        for feature in layer.getFeatures():
            geom = feature.geometry()
            point = geom.asPoint()
            transformed_point = transform.transform(point)

            server_key_id = str(uuid.uuid4())
            scenario_fk = str(uuid.uuid4())

            name = feature.attribute(self.nameTankscomboBox.currentText()) if self.nameTankscomboBox.currentText() != "No match" else "string"
            description = feature.attribute(self.descriptionTankscomboBox.currentText()) if self.descriptionTankscomboBox.currentText() != "No match" else "string"
            z = feature.attribute(self.zTankscomboBox.currentText()) if self.zTankscomboBox.currentText() != "No match" else 0
            initialLevel = feature.attribute(self.initTankscomboBox()) if self.initTankscomboBox() != "No match" else 0
            minimumLevel = feature.attribute(self.minTankscomboBox()) if self.minTankscomboBox() != "No match" else 0
            maximumLevel = feature.attribute(self.maxTankscomboBox()) if self.maxTankscomboBox() != "No match" else 0
            minimumVolume = feature.attribute(self.minVTankscomboBox()) if self.minVTankscomboBox() != "No match" else 0
            nominalDiameter = feature.attribute(self.diameterTankscomboBox()) if self.diameterTankscomboBox() != "No match" else 0

            feature_json = {
                "serverKeyId": server_key_id,
                "scenarioFK": scenario_fk,
                "name": name,
                "description": description,
                "lng": transformed_point.x(),
                "lat": transformed_point.y(),
                "z": z,
                "initialLevel": initialLevel,
                "minimumLevel": minimumLevel,
                "maximumLevel": maximumLevel,
                "minimumVolume": minimumVolume,
                "nominalDiameter": nominalDiameter,
                }
            self.post_to_server(feature_json, name)
            features.append(feature_json)
        # Save features as JSON to a file
        with open("/Users/alejandrorodriguez/Documents/Courses/Data Science/Personal Projects/Jumapa/Json to Qgis/Data.json", 'w') as file:
            json.dump(features, file, indent=4)
        
        QgsProject.instance().removeMapLayer(layer)
        return features
    
    def convert_sensor_to_json(self, layer_name):
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        features = []
        # Define the source and destination coordinate reference systems
        crs_source = layer.crs()
        crs_destination = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84
        transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())

        for feature in layer.getFeatures():
            geom = feature.geometry()
            point = geom.asPoint()
            transformed_point = transform.transform(point)

            server_key_id = str(uuid.uuid4())
            scenario_fk = WateringUtils.getScenarioId()

            ### Optimize later Adapt ui correctly
            if self.sensorNameCBox.currentText() == "No match":
                name = "Sensor"
            else:
                name = feature.attribute(self.sensorNameCBox.currentText())
                    
            if self.sensorDescriptCBox.currentText() == "No match":
                description = ""
            else:
                description = feature.attribute(self.sensorDescriptCBox.currentText())

            if self.sensorZCBox.currentText() == "No match":
                z = 0
            else:
                z = feature.attribute(self.sensorZCBox.currentText())

            feature_json = {
                "serverKeyId": server_key_id,
                "scenarioFK": scenario_fk,
                "name": name,
                "description": description,
                "lng": transformed_point.x(),
                "lat": transformed_point.y(),
                "z": z
            }
            
            self.post_to_server(feature_json, name)
            features.append(feature_json)
        print(features)
        QgsProject.instance().removeMapLayer(layer)
        return features
    
    def post_to_server(self, json, name):
        headers = {'Authorization': "Bearer {}".format(self.token)}
        response = requests.post(self.UrlPost, json=json, headers=headers)
        #response = WateringUtils.requests_post(self.UrlPost, json)

        if response.status_code == 200:
            print(f'"{name}" correctly uploaded')
            print(response)
            #time.sleep(1.5)
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Watering Shp")
            message_box.setText("Failed to upload file. Status code: {}".format(response.status_code))
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()