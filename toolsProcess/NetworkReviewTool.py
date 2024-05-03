import os
from ..watering_utils import WateringUtils
from qgis.core import Qgis, QgsProject, QgsCoordinateTransformContext, QgsProcessingFeedback, QgsGeometry, QgsFeature, QgsPoint, QgsPointXY, QgsVectorLayer
import processing
from PyQt5.QtWidgets import QAction, QMessageBox, QLabel
import uuid

class NetworkReviewTool:

    def __init__(self, iface):
        self.iface = iface
        self.pipe_layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]
        self.node_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        self.project_path = WateringUtils.getProjectPath()
        self.scenario_id = WateringUtils.getScenarioId()
        # Temporary Layers
        self.intersections_layer = None
        self.snap_layer = None
        self.linesOnNodes = None
        self.splited_lines = None
        self.interpolate_layer = None
    
    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.iface.tr(u"Error"), 
                                                self.iface.tr(u"Load a project scenario first in Download Elements!"), 
                                                level=1, duration=5)
            return
            
        if os.environ.get('TOKEN') is None:
            self.iface.messageBar().pushMessage(self.iface.tr("Error"), 
                                                self.iface.tr("You must login to WaterIng first!"), 
                                                level=1, duration=5)
            return

        field_waterM_nodeFK = 'Unconected'
        unnconnected = 1
        WateringUtils.createNewColumn(self, "watering_demand_nodes", field_waterM_nodeFK)

        self.node_layer.startEditing()
        
        field_index = self.node_layer.fields().indexFromName(field_waterM_nodeFK)

        pipe_features = list(self.pipe_layer.getFeatures())
        node_features = list(self.node_layer.getFeatures())
        
        for feature_x in pipe_features:
            pipe_geom = feature_x.geometry()
            
            for feature_y in node_features:
                node_geom = feature_y.geometry()

                if not node_geom.disjoint(pipe_geom):
                    continue
                else:
                    # Calculate distance between point and MultiLineString
                    distance = node_geom.distance(pipe_geom)
                
                    if distance <= 5:
                        self.node_layer.dataProvider().changeAttributeValues({feature_y.id(): {field_index: unnconnected}})
        
        self.node_layer.commitChanges()
        WateringUtils.changeColors(self,self.node_layer,field_waterM_nodeFK, "categorized")

        self.button()

        self.iface.messageBar().pushMessage("Success", "Successfully identified unconnected nodes!", level=Qgis.Success, duration=6)
        print("Update completed.")

    def run_once(func):
        def wrapper(*args, **kwargs):
            if not wrapper.has_run:
                func(*args, **kwargs)
                wrapper.has_run = True
        wrapper.has_run = False
        return wrapper

    def intersectionLayer(self):
        layer_name = 'Intersections'

        # Define the parameters for the Line Intersections tool
        parameters = {
            'INPUT': self.pipe_layer,
            'INTERSECT': self.pipe_layer,
            'OUTPUT': 'memory:' + layer_name,
            'INTERSECT_FIELDS': [],  # Keep all fields from intersect layer
            'INPUT_FIELDS': []  # Keep all fields from input layer
        }

        # Run the Line Intersections tool
        feedback = QgsProcessingFeedback()
        result = processing.run("qgis:lineintersections", parameters, feedback=feedback)

        # Check if the tool ran successfully
        self.intersections_layer = self.process_result(result)
    
    def interpolatePointsToLines(self):
        uri = "Point?crs=epsg:3857&field=id:integer&field=name:string(20)&index=yes"
        layer = QgsVectorLayer(uri, "Interpolate", "memory")
        QgsProject.instance().addMapLayer(layer)
        self.interpolate_layer = QgsProject.instance().mapLayersByName("Interpolate")[0]
        for feature_x in self.pipe_layer.getFeatures():
            pipe_geom = feature_x.geometry()
            for feature_y in self.node_layer.getFeatures():
                node_geom = feature_y.geometry()
                if not node_geom.disjoint(pipe_geom):
                    continue
                else:
                    # Calculate distance between point and MultiLineString
                    distance = node_geom.distance(pipe_geom)
                    if distance <= 5:
                        # Get the point along the pipe which is closest to the node
                        _, closest_point, _, _ = pipe_geom.closestSegmentWithContext(node_geom.asPoint())
                        # Create a QgsGeometry object for the closest point
                        closest_point_geom = QgsGeometry.fromPointXY(closest_point)
                        new_feature = QgsFeature()
                        new_feature.setGeometry(closest_point_geom)
                        layer.dataProvider().addFeature(new_feature)

    def snapPointTioPoint(self, layer_name, input, reference, behavior):
        # Define the parameters for the Snap geometries to layer tool
        parameters = {
            'INPUT': input,
            'REFERENCE_LAYER': reference,
            'TOLERANCE': 6.000,  # Set a suitable tolerance value
            'BEHAVIOR': behavior,  # 0 for closest
            'OUTPUT': 'memory:' + layer_name
        }

        # Run the Snap geometries to layer tool
        feedback = QgsProcessingFeedback()
        result = processing.run("native:snapgeometries", parameters, feedback=feedback)
        #path = f'{self.project_path}/{self.scenario_id}/watering_demand_nodes.shp'

        # Check if the tool ran successfully
        self.snap_layer = self.process_result(result)
        
    def copyCoordinates(self, layer, newCoordinates):
        id_column_name = "ID"
        # Start editing for Layer Nodes
        layer.startEditing()

        # Get the features of both layers
        layer_features = {f.attribute(id_column_name): f for f in layer.getFeatures()}
        newSnap_features = {f.attribute(id_column_name): f for f in newCoordinates.getFeatures()}

        # Iterate through features in snapLayer and update coordinates in self.node_layer
        for feature_id, snap_feature in newSnap_features.items():
            node_feature = layer_features.get(feature_id)
            
            if node_feature:
                layer.dataProvider().changeGeometryValues({node_feature.id(): snap_feature.geometry()})

        # Commit changes
        layer.commitChanges()

    def split_lines_with_lines(self, input_layer, split_layer):
        layer_name = "Splited lines"
        #output = f'{self.project_path}/{self.scenario_id}/watering_pipes.shp'
        params = {
            'INPUT': input_layer,
            'LINES': split_layer,
            'OUTPUT': 'memory:' + layer_name
        }
        # Run the Snap geometries to layer tool
        feedback = QgsProcessingFeedback()
        result = processing.run("qgis:splitwithlines", params, feedback=feedback)
        # Check if the tool ran successfully
        self.splited_lines = self.process_result(result)
        #self.setFinalData()
        
        id_field_index = self.splited_lines.fields().indexFromName("ID")
    
        self.splited_lines.startEditing()
        
        for feature in self.splited_lines.getFeatures():
            new_uuid = str(uuid.uuid4())[:10]
            self.splited_lines.changeAttributeValue(feature.id(), id_field_index, new_uuid)

        self.splited_lines.commitChanges()
        
    def create_lines_on_points(self, input_layer):
        layer_name = "Lines on nodes"
        params = {
            'INPUT': input_layer,
            'OUTPUT_GEOMETRY': 1,
            'EXPRESSION': "make_line($geometry, translate($geometry, 5, 5))",
            'OUTPUT': 'memory:' + layer_name
        }
        # Run the Snap geometries to layer tool
        feedback = QgsProcessingFeedback()
        result = processing.run("native:geometrybyexpression", params, feedback=feedback)
        
        # Check if the tool ran successfully
        self.linesOnNodes = self.process_result(result)

    def button(self):
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(None,
                                            "Conitnue Fixing the Network",
                                            "The current network has errors. Do you want to continue to fix the unconnected nodes?",
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if response == QMessageBox.Yes:
                #node adjustment
                self.intersectionLayer()
                self.interpolatePointsToLines()
                self.snapPointTioPoint("Interpolated to Intersections", self.interpolate_layer, self.intersections_layer,3)
                self.snapPointTioPoint("Points to points",self.node_layer, self.snap_layer, 3)
                self.copyCoordinates(self.node_layer, self.snap_layer)

                #pipes adjustment
                self.snapPointTioPoint("Lines to points",self.pipe_layer, self.node_layer, 0)
                self.create_lines_on_points(self.node_layer)
                self.split_lines_with_lines(self.snap_layer, self.linesOnNodes)
                #self.copyCoordinates(self.pipe_layer, self.splited_lines)

                self.cleanUpTemporaryData()
            
                print("Finished fixing the network")
            elif response == QMessageBox.Cancel:
                print("Out")
                return
            
    def process_result(self, result):
        if result['OUTPUT']:
            lines_on_nodes = result['OUTPUT']
            QgsProject.instance().addMapLayer(lines_on_nodes)
            print("Snap layer created successfully.")
            return lines_on_nodes
        else:
            print("Error creating snap layer.")
            return None
        
    def cleanUpTemporaryData(self):
        project = QgsProject.instance()
        # List of layer names to delete
        layers_to_delete = ['Intersections', 'Points to points', 'Lines to points',
                            'snaped_layer', 'Lines on nodes', 'Interpolate', 'Interpolated to Intersections']
        for layer_name in layers_to_delete:
            layer_id = project.mapLayersByName(layer_name)
            if layer_id:
                project.removeMapLayer(layer_id[0])
        WateringUtils.delete_column(self,self.node_layer,"Unconected")
        WateringUtils.changeColors(self,self.node_layer,"","single")

"""     def setFinalData(self):
        #New addition od uuid4 code to new pipes when spliting
        id_count = {}  # Dictionary to store counts of each original ID

        self.splited_lines.startEditing()

        for feature in self.splited_lines.getFeatures():
            # Get the line geometry
            line_geometry = feature.geometry().asPolyline()
            # Get the start (up) node and end (down) node of the line
            start_node = line_geometry[0]
            end_node = line_geometry[-1]
            # Update the "Up-Node" and "Down-Node" fields with the start and end nodes respectively
            self.splited_lines.changeAttributeValue(feature.id(), self.splited_lines.fields().indexFromName("Up-Node"), start_node)
            self.splited_lines.changeAttributeValue(feature.id(), self.splited_lines.fields().indexFromName("Down-Node"), end_node)
            # Calculate the length of the line geometry
            line_length = feature.geometry().length()
            # Update the "Length" field with the calculated length
            self.splited_lines.changeAttributeValue(feature.id(), self.splited_lines.fields().indexFromName("Length"), line_length)
            original_id = feature['ID']
            if original_id not in id_count:
                id_count[original_id] = 1
            else:
                id_count[original_id] += 1
            
            if id_count[original_id] > 1:
                # Assign a new unique ID using UUID
                unique_id = str(uuid.uuid4())[:36]  # Generate UUID and truncate to first 36 characters
                feature.setAttribute("ID", unique_id)
                self.splited_lines.updateFeature(feature)

        self.splited_lines.commitChanges() """
