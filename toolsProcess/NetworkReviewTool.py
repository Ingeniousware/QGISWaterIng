import os
from ..watering_utils import WateringUtils
from qgis.core import Qgis, QgsProject, QgsCoordinateTransformContext, QgsProcessingFeedback
import processing
from PyQt5.QtWidgets import QAction, QMessageBox, QLabel

class NetworkReviewTool:

    def __init__(self, iface):
        self.iface = iface
        self.pipe_layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]
        self.node_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        self.project_path = WateringUtils.getProjectPath()
        self.scenario_id = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        self.intersections_layer = None
        self.snap_layer = None
    
    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.iface.tr(u"Error"), self.iface.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
            return
            
        if os.environ.get('TOKEN') is None:
            self.iface.messageBar().pushMessage(self.iface.tr("Error"), self.iface.tr("You must login to WaterIng first!"), level=1, duration=5)
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
        WateringUtils.changeColors(self,self.node_layer,field_waterM_nodeFK)

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
        if result['OUTPUT']:
            self.intersections_layer = result['OUTPUT']
            QgsProject.instance().addMapLayer(self.intersections_layer)
            print("Intersection layer created successfully.")
        else:
            print("Error creating intersection layer.")

    def snapPointTioPoint(self):
        layer_name = "snapped_layer"
    
        # Define the parameters for the Snap geometries to layer tool
        parameters = {
            'INPUT': self.node_layer,
            'REFERENCE_LAYER': self.intersections_layer,
            'TOLERANCE': 6.000,  # Set a suitable tolerance value
            'BEHAVIOR': 3,  # 0 for closest
            'OUTPUT': 'memory:' + layer_name
        }

        # Run the Snap geometries to layer tool
        feedback = QgsProcessingFeedback()
        result = processing.run("native:snapgeometries", parameters, feedback=feedback)
        path = f'{self.project_path}/{self.scenario_id}/watering_demand_nodes.shp'
        # Create the transform context
        transform_context = QgsCoordinateTransformContext()

        # Check if the tool ran successfully
        if result['OUTPUT']:
            self.snap_layer = result['OUTPUT']
            QgsProject.instance().addMapLayer(self.snap_layer)
            print("Snap layer created successfully.")
            self.copyCoordinates(self.snap_layer)
        
        else:
            print("Error creating snap layer.")
        

    def copyCoordinates(self):
        id_column_name = "ID"
        # Start editing for Layer Nodes
        self.node_layer.startEditing()

        # Get the features of both layers
        node_features = {f.attribute(id_column_name): f for f in self.node_layer.getFeatures()}
        snap_features = {f.attribute(id_column_name): f for f in self.snap_layer.getFeatures()}

        # Iterate through features in snapLayer and update coordinates in self.node_layer
        for feature_id, snap_feature in snap_features.items():
            node_feature = node_features.get(feature_id)
            
            if node_feature:
                self.node_layer.dataProvider().changeGeometryValues({node_feature.id(): snap_feature.geometry()})

        # Commit changes
        self.node_layer.commitChanges()

    @run_once
    def button(self):
        project = QgsProject.instance()
        if project.isDirty():
            response = QMessageBox.question(None,
                                            "Conitnue Fixing the Network",
                                            "The current network has errors. Do you want to continue to fix the unconnected nodes?",
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if response == QMessageBox.Yes:
                self.intersectionLayer()
                self.snapPointTioPoint()
                self.copyCoordinates()
                
                #Delete temporary layers
                #QgsProject.instance().removeMapLayer(self.intersections_layer.id())
                #QgsProject.instance().removeMapLayer(self.snap_layer.id())
            
                print("yes")
            elif response == QMessageBox.Cancel:
                print("Out mtoherfkr")
                return


