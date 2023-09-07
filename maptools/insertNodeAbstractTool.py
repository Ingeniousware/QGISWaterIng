from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker


class InsertNodeAbstractTool(QgsMapToolEmitPoint):

    def __init__(self, canvas):

        self.canvas = canvas

        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.point = None



    def canvasPressEvent(self, e):

        self.point = self.toMapCoordinates(e.pos())

        print(self.point.x(), self.point.y())

        m = QgsVertexMarker(self.canvas)

        m.setCenter(self.point)

        m.setColor(QColor(0,255,0))

        m.setIconSize(5)

        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X

        m.setPenWidth(3)