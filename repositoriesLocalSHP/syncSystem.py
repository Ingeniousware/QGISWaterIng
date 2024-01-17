from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest
from PyQt5.QtCore import QFileInfo, QDateTime, QDateTime, Qt
from ..watering_utils import WateringUtils
from collections import deque
import json

class Change:
    def __init__(self, layer_id, feature_id, change_type, data):
        self.layer_id = layer_id
        self.feature_id = feature_id
        self.change_type = change_type
        self.change_data = data
        self.timestamp = WateringUtils.getDateTimeNow()
        
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
        self.repositories = repositories

    def initializeRepository(self):
        ...

    def get_server_changes(self):
        print("reach")
        lastUpdate = WateringUtils.getLastUpdate()

        # Test variables
        test_lastUpdate = '2023-11-29T10:28:46.2756439Z'
        self.repositories = self.repositories.copy()
        self.repositories.pop(5)
        self.server_change_queue.clear()
        # End test variables
        
        for repo in self.repositories:
            response = repo.loadChanges(test_lastUpdate)
            if response._content:
                data = response.json()
                if data:
                    self.track_server_updates(repo, data)
                    
        print("change_queue: ", self.server_change_queue)

    def get_offline_changes(self):
        lastUpdate = WateringUtils.getLastUpdate()
        
        # Test variables
        test_lastUpdate = '2023-11-29T10:28:46.2756439Z'
        self.repositories = self.repositories.copy()
        self.repositories.pop(5)
        self.server_change_queue.clear()
        # End test variables
        
        for repo in self.repositories:
            self.track_offline_updates(repo, test_lastUpdate)
        
    def track_server_updates(self, repo, data):
        changes_list = repo.getServerUpdates(data)
        self.server_change_queue.extend(changes_list)
    
    def track_offline_updates(self, repo, lastUpdated):
        changes_list = repo.getOfflineUpdates(lastUpdated)
        self.offline_change_queue.extend(changes_list)
        
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
            if change.layer_id == repo.LayerName and repo.connectorToServer:
                repo.connectorToServer.addElementToServer(change.data)
                    
    def process_add_to_offline(self, change):
        print(f"Adding element in {change.layer_id}: {id} from server to offline")
        self.layer = QgsProject.instance().mapLayersByName(change.layer_id)[0]
        
        feature = QgsFeature(self.layer.fields())
        feature.setAttribute("ID", change.feature_id)
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1])))
        
        self.layer.startEditing()
        
        for i, field in enumerate(self.get_field_definitions()):
            feature[field] = change.data[i]
        
        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())
        
        self.layer.addFeature(feature)
        self.layer.commitChanges()
        
    def process_update_on_server(self, change):
        for repo in self.repositories:
            if change.layer_id == repo.LayerName and repo.connectorToServer:
                repo.connectorToServer.addElementToServer(change.data)

    def process_update_in_offline(self, change):
        print(f"Update element in {change.layer_id}: {id} from server to offline")
        
        self.layer = QgsProject.instance().mapLayersByName(change.layer_id)[0]
        self.layer.startEditing()

        attrs = {}

        field_definitions = self.get_field_definitions()
        
        for i in range(field_definitions):
            field_index = self.layer.fields().indexOf(field_definitions[i])
            attrs[field_index] = change.data[i]

        last_update_index = self.layer.fields().indexOf('lastUpdate')
        attrs[last_update_index] = WateringUtils.getDateTimeNow()

        feature = self.get_feature_by_id(change.id)
        
        self.layer.dataProvider().changeAttributeValues({feature.id(): attrs})

        new_geometry = QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1]))
        self.layer.dataProvider().changeGeometryValues({feature.id(): new_geometry})

        self.layer.commitChanges()
        
    def process_delete_on_server(self, change):
        for repo in self.repositories:
            if change.layer_id == repo.LayerName and repo.connectorToServer:
                repo.connectorToServer.removeElementFromServer(change.layer_id)
        
    def process_delete_in_offline(self, change):
        print(f"Delete element in {change.layer_id}: {id} from server to offline")
        
        self.layer = QgsProject.instance().mapLayersByName(change.layer_id)[0]
        id_to_delete = self.get_feature_by_id(change.feature_id)
        
        self.layer.startEditing()
        self.layer.deleteFeatures(id_to_delete)
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
        return [field.name() for field in fields]
    
    def get_feature_by_id(self, id):
        expression = f'"ID" = \'{id}\''
        request = QgsFeatureRequest(expression)
        matching_features = self.Layer.getFeatures(request)
        
        feature_id = None
        for feature in matching_features:
            feature_id = feature.id(); break

        return feature_id