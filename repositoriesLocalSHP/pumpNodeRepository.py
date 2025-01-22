import os
import requests

from ..watering_utils import WateringUtils
from .abstract_repository import AbstractRepository

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)
from qgis.core import (
    QgsVectorFileWriter,
    QgsPointXY,
    QgsFeature,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsSvgMarkerSymbolLayer,
)
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor


class PumpNodeRepository(AbstractRepository):

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        super(PumpNodeRepository, self).__init__(token, scenarioFK)
        self.UrlGet = "/api/v1/WaterPump"
        self.StorageShapeFile = os.path.join(project_path, "watering_pumps.shp")
        self.LayerName = "watering_pumps"
        self.FileQml = project_path + "/" + self.LayerName + ".qml"
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Model FK", QVariant.String),
            ("Rel. Speed", QVariant.Double),
            ("Up-NodeKey", QVariant.String),
            ("Down-NodeKey", QVariant.String),
            ("Up-Node", QVariant.String),
            ("Down-Node", QVariant.String),
            ("lastUpdate", QVariant.String),
        ]

        self.features = [
            "lng",
            "lat",
            "serverKeyId",
            "lastModified",
            "name",
            "description",
            "z",
            "pumpModelFK",
            "relativeSpeed",
            "upstreamNodeKeyId",
            "downstreamNodeKeyId",
            "upstreamNode",
            "downstreamNode",
        ]

        self.LayerType = "Point?crs="
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None
        self.currentLayer = None

    def initializeRepository(self, offline):
        super(PumpNodeRepository, self).initializeRepository(offline)
        self.openLayers(":/plugins/QGISPlugin_WaterIng/images/pumpLayer.svg", 12)
        self.createBackupLayer()

    def setDefaultValues(self, feature):
        name = f"P-[{WateringUtils.generar_name_aleatorio()}]"
        description = "pump from QGIS"
        z = 0
        model = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        speed = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)
        feature.setAttribute("Model FK", model)
        feature.setAttribute("Rel. Speed", speed)

    def setElementSymbol(self, layer, path_to_gif, layer_size):
        renderer = layer.renderer()
        symbol = renderer.symbol()

        symbol_layer = QgsSvgMarkerSymbolLayer(path_to_gif, layer_size)
        # symbol_layer.setFrameRate(1)
        symbol.changeSymbolLayer(0, symbol_layer)

        symbol.setColor(self.Color)
        if self.StrokeColor:
            symbol.symbolLayer(0).setStrokeColor(self.StrokeColor)
        layer.triggerRepaint()
