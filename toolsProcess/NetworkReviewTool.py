import os
from ..watering_utils import WateringUtils
from qgis.core import Qgis, QgsProject, QgsProcessingFeedback, QgsGeometry, QgsFeature, QgsVectorLayer
import processing
from PyQt5.QtWidgets import QMessageBox
import uuid
import datetime

class NetworkReviewTool:

    def __init__(self, iface):
        self.iface = iface
        self.pipe_layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]
        self.node_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        self.reservoir_layer = QgsProject.instance().mapLayersByName("watering_reservoirs")[0]
        self.tanks_layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
        self.pumps_layer = QgsProject.instance().mapLayersByName("watering_pumps")[0]
        self.valves_layer = QgsProject.instance().mapLayersByName("watering_valves")[0]

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
        self.find_unconnected_nodes()

    def find_unconnected_nodes(self):
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
        
        WateringUtils.changeColors(self.node_layer,field_waterM_nodeFK, "categorized")

        self.button()

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

        feedback = QgsProcessingFeedback()
        result = processing.run("qgis:lineintersections", parameters, feedback=feedback)

        self.intersections_layer = self.process_result(result)
    
    def interpolatePointsToLines(self):
        uri = "Point?crs=epsg:3857&field=id:integer&field=name:string(20)&index=yes"
        layer = QgsVectorLayer(uri, "Interpolate", "memory")
        QgsProject.instance().addMapLayer(layer)
        self.interpolate_layer = QgsProject.instance().mapLayersByName("Interpolate")[0]

        node_pipe_associations = {}
        for feature_x in self.pipe_layer.getFeatures():
            pipe_geom = feature_x.geometry()
            for feature_y in self.node_layer.getFeatures():
                node_id = feature_y.id()
                node_geom = feature_y.geometry()
                
                # Calculate distance between point and MultiLineString
                distance = node_geom.distance(pipe_geom)
                if distance <= 5:
                    # If node already associated with another pipe, skip
                    if node_id in node_pipe_associations:
                        continue
                    # Get the point along the pipe which is closest to the node
                    _, closest_point, _, _ = pipe_geom.closestSegmentWithContext(node_geom.asPoint())
                    # Store association between node and pipe
                    node_pipe_associations[node_id] = {'line_id': feature_x.id(), 'closest_point': closest_point}
        # Interpolate points based on associations
        for node_id, association in node_pipe_associations.items():
            closest_point = association['closest_point']
            closest_point_geom = QgsGeometry.fromPointXY(closest_point)
            new_feature = QgsFeature()
            new_feature.setGeometry(closest_point_geom)
            layer.dataProvider().addFeature(new_feature)

    def snapPointTioPoint(self, layer_name, input, reference, behavior):
        parameters = {
            'INPUT': input,
            'REFERENCE_LAYER': reference,
            'TOLERANCE': 5.000,  # Set a suitable tolerance value
            'BEHAVIOR': behavior,
            'OUTPUT': 'memory:' + layer_name
        }
        feedback = QgsProcessingFeedback()
        result = processing.run("native:snapgeometries", parameters, feedback=feedback)

        self.snap_layer = self.process_result(result)
        
    def copyCoordinates(self, layer, newCoordinates, case):
        layer.startEditing()
        # Get the features of both layers
        layer_features = {f.attribute("ID"): f for f in layer.getFeatures()}
        newSnap_features = {f.attribute("ID"): f for f in newCoordinates.getFeatures()}
        # Iterate through features in snapLayer and update coordinates in self.node_layer
        for feature_id, snap_feature in newSnap_features.items():
            feature = layer_features.get(feature_id)
            if case == 1:  # For pipes
                if feature:
                    layer.dataProvider().changeGeometryValues({feature.id(): snap_feature.geometry()})
                else:
                    layer.addFeature(snap_feature)
            if case == 0:  # For nodes
                if feature:
                    layer.dataProvider().changeGeometryValues({feature.id(): snap_feature.geometry()})
                else:
                    layer.addFeature(snap_feature)
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

    def update_attributes(self, layer, case):
        #Change to new attributes 
        id_field_index = layer.fields().indexFromName("ID")
        down_node_field_index = layer.fields().indexFromName("Down-Node")
        up_node_field_index = layer.fields().indexFromName("Up-Node")

        layer.startEditing()
        if case == 0: #For pipes
            for feature in layer.getFeatures():
                new_uuid = str(uuid.uuid4())[:10]
                down_node, up_node = self.getPipeNodes(feature)
                attr_values = {
                    id_field_index: new_uuid,
                    down_node_field_index: str(down_node),
                    up_node_field_index: str(up_node)
                }
                layer.changeAttributeValues(feature.id(), attr_values)
        else: #For Nodes
             for feature in layer.getFeatures():
                new_uuid = str(uuid.uuid4())[:10]
                attr_values = {
                    id_field_index: new_uuid
                }
                layer.changeAttributeValues(feature.id(), attr_values)

        layer.commitChanges()
    
    #START
    def getPipeNodes(self, feature):
        demand_nodes_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        tanks_layer = QgsProject.instance().mapLayersByName("watering_tanks")[0]
        reservoirs_layer = QgsProject.instance().mapLayersByName("watering_reservoirs")[0]
        
        polyline_geom = feature.geometry()

        if polyline_geom.isMultipart():
            lines = polyline_geom.asMultiPolyline()
            start_point = lines[0][0]  
            end_point = lines[-1][-1]  
        else:
            line = polyline_geom.asPolyline()
            start_point = line[0]
            end_point = line[-1]
        
        up_node = None
        down_node = None

        for layer in [demand_nodes_layer, tanks_layer, reservoirs_layer]:
            up_node = self.find_matching_node(start_point, layer)
            if up_node:
                break

        for layer in [demand_nodes_layer, tanks_layer, reservoirs_layer]:
            down_node = self.find_matching_node(end_point, layer)
            if down_node:
                break
            
        return down_node, up_node
        
    def find_matching_node(self, point, node_layer):
        tolerance=0.0001
        for node in node_layer.getFeatures():
            node_point = node.geometry().asPoint()
            if point.distance(node_point) < tolerance:
                return node["ID"]
        return None
    #END
    
    def create_lines_on_points(self, input_layer):
        layer_name = "Lines on nodes"
        params = {
            'INPUT': input_layer,
            'OUTPUT_GEOMETRY': 1,
            'EXPRESSION': "make_line($geometry, translate($geometry, 0.9, 0.9))",
            'OUTPUT': 'memory:' + layer_name
        }
        feedback = QgsProcessingFeedback()
        result = processing.run("native:geometrybyexpression", params, feedback=feedback)
    
        self.linesOnNodes = self.process_result(result)

    def button(self):
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(None,
                                            "Fix Unconnected Nodes",
                                            "The current network has errors. Do you want to continue to fix the unconnected nodes?",
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if response == QMessageBox.Yes:

                self.reviewProcess()
                WateringUtils.delete_column(self.node_layer,"Unconected")
                WateringUtils.changeColors(self.node_layer,"","single")

                self.iface.messageBar().pushMessage("Success", "Successfully identified unconnected nodes!", level=Qgis.Success, duration=6)
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
                            'snaped_layer', 'Lines on nodes', 'Interpolate', 'Interpolated to Intersections', 
                            'Splited lines', 'Reservoirs to nodes']
        for layer_name in layers_to_delete:
            layer_id = project.mapLayersByName(layer_name)
            if layer_id:
                project.removeMapLayer(layer_id[0])
    
    def deleteAllFeatures(self,layer):
        #Add to back up layer before deleting
        for feature in layer.getFeatures():
            WateringUtils.add_feature_to_backup_layer(feature, layer)
        #Delete all features of a layer
        layer.startEditing()
        feature_ids = [feature.id() for feature in layer.getFeatures()]
        layer.dataProvider().deleteFeatures(feature_ids)
        layer.commitChanges()

    def removeDuplicatePoints(self, layer, reference_layer=None):
        unique_points = set()
        # Collect reference points for comparison if a reference layer is provided
        reference_points = set()
        if reference_layer:
            for feature in reference_layer.getFeatures():
                point = feature.geometry().asPoint()
                point_tuple = (point.x(), point.y())
                reference_points.add(point_tuple)
        for feature in layer.getFeatures():
            point = feature.geometry().asPoint()
            point_tuple = (point.x(), point.y())
            # Check if the point is duplicate in the layer or the reference layer
            if point_tuple in unique_points or (reference_layer and point_tuple in reference_points):
                # Delete duplicate feature
                WateringUtils.add_feature_to_backup_layer(feature, layer)
                layer.dataProvider().deleteFeatures([feature.id()])
            else:
                # Add unique point to set
                unique_points.add(point_tuple)

    def eliminateCloseNodes(self):
        for feature_x in self.node_layer.getFeatures():
            node_geom_x = feature_x.geometry()
            
            for feature_y in self.node_layer.getFeatures():
                if feature_x == feature_y:
                    continue  # Skip self-comparison
                node_geom_y = feature_y.geometry()
                distance = node_geom_x.distance(node_geom_y)
                # If distance is less than 5, delete one of the nodes
                if distance < 5:
                    WateringUtils.add_feature_to_backup_layer(feature_y, self.node_layer)
                    self.node_layer.deleteFeature(feature_y.id())
                    break 

    @run_once
    def reviewProcess(self):
        #node adjustment
        self.intersectionLayer()
        #self.eliminateCloseNodes()
        self.interpolatePointsToLines()
        self.snapPointTioPoint("Interpolated to Intersections", self.interpolate_layer, self.intersections_layer,3)
        self.snapPointTioPoint("Points to points",self.node_layer, self.snap_layer, 3)
        self.deleteAllFeatures(self.node_layer)
        self.copyCoordinates(self.node_layer, self.snap_layer,0)
        self.update_attributes(self.node_layer, 1)
        self.removeDuplicatePoints(self.node_layer)

        #pipes adjustment
        self.snapPointTioPoint("Lines to points",self.pipe_layer, self.node_layer, 0)
        self.create_lines_on_points(self.node_layer)
        self.split_lines_with_lines(self.snap_layer, self.linesOnNodes)

        #Other elements adjustment
        self.snapPointTioPoint("Reservoirs to nodes", self.reservoir_layer, self.node_layer,3)
        self.copyCoordinates(self.reservoir_layer, self.snap_layer,0)
        self.update_attributes(self.reservoir_layer, 1)
        self.removeDuplicatePoints(self.node_layer, self.reservoir_layer)

        #Continue on pipes
        self.update_attributes(self.splited_lines, 0)
        self.deleteAllFeatures(self.pipe_layer)
        self.copyCoordinates(self.pipe_layer, self.splited_lines,1)

        self.cleanUpTemporaryData()
