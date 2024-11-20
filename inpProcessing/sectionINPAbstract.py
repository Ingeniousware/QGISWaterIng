from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsWkbTypes
from qgis.core import QgsGeometry, QgsCoordinateTransform, QgsPointXY


class sectionINPAbstract:
    def __init__(self, sourceCrs=QgsCoordinateReferenceSystem(4326)):
        # Constructor.
        self.sourceCrs = sourceCrs  # QgsCoordinateReferenceSystem(32614)
        self.destCrs = QgsCoordinateReferenceSystem(4326)

    def ProcessCoordinatesConvertion(self, out_file, line): ...

    def convert_to_coordinates(self, x_coord, y_coord):
        geometry = QgsGeometry.fromPointXY(QgsPointXY(x_coord, y_coord))
        transformed_geometry = geometry.transform(
            QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance())
        )

        longitude = geometry.asPoint().x()
        latitude = geometry.asPoint().y()

        return latitude, longitude
