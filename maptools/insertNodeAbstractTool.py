from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker, QgsMapTool
from PyQt5.QtGui import QColor
from qgis.PyQt import uic, QtWidgets

class InsertNodeAbstractTool(QgsMapTool):

    def __init__(self, canvas, action):
        
        self.action = action
        self.canvas = canvas
        
        super().__init__(self.canvas)

        self.point = None
        
        self.canvas.setMapTool(self)
        
        self.action.triggered.connect(self.endProcedure)

    def canvasPressEvent(self, e):
        
        self.point = self.toMapCoordinates(e.pos())
        
        print(self.point.x(), self.point.y())

        m = QgsVertexMarker(self.canvas)

        m.setCenter(self.point)

        m.setColor(QColor(0,255,0))

        m.setIconSize(5)

        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X

        m.setPenWidth(3)

        self.endProcedure()
        
    def endProcedure(self):
    
        self.canvas.unsetMapTool(self)