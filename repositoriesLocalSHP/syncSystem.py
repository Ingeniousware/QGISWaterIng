from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsLineString, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest, QgsCoordinateTransform
from PyQt5.QtCore import QFileInfo, QDateTime, QDateTime, Qt
from ..watering_utils import WateringUtils
from .change import Change
from collections import deque
import json
        
class WateringSync():
    def __init__(self,token, project_path, scenarioFK, 
                 repositories):
        
        self.server_change_queue = deque()
        self.offline_change_queue = deque()
        
        # Name = operation + responsible side
        self.change_handlers = {
            "add_from_server": self.process_add_to_offline,
            "add_from_offline": self.process_add_to_server,
            "update_from_server": self.process_update_in_offline,
            "update_from_offline": self.process_update_on_server,
            "delete_from_server": self.process_delete_in_offline,
            "delete_from_offline": self.process_delete_on_server
        }
        
        self.token = token
        self.project_path = project_path
        self.scenarioFK = scenarioFK
        
        #Test variables 
        self.repo_copy = repositories.copy()
        self.repo_copy.pop(3)
        #self.repo_copy.pop(5)
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.destCrs = QgsCoordinateReferenceSystem(3857)
        
        self.repositories = self.repo_copy

    def initializeRepository(self):
        ...

    def get_server_changes(self, lastUpdated):
        print("self.lastUpdate: ", lastUpdated)
        # Test variables
        #test_lastUpdate = '2023-11-29T10:28:46.2756439Z'
        self.server_change_queue.clear()
        # End test variables
        
        for repo in self.repositories:
            response = repo.loadChanges(lastUpdated)
            if response._content:
                data = response.json()
                if data:
                    self.track_server_updates(repo, data)
                    
        print("server_change_queue: ", self.server_change_queue)

    def get_offline_changes(self, lastUpdated):
        print("self.lastUpdate: ", lastUpdated)
        # Test variables
        #test_lastUpdate = '2023-11-29T10:28:46.2756439Z'
        self.offline_change_queue.clear()
        # End test variables
        
        for repo in self.repositories:
            self.track_offline_updates(repo, lastUpdated)
        
        print("offline_change_queue: ", self.offline_change_queue)
        
    def track_server_updates(self, repo, data):
        changes_list = repo.getServerUpdates(data)
        self.server_change_queue.extend(changes_list)

    def track_offline_updates(self, repo, lastUpdated):
        changes_list = repo.getOfflineUpdates(lastUpdated)
        self.offline_change_queue.extend(changes_list)

    def synchronize(self):
        keyUpdate = WateringUtils.scenarioKeyLastUpdate(self.scenarioFK)
        lastUpdated = WateringUtils.getLastUpdate(keyUpdate)
        
        print("lastUpdated: ", lastUpdated)
        self.get_offline_changes(lastUpdated)
        self.get_server_changes(lastUpdated)
        self.synchronize_server_changes()
        self.synchronize_offline_changes()
        
        now = WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss")
        WateringUtils.setProjectMetadata(keyUpdate, now)
        
    def synchronize_server_changes(self):
        while self.server_change_queue:
            change = self.server_change_queue.popleft()
            self.processChange(change)

    def synchronize_offline_changes(self):
        while self.offline_change_queue:
            change = self.offline_change_queue.popleft()
            self.processChange(change)
            
    def processChange(self, change):
        try:
            process_method = self.change_handlers[change.change_type]
            process_method(change)
        except KeyError:
            print(f"Unknown change type: {change.change_type}")
        
    def process_add_to_server(self, change):
        for repo in self.repositories:
            if change.layer_id.name() == repo.LayerName and repo.connectorToServer:
                repo.connectorToServer.addElementToServer(change.data)
                break
                
    def process_add_to_offline(self, change):
        print(f"Adding element in {change.layer_id}: {id} from server to offline")
        self.layer = change.layer_id
        
        feature = QgsFeature(self.layer.fields())
        feature.setAttribute("ID", change.feature_id)
        
        if self.layer.name() == "watering_pipes":
            #feature.setGeometry(QgsGeometry.fromPolylineXY(change.data[-1]))
            feature.setGeometry(change.data[-1])
        else:
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1])))
        
        self.layer.startEditing()
        
        for i, field in enumerate(self.get_field_definitions()):
            feature[field] = change.data[i]
        
        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
        
        self.layer.addFeature(feature)
        self.layer.commitChanges()
        
    def process_update_on_server(self, change):
        for repo in self.repositories:
            if change.layer_id.name() == repo.LayerName and repo.connectorToServer:
                repo.connectorToServer.addElementToServer(change.data)
                break
            
    def process_update_in_offline(self, change):
        layer_name = change.layer_id.name()
        print("Layer: ", layer_name)
        print(f"Update element in {change.layer_id}: {id} from server to offline")
        self.layer = change.layer_id
        
        self.layer.startEditing()

        attrs = {}

        field_definitions = self.get_field_definitions()
        
        for i in range(len(field_definitions)):
            field_index = self.layer.fields().indexOf(field_definitions[i])
            attrs[field_index] = change.data[i]

        last_update_index = self.layer.fields().indexOf('lastUpdate')
        attrs[last_update_index] = WateringUtils.getDateTimeNow()

        feature_id = self.get_feature_by_id(change.feature_id).id()
        
        self.layer.dataProvider().changeAttributeValues({feature_id: attrs})
        
        """if self.layer.name() == "watering_pipes":
            #new_geometry = QgsGeometry.fromPolylineXY(change.data[-1])
            #new_geometry = change.data[-1]
            data = change.data[-1]
            print("Data == ", change.data[-1])
            points = [QgsPointXY(vertex['lng'], vertex['lat']) for vertex in data]
            new_geometry = QgsGeometry.fromPolylineXY(points)
            new_geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
        else:
            new_geometry = QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1]))
            
        self.layer.dataProvider().changeGeometryValues({feature_id: new_geometry})"""

        self.layer.commitChanges()
        
        
    def process_delete_on_server(self, change):
        for repo in self.repositories:
            if change.layer_id.name() == repo.LayerName and repo.connectorToServer:
                #feature = self.get_feature_by_id(change.layer_i)
                repo.connectorToServer.removeElementFromServer(change.data["ID"])
                break
            
    def process_delete_in_offline(self, change):
        print(f"Delete element in {change.layer_id}: {id} from server to offline")
        
        self.layer = change.layer_id
        feature_to_delete = self.get_feature_by_id(change.feature_id)
        
        if feature_to_delete:
            self.layer.startEditing()
            self.layer.deleteFeatures(feature_to_delete.id())
            self.layer.commitChanges()

    def save_offline_changes_to_project(self):
       serialized_changes = json.dumps([change.__dict__ for change in self.offline_change_queue])
       QgsProject.instance().writeEntry("WateringSync", "Changes", serialized_changes)

    def load_offline_changes_from_project(self):
       success, serialized_changes = QgsProject.instance().readEntry("WateringSync", "Changes", "")
       if success:
           changes_list = json.loads(serialized_changes)
           for change_dict in changes_list:
               change = Change(**change_dict)
               self.offline_change_queue.append(change)
    
    def get_field_definitions(self):
        if not self.layer: return []
        fields = self.layer.fields()
        definitions = [field.name() for field in fields]
        return definitions[1:-1]
    
    def get_feature_by_id(self, id):
        expression = QgsExpression(f'"ID" = \'{id}\'')
        request = QgsFeatureRequest(expression)
        matching_features = self.layer.getFeatures(request)
        
        feature_ = None
        for feature in matching_features:
            feature_ = feature; break

        return feature_

    def handle_update_line_layer(self, change):
        ...
    
    def handle_update_point_layer(self, change):
        self.layer.startEditing()

        attrs = {}

        field_definitions = self.get_field_definitions()
        
        for i in range(len(field_definitions)):
            field_index = self.layer.fields().indexOf(field_definitions[i])
            attrs[field_index] = change.data[i]

        last_update_index = self.layer.fields().indexOf('lastUpdate')
        attrs[last_update_index] = WateringUtils.getDateTimeNow()

        feature_id = self.get_feature_by_id(change.feature_id).id()
        
        self.layer.dataProvider().changeAttributeValues({feature_id: attrs})

        new_geometry = QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1]))
        self.layer.dataProvider().changeGeometryValues({feature_id: new_geometry})

        self.layer.commitChanges()
    
    def handle_add_line_layer(self, change):
        feature = QgsFeature(self.layer.fields())
        
        feature.setAttribute("ID", change.feature_id)
        feature.setGeometry(change.data[-1])
        
        self.layer.startEditing()
        
        for i, field in enumerate(self.get_field_definitions()):
            feature[field] = change.data[i]

        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
         
        self.layer.addFeature(feature)
        self.layer.commitChanges()
        
    def handle_add_point_layer(self, change):
        feature = QgsFeature(self.layer.fields())
        feature.setAttribute("ID", change.feature_id)
        
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1])))
        
        self.layer.startEditing()
        
        for i, field in enumerate(self.get_field_definitions()):
            feature[field] = change.data[i]
        
        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
        
        self.layer.addFeature(feature)
        self.layer.commitChanges()
        