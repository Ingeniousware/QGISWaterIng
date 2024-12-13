from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)
from qgis.PyQt.QtCore import Qt
import uuid
from ..watering_utils import WateringUtils
from ..shpProcessing.abstractShpImport import AbstractShpImport


class ImportSensorsShp(AbstractShpImport):

    def __init__(self):
        # Constructor.
        super(ImportSensorsShp, self).__init__()

    def shpProcessing(self, layer_name):
        source_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        destination_layer_name = "watering_sensors"
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
            name = (
                feature.attribute(self.sensorNameCBox.currentText())
                if self.sensorNameCBox.currentText() != "No match"
                else "Sensor"
            )
            description = (
                feature.attribute(self.sensorDescriptCBox.currentText())
                if self.sensorDescriptCBox.currentText() != "No match"
                else "Imported from Shp"
            )
            z = feature.attribute(self.sensorZCBox.currentText()) if self.sensorZCBox.currentText() != "No match" else 0

            # Create a new feature
            new_feature = QgsFeature(fields)
            new_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(transformed_point)))

            # Set attributes
            new_feature.setAttribute("ID", server_key_id)
            new_feature.setAttribute("Name", name)
            new_feature.setAttribute("Descript", description)
            new_feature.setAttribute("Z[m]", z)

            # Add the feature to the destination layer
            destination_layer.startEditing()
            destination_layer.addFeature(new_feature)
            destination_layer.commitChanges()

            features.append(new_feature)

        QgsProject.instance().removeMapLayer(source_layer)
        return features
