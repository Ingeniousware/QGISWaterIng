from ..ActionManagement.insertPipeAction import insertPipeAction
from ..ActionManagement.insertNodeAction import insertNodeAction
from .insertAbstractTool import InsertAbstractTool
from qgis.gui import QgsVertexMarker, QgsMapTool, QgsRubberBand, Qgis
from qgis.core import QgsPoint, QgsGeometry
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class InsertWaterPipeTool(InsertAbstractTool):

    def __init__(self, canvas, elementRepository, elementNodesRepository, actionManager):
        super(InsertWaterPipeTool, self).__init__(canvas, elementRepository, actionManager)          
        self.canvas = canvas
        self.point = None
        self.elementNodesRepository = elementNodesRepository
        self.rubberBand1 = None
        self.rubberBand2 = None
        self.clickedQgsPoints = [] 
        self.lastPoint = None 
        self.upnode = None
        self.downnode = None


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
            else: 
                self.upnode = action.feature
            
        self.lastPoint = point



    def canvasMoveEvent(self, e):
        if not (self.lastPoint == None): 
            pointTemp = self.toMapCoordinates(e.pos())
            point = QgsPoint(pointTemp.x(), pointTemp.y())
            self.createMovingPartOfPipe(self.lastPoint, point)

    
    
    def keyReleaseEvent (self, e):
        if e.key() == Qt.Key.Key_Escape:
            print("Esc pressed....insert pipe should be deactivated")



    def deactivate(self):
        print("deactivate insert pipe tool")
        self.clickedQgsPoints = []        
        self.rubberBand1 = None
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