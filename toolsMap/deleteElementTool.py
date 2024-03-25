#DeleteElementTool
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
        
        feature = found_features[0].mFeature
        layer = found_features[0].mLayer
        repo = self.scenarioUnitOfWork.getRepoByLayer(layer)
        print("repo: ", repo)
        layer.removeSelection()
            
        repo.deleteFeatureFromMapInteraction(feature)
        
        self.addFeatureToBackupLayer(feature, layer)
 
                        
    def deactivate(self):
        print("Clicked to unselect button of deleting element.")
        #self.layer.removeSelection()
    
    def addFeatureToBackupLayer(self, feature, layer):
        backup_layer_name = layer.name() + "_backup"
        backup_layer = QgsProject.instance().mapLayersByName(backup_layer_name)[0]
        backup_layer.startEditing()
        
        new_feat = QgsFeature(backup_layer.fields())
        new_feat.setGeometry(feature.geometry())
        new_feat.setAttributes(feature.attributes())
        lastUpdateIndex = new_feat.fields().indexFromName('lastUpdate')
        new_feat.setAttribute(lastUpdateIndex, WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
        backup_layer.addFeature(new_feat)
        
        print(f"adding feature {new_feat} to {backup_layer}")
            
        backup_layer.commitChanges()