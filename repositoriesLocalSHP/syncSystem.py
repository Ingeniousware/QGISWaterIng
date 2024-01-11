from ..watering_utils import WateringUtils
from collections import deque

class Change:
    def __init__(self, feature_id, change_type, timestamp=None):
        self.feature_id = feature_id
        self.change_type = change_type
        self.timestamp = WateringUtils.getDateTimeNow()
        
class WateringSync:
    def __init__(self):
        self.change_queue = deque()

    def trackChange(self, feature_id, change_type):
        change = Change(feature_id, change_type)
        self.change_queue.append(change)

    def synchronize(self):
        while self.change_queue:
            change = self.change_queue.popleft()
            self.processChange(change)

    def processChange(self, change):
        if change.change_type == "add":
            self.process_add(change)
        elif change.change_type == "update":
            self.process_update(change)
        elif change.change_type == "delete":
            self.process_delete(change)
        else:
            print(f"Unknown change type: {change.change_type}")

    def process_add(self, change):
        ...

    def process_update(self, change):
        ...

    def process_delete(self, change):
        ...
        