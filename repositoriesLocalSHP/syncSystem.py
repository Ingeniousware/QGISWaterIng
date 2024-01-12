from qgis.core import QgsProject
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
        
class WateringSync:
    def __init__(self):
        self.server_change_queue = deque()
        self.offline_change_queue = deque()
        
        self.change_handlers = {
            "add_server": self.process_add_to_server,
            "add_offline": self.process_add_to_offline,
            "update_server": self.process_update_on_server,
            "update_offline": self.process_update_in_offline,
            "delete_server": self.process_delete_on_server,
            "delete_offline": self.process_delete_in_offline
        }
        
    def track_server_change(self, feature_id, change_type):
        change = Change(feature_id, change_type)
        self.server_change_queue.append(change)

    def track_offline_change(self, feature_id, change_type):
        change = Change(feature_id, change_type)
        self.offline_change_queue.append(change)
        
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
        ...

    def process_add_to_offline(self, change):
        ...
        
    def process_update_on_server(self, change):
        ...

    def process_update_in_offline(self, change):
        ...
        
    def process_delete_on_server(self, change):
        ...
        
    def process_delete_in_offline(self, change):
        ...
        
    def save_offline_changes_to_project(self):
       serialized_changes = json.dumps([change.__dict__ for change in self.offline_change_queue])
       QgsProject.instance().writeEntry("WateringSync", "Changes", serialized_changes)
