from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeature, QgsGeometry, QgsPointXY
from qgis.PyQt.QtCore import Qt
import uuid
from ..shpProcessing.abstractShpImport import AbstractShpImport

class ImportValvesShp(AbstractShpImport):

    def __init__(self):
            #Constructor.
            super(ImportValvesShp, self).__init__()
    
    def shpProcessing(self, layer_name):
        source_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        destination_layer_name = "watering_valves"
        destination_layer = QgsProject.instance().mapLayersByName(destination_layer_name)[0]

        # Define the source and destination coordinate reference systems
        crs_source = source_layer.crs()
        crs_destination = QgsCoordinateReferenceSystem("EPSG:3857")
        transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())

        # Prepare fields for the new features in the destination layer
        fields = destination_layer.fields()

        features = []

        for feature in source_layer.getFeatures():
            geom = feature.geometry()
            point = geom.asPoint()
            transformed_point = transform.transform(point)

            server_key_id = str(uuid.uuid4())[:10]

            # Extract attribute values based on your combobox mappings
            name = feature.attribute(self.valveNameCBox.currentText()) if self.valveNameCBox.currentText() != "No match" else "Valve"
            description = feature.attribute(self.valveDescriptCBox.currentText()) if self.valveDescriptCBox.currentText() != "No match" else "Imported from Shp"
            z = feature.attribute(self.valveZCBox.currentText()) if self.valveZCBox.currentText() != "No match" else 0
            diameter = feature.attribute(self.valveDiameterCBox.currentText()) if self.valveDiameterCBox.currentText() != "No match" else 0.2
            typeValve = feature.attribute(self.typeValveCBox.currentText()) if self.typeValveCBox.currentText() != "No match" else 0
            setting = feature.attribute(self.valveSettingCBox.currentText()) if self.valveSettingCBox.currentText() != "No match" else 20
            minorLossCoef = feature.attribute(self.minorValveCBox.currentText()) if self.minorValveCBox.currentText() != "No match" else 0
            initialStatus = feature.attribute(self.valveStatusCBox.currentText()) if self.valveStatusCBox.currentText() != "No match" else 1

            # Create a new feature
            new_feature = QgsFeature(fields)
            new_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(transformed_point)))

            # Set attributes
            new_feature.setAttribute("ID", server_key_id)
            new_feature.setAttribute("Name", name)
            new_feature.setAttribute("Descript", description)
            new_feature.setAttribute("Z[m]", z)
            new_feature.setAttribute("Diameter", diameter)
            new_feature.setAttribute("typeValvul", typeValve)
            new_feature.setAttribute("setting", setting)
            new_feature.setAttribute("minorLossC", minorLossCoef)
            new_feature.setAttribute("initialSta", initialStatus)


            # Add the feature to the destination layer
            destination_layer.startEditing()
            destination_layer.addFeature(new_feature)
            destination_layer.commitChanges()

            features.append(new_feature)
        
        QgsProject.instance().removeMapLayer(source_layer)
        return features
