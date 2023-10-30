from ..ActionManagement.insertNodeAction import insertNodeAction
from .insertAbstractTool import InsertAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsProject
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, QEvent, Qt

class InsertDemandNodeTool(InsertAbstractTool):
    def __init__(self, canvas, elementRepository, actionManager):
        super(InsertDemandNodeTool, self).__init__(canvas, elementRepository, actionManager)  
        print("Init at Insert Demand Node")
        if (QgsProject.instance().mapLayersByName("watering_demand_nodes") is not None) and len(QgsProject.instance().mapLayersByName("watering_demand_nodes")) != 0:
          self.demandNodeLayer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
          self.toolFindIdentify = QgsMapToolIdentify(self.canvas)

          
    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())
        
        #print(self.point.x(), self.point.y(), " ---- ", e.x(), e.y())

        #this can be needed for the case later when a node is substituted by another type of node
        #found_features = self.toolFindIdentify.identify(e.x(), e.y(), [self.demandNodeLayer], QgsMapToolIdentify.TopDownAll)
        #if len(found_features) > 0:
                #element has been found
        #        ...

        #TODO eliminate the direct call to the AddNewElementFromMapInteraction in the next line when the action and action manager are implemented and working
        #self.elementRepository.AddNewElementFromMapInteraction(self.point.x(), self.point.y())
        action = insertNodeAction(self.elementRepository, self.point.x(), self.point.y())         
        self.actionManager.execute(action)
            


    def deactivate(self):
        print("deactivate insert demand node tool")


    