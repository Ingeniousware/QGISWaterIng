from ..watering_utils import WateringUtils
from collections import deque

class Change:
    def __init__(self, layer_id, feature_id, change_type, timestamp=None):
        self.layer_id = layer_id
        self.feature_id = feature_id
        self.change_type = change_type
        self.timestamp = WateringUtils.getDateTimeNow()
        
class WateringSync:
    def __init__(self):
        self.change_queue = deque()
        self.change_handlers = {
            "add": self.process_add,
            "update": self.process_update,
            "delete": self.process_delete
        }
        
    def trackChange(self, feature_id, change_type):
        change = Change(feature_id, change_type)
        self.change_queue.append(change)

    def synchronize(self):
        while self.change_queue:
            change = self.change_queue.popleft()
            self.processChange(change)

    def processChange(self, change):
        try:
            process_method = self.change_handlers[change.change_type]
            process_method(change)
        except KeyError:
            print(f"Unknown change type: {change.change_type}")

    def process_add(self, change):
        ...

    def process_update(self, change):
        ...

    def process_delete(self, change):
        ...
        