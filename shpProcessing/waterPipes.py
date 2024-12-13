from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)
import json
import uuid
from datetime import datetime
from ..watering_utils import WateringUtils
from ..shpProcessing.abstractShpImport import AbstractShpImport


class ImportPipesShp(AbstractShpImport):

    def __init__(self):
        # Constructor.
        super(ImportPipesShp, self).__init__()

    def shpProcessing(self, layer_name):
        source_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        pipes_layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]
        nodes_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]

        # Define the source and destination coordinate reference systems
        crs_source = source_layer.crs()
        crs_destination = QgsCoordinateReferenceSystem("EPSG:3857")
        transform = QgsCoordinateTransform(crs_source, crs_destination, QgsProject.instance())

        # Prepare fields for the new features in the destination layers
        pipe_fields = pipes_layer.fields()
        node_fields = nodes_layer.fields()

        scenario_fk = WateringUtils.getScenarioId()
        current_datetime = datetime.utcnow().isoformat() + "Z"

        pipe_features = []
        node_features = []
        special_vertices_dict = {}
        count = 0

        for feature in source_layer.getFeatures():
            geom = feature.geometry()
            linestring = geom.asMultiPolyline()[0]
            transformed_linestring = [transform.transform(QgsPointXY(pt)) for pt in linestring]

            # Extract attribute values based on combobox mappings
            name = (
                feature.attribute(self.pipeNameCBox.currentText())
                if self.pipeNameCBox.currentText() != "No match"
                else "Pipe"
            )
            description = (
                feature.attribute(self.pipeDescriptCBox.currentText())
                if self.pipeDescriptCBox.currentText() != "No match"
                else "Imported from Shp"
            )
            diameter = (
                feature.attribute(self.pipeDiameterCBox.currentText())
                if self.pipeDiameterCBox.currentText() != "No match"
                else 0.2
            )
            rough = (
                feature.attribute(self.pipeRoughCBox.currentText())
                if self.pipeRoughCBox.currentText() != "No match"
                else 0.045
            )
            length = (
                feature.attribute(self.pipeLengthCBox.currentText())
                if self.pipeLengthCBox.currentText() != "No match"
                else 0
            )

            vertices = []
            node_up_fk = None
            node_down_fk = None

            for index, pt in enumerate(transformed_linestring):
                coord_key = (pt.x(), pt.y())
                if index == 0 or index == len(transformed_linestring) - 1:
                    if coord_key in special_vertices_dict:
                        special_vertex = special_vertices_dict[coord_key]
                        special_vertex["description"] += f", {name}"
                    else:
                        special_vertex = {
                            "serverKeyId": str(uuid.uuid4())[:10],
                            "scenarioFK": scenario_fk,
                            "name": f"Node {count}",  # Unique name
                            "description": f"{name}",
                            "lng": pt.x(),
                            "lat": pt.y(),
                            "z": 0,
                            "baseDemand": 0,
                            "emitterCoeff": 0,
                            "removed": False,
                        }
                        special_vertices_dict[coord_key] = special_vertex
                        count += 1

                    if index == 0:
                        node_up_fk = special_vertex["serverKeyId"]
                    else:
                        node_down_fk = special_vertex["serverKeyId"]
                else:
                    vertex_fk = str(uuid.uuid4())[:10]
                    vertex = {"vertexFK": vertex_fk, "lng": pt.x(), "lat": pt.y(), "order": index}
                    vertices.append(vertex)

            # Create pipe feature
            pipe_feature = QgsFeature(pipe_fields)
            pipe_feature.setGeometry(QgsGeometry.fromPolylineXY(transformed_linestring))
            pipe_feature.setAttribute("ID", str(uuid.uuid4())[:10])
            pipe_feature.setAttribute("Last Mdf", current_datetime)
            pipe_feature.setAttribute("Up-Node", node_up_fk)
            pipe_feature.setAttribute("Down-Node", node_down_fk)
            pipe_feature.setAttribute("Name", name)
            pipe_feature.setAttribute("Descript", description)
            pipe_feature.setAttribute("Diameter", diameter)
            pipe_feature.setAttribute("Length", length)
            pipe_feature.setAttribute("Rough.A", rough)
            pipe_feature.setAttribute("C(H.W.)", 0)

            pipe_features.append(pipe_feature)

        # Add pipe features to the pipes layer
        pipes_layer.startEditing()
        pipes_layer.addFeatures(pipe_features)
        pipes_layer.commitChanges()

        # Create and add node features to the nodes layer
        for vertex in special_vertices_dict.values():
            node_feature = QgsFeature(node_fields)
            node_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(vertex["lng"], vertex["lat"])))
            node_feature.setAttribute("ID", vertex["serverKeyId"])
            node_feature.setAttribute("Name", vertex["name"])
            node_feature.setAttribute("Descript", vertex["description"])
            node_feature.setAttribute("Z[m]", vertex["z"])
            node_feature.setAttribute("B. Demand", vertex["baseDemand"])
            node_feature.setAttribute("EmitterCoe", vertex["emitterCoeff"])

            node_features.append(node_feature)

        nodes_layer.startEditing()
        nodes_layer.addFeatures(node_features)
        nodes_layer.commitChanges()

        QgsProject.instance().removeMapLayer(source_layer)
        return pipe_features, node_features
