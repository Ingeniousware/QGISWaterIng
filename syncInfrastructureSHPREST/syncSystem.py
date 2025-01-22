from qgis.core import (
    QgsField, QgsProject, QgsCoordinateReferenceSystem, QgsGeometry, QgsWkbTypes, 
    QgsFeature, edit, QgsPointXY, QgsExpression, QgsFeatureRequest, QgsCoordinateTransform
)
from PyQt5.QtCore import QVariant

from ..watering_utils import WateringUtils
from collections import deque
import json
import uuid
import os
import requests

class WateringSync:
    def __init__(self, token, project_path, scenario_fk, repositories):
        self.server_change_queue = deque()
        self.offline_change_queue = deque()
        
        self.change_handlers = {
            "add_from_server": self._handle_server_add,
            "update_from_server": self._handle_server_update,
            "delete_from_server": self._handle_server_delete,
        }

        self.token = token
        self.project_path = project_path
        self.scenario_fk = scenario_fk
        self.repositories = repositories
        self.source_crs = QgsCoordinateReferenceSystem(4326)
        self.dest_crs = QgsCoordinateReferenceSystem(3857)
        self.sync_halted = False
        self.layer = None
        self.project_fk = None

    def synchronize(self):
        last_updated = WateringUtils.get_last_updated(self.scenario_fk)
        self.sync_halted = False

        if not self._upload_local_project():
            self.sync_halted = True
            return False

        if last_updated <= "2000-01-01T00:00:00.0000000Z":
            self._reset_element_ids(self.repositories)

        self._fetch_offline_changes(last_updated)
        self._fetch_server_changes(last_updated)
        self._process_server_changes()
        self._process_offline_changes()

        if not self.sync_halted:
            self._finalize_sync()
            return True
        return False

    def _upload_local_project(self):
        self.token = os.environ.get("TOKEN")
        projects_json_path = WateringUtils.get_projects_json_path()
        if not os.path.exists(projects_json_path):
            return True

        with open(projects_json_path, "r") as f:
            projects_data = json.load(f)

        project_key_id = WateringUtils.getProjectId()
        if project_key_id not in projects_data:
            return True

        project_entry = projects_data[project_key_id]
        if project_entry.get("localOnly", False):
            success, response = self._create_server_project(project_key_id, project_entry.get("name", "Unnamed Project"))
            if not success or not response:
                return False

            server_project_key_id = response.json().get("serverKeyId")
            if not server_project_key_id:
                return False

            projects_data[project_key_id].update({
                "localOnly": False,
                "serverKeyId": server_project_key_id
            })
        else:
            server_project_key_id = project_entry.get("serverKeyId")
            if not server_project_key_id:
                return True

        scenarios = project_entry.get("scenarios", {})
        for scn_key, scn_value in scenarios.items():
            if scn_value.get("localOnly", False):
                if not self._create_server_scenario(scn_key, server_project_key_id, scn_value.get("name", "Unnamed Scenario")):
                    return False
                projects_data[project_key_id]["scenarios"][scn_key]["localOnly"] = False

        with open(projects_json_path, "w") as f:
            json.dump(projects_data, f, indent=4)
        return True

    def _create_server_project(self, local_key, name):
        project_data = {
            "keyId": str(local_key),
            "name": str(name),
            "description": "Project created via QGIS offline->online sync."
        }

        url = f"{WateringUtils.getServerUrl()}/api/v1/ProjectWaterNetworks"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = WateringUtils.send_post_request(url, None, project_data, headers, "Failed to create project")

        if response and response.status_code == 200:
            self.project_fk = local_key
            return True, response

        return False, None

    def _create_server_scenario(self, local_key, server_project_key, name):
        scenario_data = {
            "keyId": str(local_key),
            "serverKeyId": str(local_key),
            "fkWaterProject": str(server_project_key),
            "name": str(name),
            "description": "Scenario created via QGIS offline->online sync."
        }

        url = f"{WateringUtils.getServerUrl()}/api/v1/ScenarioWaterNetwork"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(url, headers=headers, json=scenario_data)

        if response and response.status_code == 200:
            self.scenario_fk = local_key
            return True

        return False

    def _fetch_server_changes(self, last_updated):
        self.server_change_queue.clear()
        for repo in self.repositories:
            repo.scenario_fk = self.scenario_fk
            response = repo.loadChanges(last_updated)
            if response.status_code == 200 and response._content:
                try:
                    data = response.json()
                    if data:
                        self._track_server_updates(repo, data)
                except ValueError:
                    continue

    def _fetch_offline_changes(self, last_updated):
        self.offline_change_queue.clear()
        for repo in self.repositories:
            self._track_offline_updates(repo, last_updated)

    def _track_server_updates(self, repo, data):
        changes = repo.getServerUpdates(data)
        self.server_change_queue.extend(changes)

    def _track_offline_updates(self, repo, last_updated):
        repo.getOfflineUpdates(last_updated)

    def _process_server_changes(self):
        while self.server_change_queue and not self.sync_halted:
            change = self.server_change_queue.popleft()
            self._process_change(change)

    def _process_offline_changes(self):
        WateringUtils.setProjectMetadata("elementsPostingInProgress", "true")
        for repo in self.repositories:
            if not repo.connectorToServer:
                self.sync_halted = True
                break
            repo.initMultiElementsPosting()
        WateringUtils.setProjectMetadata("elementsPostingInProgress", "default text")

    def _process_change(self, change):
        handler = self.change_handlers.get(change.change_type)
        if handler:
            handler(change)

    def _handle_server_add(self, change):
        self.layer = change.layer_id
        feature = self._create_feature(change)
        
        self.layer.startEditing()
        self.layer.addFeature(feature)
        self.layer.commitChanges()

    def _handle_server_update(self, change):
        self.layer = change.layer_id
        self.layer.startEditing()

        attrs = self._prepare_attributes(change)
        feature = self._get_feature_by_id(change.feature_id)
        if not feature:
            self.layer.commitChanges()
            return

        feature_id = feature.id()
        self.layer.dataProvider().changeAttributeValues({feature_id: attrs})
        self._update_geometry(change, feature_id)
        self.layer.commitChanges()

    def _handle_server_delete(self, change):
        self.layer = change.layer_id
        feature = self._get_feature_by_id(change.feature_id)
        if feature:
            self.layer.startEditing()
            self.layer.deleteFeature(feature.id())
            self.layer.commitChanges()

    def _create_feature(self, change):
        feature = QgsFeature(self.layer.fields())
        feature.setAttribute("ID", change.feature_id)
        
        if self.layer.geometryType() == QgsWkbTypes.PointGeometry:
            point = QgsPointXY(change.data[-1][0], change.data[-1][1])
            feature.setGeometry(QgsGeometry.fromPointXY(point))
        elif self.layer.geometryType() == QgsWkbTypes.LineGeometry:
            line_points = [QgsPointXY(pt["lng"], pt["lat"]) for pt in change.data[-1]]
            geometry = QgsGeometry.fromPolylineXY(line_points)
            geometry.transform(QgsCoordinateTransform(self.source_crs, self.dest_crs, QgsProject.instance()))
            feature.setGeometry(geometry)

        for i, field in enumerate(self._get_field_names()):
            feature[field] = change.data[i]

        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
        return feature

    def _prepare_attributes(self, change):
        attrs = {}
        field_names = self._get_field_names()
        
        for i, field in enumerate(field_names):
            field_index = self.layer.fields().indexOf(field)
            attrs[field_index] = change.data[i]
            
        last_update_index = self.layer.fields().indexOf("lastUpdate")
        attrs[last_update_index] = WateringUtils.getDateTimeNow()
        return attrs

    def _update_geometry(self, change, feature_id):
        if self.layer.name() == "watering_pipes":
            points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in change.data[-1]]
            if points:
                geometry = QgsGeometry.fromPolylineXY(points)
                transform = QgsCoordinateTransform(self.source_crs, self.dest_crs, QgsProject.instance())
                geometry.transform(transform)
                self.layer.dataProvider().changeGeometryValues({feature_id: geometry})
        else:
            geometry = QgsGeometry.fromPointXY(QgsPointXY(change.data[-1][0], change.data[-1][1]))
            self.layer.dataProvider().changeGeometryValues({feature_id: geometry})

    def _get_field_names(self):
        if not self.layer:
            return []
        return [field.name() for field in self.layer.fields()][1:-1]

    def _get_feature_by_id(self, feature_id):
        expression = QgsExpression(f"\"ID\" = '{feature_id}'")
        request = QgsFeatureRequest(expression)
        features = self.layer.getFeatures(request)
        return next(features, None)

    def _reset_element_ids(self, layers):
        for layer_info in layers:
            layer = QgsProject.instance().mapLayersByName(layer_info.LayerName)[0]
            if not layer or not layer.isValid():
                continue

            with edit(layer):
                if "ID" not in [field.name() for field in layer.fields()]:
                    layer.dataProvider().addAttributes([QgsField("ID", QVariant.String)])
                    layer.updateFields()

                for feature in layer.getFeatures():
                    feature.setAttribute(feature.fieldNameIndex("ID"), str(uuid.uuid4())[:10])
                    layer.updateFeature(feature)
            layer.commitChanges()

    def _finalize_sync(self):
        WateringUtils.clear_added_from_signalr(self.scenario_fk)
        WateringUtils.update_last_updated(self.scenario_fk)
        WateringUtils.clear_sync_file()