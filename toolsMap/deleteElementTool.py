#DeleteElementTool
from ..watering_utils import WateringUtils

from qgis.gui import QgsMapTool, QgsMapToolIdentify
from qgis.utils import iface
from qgis.core import QgsProject, QgsFeature, QgsVectorLayer


class DeleteElementTool(QgsMapTool):

    def __init__(self, canvas):
        self.canvas = canvas
        self.point = None
        self.layer = None
        self.test = QgsMapToolIdentify(self.canvas)
        super().__init__(self.canvas)
        print("Init at Tool Delete Element")

    def canvasPressEvent(self, e):
        
        found_features = self.test.identify(e.x(), e.y(), self.test.TopDownStopAtFirst, self.test.VectorLayer)
        
        if found_features:
            self.layer = found_features[0].mLayer
            self.layer.removeSelection()
            
            print("Clicled layer: ", self.layer)
            print(found_features[0].mFeature.attributes())
            feature_ids = [f.mFeature.id() for f in found_features]
            
            
            backup_layer_name = self.layer.name() + "_backup"
            key = "backup_layer_path" + self.layer.name()
            
            backup_layer_path = WateringUtils.getProjectMetadata(key)
            val = WateringUtils.getProjectMetadata("backup_layer_pathwatering_demand_nodes")
            #print("SECOND ATTEMPT: ", val)
            #print("BAKCUP LAYER PATH: ", backup_layer_path, "key: ",key, "backup_layer_name: ", backup_layer_name)
            #backup_layer = QgsVectorLayer(backup_layer_path, backup_layer_name, "ogr") 
            backup_layer = QgsProject.instance().mapLayersByName(backup_layer_name)[0]
            #backup_layer = QgsProject.instance().mapLayersByName(backup_layer_name)[0]

            backup_layer.startEditing()
            
            for ident in found_features:
                # 'ident' is a QgsFeatureIdentifyResult
                feature = ident.mFeature

                # Create a new feature for the target layer
                new_feat = QgsFeature(backup_layer.fields())
                new_feat.setGeometry(feature.geometry())
                new_feat.setAttributes(feature.attributes())
                lastUpdateIndex = new_feat.fields().indexFromName('lastUpdate')
                new_feat.setAttribute(lastUpdateIndex, WateringUtils.getDateTimeNow())
                # Add the new feature to the target layer
                backup_layer.addFeature(new_feat)
                
                print(f"adding feature {new_feat} to {backup_layer}")
                
            backup_layer.commitChanges()
            
            """#adding backup layer
            QgsProject.instance().addMapLayer(backup_layer)"""
            
            # Start an undo block in case we want to revert this operation
            self.layer.startEditing()

            # Delete the features with the collected IDs
            success = self.layer.deleteFeatures(feature_ids)

            if success:
                # If features were successfully deleted, save the changes
                self.layer.commitChanges()
            else:
                # If the delete was not successful, roll back the changes
                self.layer.rollBack()
                                  
    def deactivate(self):
        print("Clicked to unselect button of deleting element.")
        #self.layer.removeSelection()
    