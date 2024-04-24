import os
from ..watering_utils import WateringUtils
from qgis.core import Qgis, QgsProject, QgsCoordinateTransformContext, QgsCoordinateReferenceSystem

class NetworkReviewTool:

    def __init__(self, iface):
        self.iface = iface
    
    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.iface.tr(u"Error"), self.iface.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
            return
            
        if os.environ.get('TOKEN') is None:
            self.iface.messageBar().pushMessage(self.iface.tr("Error"), self.iface.tr("You must login to WaterIng first!"), level=1, duration=5)
            return

        field_waterM_nodeFK = 'Unconected'
        unnconnected = 1

        pipe_layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]
        node_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]

        WateringUtils.createNewColumn(self, "watering_demand_nodes", field_waterM_nodeFK)

        node_layer.startEditing()
        
        field_index = node_layer.fields().indexFromName(field_waterM_nodeFK)

        pipe_features = list(pipe_layer.getFeatures())
        node_features = list(node_layer.getFeatures())
        
        for feature_x in pipe_features:
            pipe_geom = feature_x.geometry()
            #pipe_name = feature_x['ID']

            for feature_y in node_features:
                node_geom = feature_y.geometry()
                #node_name = feature_y['ID']

                if not node_geom.disjoint(pipe_geom):
                    #print(f'{node_name} intersects with {pipe_name}')
                    continue
                else:
                    # Calculate distance between point and MultiLineString
                    distance = node_geom.distance(pipe_geom)
                
                    if distance <= 5:
                        node_layer.dataProvider().changeAttributeValues({feature_y.id(): {field_index: unnconnected}})
                        #print(f"Distance between {node_name} and {pipe_name} is {distance:.2f} units")
        
        node_layer.commitChanges()
        WateringUtils.changeColors(self,node_layer,field_waterM_nodeFK)

        self.iface.messageBar().pushMessage("Success", "Successfully identified unconnected nodes!", level=Qgis.Success, duration=6)
        print("Update completed.")
