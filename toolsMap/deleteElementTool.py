# DeleteElementTool
from ..watering_utils import WateringUtils

from qgis.gui import QgsMapTool, QgsMapToolIdentify
from qgis.utils import iface
from qgis.core import QgsProject, QgsFeature, QgsVectorLayer


class DeleteElementTool(QgsMapTool):

    def __init__(self, canvas, scenarioUnitOfWork, actionManager, toolbarToolManager):
        self.canvas = canvas
        self.scenarioUnitOfWork = scenarioUnitOfWork
        self.actionManager = actionManager
        self.toolbarToolManager = toolbarToolManager
        self.point = None
        self.layer = None
        self.test = QgsMapToolIdentify(self.canvas)
        super().__init__(self.canvas)
        print("Init at Tool Delete Element")

    def canvasPressEvent(self, e):

        found_features = self.test.identify(e.x(), e.y(), self.test.TopDownStopAtFirst, self.test.VectorLayer)

        if not found_features:
            WateringUtils.error_message("No features found!")
            return

        feature = found_features[0].mFeature
        layer = found_features[0].mLayer
        repo = self.scenarioUnitOfWork.getRepoByLayer(layer)
        print("repo: ", repo)
        layer.removeSelection()

        repo.deleteFeatureFromMapInteraction(feature)

        WateringUtils.add_feature_to_backup_layer(feature, layer)
        WateringUtils.write_sync_operation(layer, feature, WateringUtils.OperationType.DELETE)

    def deactivate(self):
        print("Clicked to unselect button of deleting element.")
        # self.layer.removeSelection()
