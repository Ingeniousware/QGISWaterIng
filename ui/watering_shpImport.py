# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QInputDialog, QLineEdit
import os
import json
import uuid
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
        self.token = os.environ.get('TOKEN')
        self.UrlPost = WateringUtils.getServerUrl() + "/api/v1/WaterDMA/withcoordinates"
        self.uploadShpFile.clicked.connect(lambda: self.addDMA_Layer(0))
    
    def addDMA_Layer(self, behavior):
        self.file_path = self.newSHPDirectory.filePath()
        vlayer = QgsVectorLayer(self.file_path, "New DMA Layer", "ogr")
        if not vlayer.isValid():
            print("Layer failed to load!")
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Error")
            message_box.setText("File not uploaded")
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()
        else:
            QgsProject.instance().addMapLayer(vlayer)
            self.close()
            self.convert_polygon_to_json("New DMA Layer")

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
            name = feature.attribute("Name")
            description = "Imported from Qgis"
            sector_index = 0
            element_count = 0
            total_demand = 0

            # Print feature attributes for debugging
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
            #Send DMA to server post
            self.postDMA(feature_json, name)
            # Append the feature JSON to the list of features
            features.append(feature_json)

        return features
    
    def postDMA(self, json, name):

        headers = {'Authorization': "Bearer {}".format(self.token)}
        response = requests.post(self.UrlPost, json=json, headers=headers)

        if response.status_code == 200:
            print("DMA Uploaded")
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Watering Shape")
            message_box.setText(f'DMA "{name}" uploaded')
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()
            # Close the message box after 1 second
            time.sleep(1)
            message_box.close()
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Watering Shape")
            message_box.setText("Failed to upload file. Status code: {}".format(response.status_code))
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()