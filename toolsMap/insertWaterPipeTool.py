from ..ActionManagement.insertPipeAction import insertPipeAction
from ..ActionManagement.insertNodeAction import insertNodeAction
from .insertAbstractTool import InsertAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsRubberBand, Qgis, QgsMapCanvas
from qgis.core import QgsPoint, QgsGeometry, QgsProject, QgsPointXY, QgsWkbTypes
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class InsertWaterPipeTool(InsertAbstractTool):

    def __init__(self, canvas, elementRepository, elementNodesRepository, actionManager, toolbarManager):
        super(InsertWaterPipeTool, self).__init__(canvas, elementRepository, actionManager) 
        self.toolbarManager =  toolbarManager         
        self.canvas = canvas
        self.point = None
        self.elementNodesRepository = elementNodesRepository
        self.rubberBand1 = None
        self.rubberBand2 = None
        self.clickedQgsPoints = [] 
        self.lastPoint = None 
        self.upnode = None
        self.downnode = None
        self.allPoints = []
        self.allLines = []


    def initialize(self):
        self.clickedQgsPoints = []        
        self.rubberBand1 = None
        self.rubberBand2 = None
        self.lastPoint = None 
    

    def canvasPressEvent(self, e):
        if not (e.button() == Qt.LeftButton): return

        pointTemp = self.toMapCoordinates(e.pos())
        point = QgsPoint(pointTemp.x(), pointTemp.y())
        self.clickedQgsPoints.append(point)
        self.allPoints.append(point)

        if e.modifiers() == Qt.ControlModifier:
            if not (self.lastPoint == None): 
                print('Adding vertex now')
                self.createFixedPartOfPipe(self.clickedQgsPoints)                
        else:
            #insert a demand node at the point where the user clicked
            action = insertNodeAction(self.elementNodesRepository, pointTemp.x(), pointTemp.y())         
            self.actionManager.execute(action)
            self.downnode = action.feature
            
            if len(self.clickedQgsPoints) > 1:
            #create a new pipe here
                print('Creating pipe now')
                if self.rubberBand1 is not None:
                    self.canvas.scene().removeItem(self.rubberBand1)
                if self.rubberBand2 is not None:
                    self.canvas.scene().removeItem(self.rubberBand2)

                actionPipe = insertPipeAction(self.elementRepository, self.clickedQgsPoints, self.upnode, self.downnode)         
                self.actionManager.execute(actionPipe)

                self.upnode = point
                self.clickedQgsPoints.clear()
                self.clickedQgsPoints.append(point)
                if not point in self.allPoints:
                    self.allPoints.append(point)
            else: 
                self.upnode = action.feature
            
        self.lastPoint = point

    def canvasMoveEvent(self, e):
        if not (self.lastPoint == None): 
            pointTemp = self.toMapCoordinates(e.pos())
            point = QgsPoint(pointTemp.x(), pointTemp.y())
            self.createMovingPartOfPipe(self.lastPoint, point)
            
    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            print("Esc pressed....insert pipe should be deactivated")
            if self.lastPoint == None:
                print("Fully deactivating pipes")
                self.deactivate()
            else:
                print("Restart pipes insertion")
                #self.clearDemandNodes()             
                #self.clearWaterPipes()
                self.clearVariables()

   
        
    
    def clearDemandNodes(self):
        layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        
        clicked_points_set = set((point.x(), point.y()) for point in self.allPoints)

        layer.startEditing()

        for feature in layer.getFeatures():
            feature_point = (feature.geometry().asPoint().x(), feature.geometry().asPoint().y())

            if feature_point in clicked_points_set:
                layer.deleteFeature(feature.id())
                self.elementRepository.deleteFeatureFromMapInteraction(feature)
                
        layer.commitChanges()
        
    def clearWaterPipes(self):
        layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]    
        
        # Start an edit session
        layer.startEditing()

        # Iterate over features in the layer
        for feature in layer.getFeatures():
            points_in_pipe = []
            lines = feature.geometry().asPolyline()
            flat_list = [(point.x(), point.y())  for sublist in lines for point in sublist]
            
            for line in feature.geometry().asPolyline():

                for point in line:
                    points_in_pipe.append((point.x(), point.y()))
                    
                if points_in_pipe == flat_list:
                    # Delete the feature
                    layer.deleteFeature(feature.id())
                    self.elementRepository.deleteFeatureFromMapInteraction(feature)
                    break  # Break out of the inner loop if a match is found

        # Commit changes
        layer.commitChanges()

    def clearVariables(self):
        self.clickedQgsPoints.clear()
        self.allPoints.clear()
        self.lastPoint = None
        
        if self.rubberBand1:  
            self.canvas.scene().removeItem(self.rubberBand1)
            self.rubberBand1 = None

        if self.rubberBand2:
            self.canvas.scene().removeItem(self.rubberBand2)     
            self.rubberBand2 = None
        
    def deactivate(self):
        print("deactivate insert pipe tool")
        self.toolbarManager.insertWaterPipeAction.setChecked(False)
        self.canvas.unsetMapTool(self.canvas.mapTool())
        self.clickedQgsPoints = []  
        
        if self.rubberBand1:  
            self.canvas.scene().removeItem(self.rubberBand1)
            self.rubberBand1 = None

        if self.rubberBand2:
            self.canvas.scene().removeItem(self.rubberBand2)     
            self.rubberBand2 = None
            
        self.lastPoint = None 


    def createFixedPartOfPipe(self, pointsFixedLine):
        if self.rubberBand1 is not None:
            self.canvas.scene().removeItem(self.rubberBand1)
        self.rubberBand1 = QgsRubberBand(self.canvas, Qgis.GeometryType.Line)
        self.rubberBand1.setToGeometry(QgsGeometry.fromPolyline(pointsFixedLine), None)
        self.rubberBand1.setColor(QColor(240, 40, 40))
        self.rubberBand1.setWidth(1)
        self.rubberBand1.setLineStyle(Qt.SolidLine)
        QgsMapCanvas().refresh()
    
    def createMovingPartOfPipe(self, lastPoint, movingPoint):
        pointsMovingLine = []
        pointsMovingLine.append(lastPoint)
        pointsMovingLine.append(movingPoint)
        if self.rubberBand2 is not None:
            self.canvas.scene().removeItem(self.rubberBand2)
        self.rubberBand2 = QgsRubberBand(self.canvas, Qgis.GeometryType.Line)
        self.rubberBand2.setToGeometry(QgsGeometry.fromPolyline(pointsMovingLine), None)
        self.rubberBand2.setColor(QColor(240, 40, 40))
        self.rubberBand2.setWidth(1)
        self.rubberBand2.setLineStyle(Qt.DashLine)
        QgsMapCanvas().refresh()