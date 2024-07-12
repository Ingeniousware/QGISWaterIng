from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QInputDialog, QLineEdit
import uuid
import requests
import os
from ..watering_utils import WateringUtils
from ..shpProcessing.abstractShpImport import AbstractShpImport

class ImportDMAShp(AbstractShpImport):
    def __init__(self):
            #Constructor.
            super(ImportDMAShp, self).__init__()
    
    def post_to_server(json, name):
        headers = {'Authorization': f"Bearer {os.environ.get('TOKEN')}"}
        UrlPost = WateringUtils.getServerUrl() + "/api/v1/WaterDMA/withcoordinates"
        #response = WateringUtils.requests_post(UrlPost, json)
        response = requests.post(UrlPost, json=json, headers=headers)
        print(response)

    def shpProcessing(self, layer_name):
            layer = QgsProject.instance().mapLayersByName(layer_name)[0]
            features = []
            # Define the source and destination coordinate reference systems
            crs_source = layer.crs()
            crs_destination = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84
            transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())

            for feature in layer.getFeatures():
                geom = feature.geometry()
                polygon = geom.asMultiPolygon()
                vertices = []
                n = len(polygon[0])
                for i in range(n):
                    coordinateList = polygon[0][i]
                    for point in coordinateList:
                        transformed_point = transform.transform(point)
                        vertices.append({
                            "vertexFK": str(uuid.uuid4()),
                            "lng": transformed_point.x(),
                            "lat": transformed_point.y(),
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
                ImportDMAShp.post_to_server(feature_json, name)
                features.append(feature_json)
            QgsProject.instance().removeMapLayer(layer)
            return features