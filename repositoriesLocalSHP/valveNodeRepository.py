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


class ValveNodeRepository(AbstractRepository):

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        super(ValveNodeRepository, self).__init__(token, scenarioFK)
        self.UrlGet = "/api/v1/WaterValve"
        self.StorageShapeFile = os.path.join(project_path, "watering_valves.shp")
        self.LayerName = "watering_valves"
        self.FileQml = project_path + "/" + self.LayerName + ".qml"
        self.field_definitions = None

        # Setting shapefile fields
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Z[m]", QVariant.Double),
            ("Diameter", QVariant.Double),
            ("minorLossC", QVariant.Double),
            ("initialSta", QVariant.Double),
            ("typeValvul", QVariant.Double),
            ("setting", QVariant.Double),
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
            "diameter",
            "minorLossCoef",
            "initialStatus",
            "typeValvule",
            "setting",
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
        super(ValveNodeRepository, self).initializeRepository(offline)
        self.openLayers(":/plugins/QGISPlugin_WaterIng/images/valveLayer.svg", 12)
        self.createBackupLayer()

    def setDefaultValues(self, feature):
        name = f"V-[{WateringUtils.generar_name_aleatorio()}]"
        description = "valve from QGIS"
        z = 0
        typeValve = 1
        minorLossCoef = 0
        diameter = 0
        initialStatus = 0
        temp = 0

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Z[m]", z)
        feature.setAttribute("Diameter", diameter)
        feature.setAttribute("minorLossC", minorLossCoef)
        feature.setAttribute("initialSta", initialStatus)
        feature.setAttribute("typeValvul", typeValve)

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
