from qgis.gui import QgsVertexMarker, QgsMapTool
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, QEvent, Qt

class InsertAbstractTool(QgsMapTool):

    def __init__(self, canvas, elementRepository, actionManager):
        
        #self.action = action
        self.canvas = canvas
        super().__init__(self.canvas)
        self.point = None
        self.elementRepository = elementRepository
        self.actionManager = actionManager
            
    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())
        
        print(self.point.x(), self.point.y())

        m = QgsVertexMarker(self.canvas)
        m.setCenter(self.point)
        m.setColor(QColor(0,255,0))
        m.setIconSize(5)
        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        m.setPenWidth(3)
    
    def deactivate(self):
        print("deactivate abstract tool")
    