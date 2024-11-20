import os
import requests
import json
import uuid
from .abstract_repository import AbstractRepository
from ..watering_utils import WateringUtils

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsLayerTreeLayer,
)
from qgis.core import (
    QgsVectorFileWriter,
    QgsPointXY,
    QgsFeature,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsSymbol,
    edit,
)
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from qgis.utils import iface


class PipeNodeRepository(AbstractRepository):

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        super(PipeNodeRepository, self).__init__(token, scenarioFK)
        self.UrlGet = "/api/v1/WaterPipe"
        self.StorageShapeFile = os.path.join(project_path, "watering_pipes.shp")
        self.LayerName = "watering_pipes"
        self.FileQml = project_path + "/" + self.LayerName + ".qml"
        # Setting shapefile fields
        self.field_definitions = [
            ("ID", QVariant.String),
            ("Last Mdf", QVariant.String),
            ("Name", QVariant.String),
            ("Descript", QVariant.String),
            ("Diameter", QVariant.Double),
            ("Length", QVariant.Double),
            ("Rough.A", QVariant.Double),
            ("C(H.W.)", QVariant.Double),
            ("Up-Node", QVariant.String),
            ("Down-Node", QVariant.String),
            ("lastUpdate", QVariant.String),
        ]

        self.features = [
            "serverKeyId",
            "lastModified",
            "name",
            "description",
            "diameterInt",
            "length",
            "roughnessAbsolute",
            "roughnessCoefficient",
            "nodeUpName",
            "nodeDownName",
        ]

        self.LayerType = "LineString?crs="
        self.Color = QColor.fromRgb(23, 61, 108)
        self.StrokeColor = None

    def initializeRepository(self):
        super(PipeNodeRepository, self).initializeRepositoryStreamingData()
        self.openLayers(None, 0.7)
        self.createBackupLayer()

    def setElementSymbol(self, layer, layer_symbol, layer_size):
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setColor(QColor.fromRgb(13, 42, 174))
        symbol_layer.setWidth(layer_size)
        layer.renderer().setSymbol(symbol)
        layer.saveNamedStyle(self.FileQml)
        layer.triggerRepaint()

    def createElementLayerFromServerStreamingResponse(self, response):
        fields = self.setElementFields(self.field_definitions)
        self.currentLayer = QgsVectorLayer("LineString?crs=" + self.destCrs.authid(), "Line Layer", "memory")
        self.currentLayer.dataProvider().addAttributes(fields)
        self.currentLayer.updateFields()

        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                chunk_data = chunk.decode("utf-8")

                self.buffer += chunk_data

                json_objects = self.buffer.split("\n")

                self.buffer = json_objects.pop()

                for obj in json_objects:
                    if obj.strip():
                        data = json.loads(obj)
                        for feature in data["data"]:
                            self.addElementFromJSON(feature)

        if self.buffer.strip():
            data = json.loads(self.buffer)
            for feature in data["data"]:
                self.addElementFromJSON(feature)

    def addElementFromJSON(self, elementJSON):
        try:
            element = [elementJSON[field] for field in self.features]

            feature = QgsFeature(self.currentLayer.fields())
            points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in elementJSON["vertices"]]
            geometry = QgsGeometry.fromPolylineXY(points)
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)

            self.currentLayer.startEditing()

            print(element)
            for i in range(len(self.field_definitions) - self.numberLocalFieldsOnly):
                feature.setAttribute(self.field_definitions[i][0], element[i])

            feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))
            self.currentLayer.addFeature(feature)

            self.currentLayer.commitChanges()

        except ValueError:
            print("Error->" + ValueError)

    # When layer already exists
    def addElementFromSignalR(self, elementJSON):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        id_already_in_offline = self.hasFeatureWithId(layer, elementJSON["serverKeyId"])

        if not id_already_in_offline:
            element = [elementJSON[field] for field in self.features]

            layer.startEditing()

            feature = QgsFeature(layer.fields())
            points = [QgsPointXY(vertex["lng"], vertex["lat"]) for vertex in elementJSON["vertices"]]
            geometry = QgsGeometry.fromPolylineXY(points)
            geometry.transform(QgsCoordinateTransform(self.sourceCrs, self.destCrs, QgsProject.instance()))
            feature.setGeometry(geometry)

            for i in range(len(self.field_definitions) - 1):
                feature.setAttribute(self.field_definitions[i][0], element[i])

            lastUpdatedForSignalR = WateringUtils.get_last_updated(self.ScenarioFK)
            feature.setAttribute("lastUpdate", lastUpdatedForSignalR)

            layer.addFeature(feature)
            layer.commitChanges()
            layer.triggerRepaint()

    def AddNewElementFromMapInteraction(self, vertexs, upnode, downnode):
        layer = QgsProject.instance().mapLayersByName(self.LayerName)[0]
        layer.startEditing()

        feature = QgsFeature(layer.fields())
        points = [QgsPointXY(vertex.x(), vertex.y()) for vertex in vertexs]
        g = QgsGeometry.fromPolylineXY(points)
        feature.setGeometry(g)

        self.setDefaultValues(feature)

        feature.setAttribute("lastUpdate", WateringUtils.getDateTimeNow())
        feature.setAttribute("Last Mdf", WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))

        id = str(uuid.uuid4())
        temp_id = id[:10]

        feature.setAttribute("ID", temp_id)

        layer.addFeature(feature)
        layer.commitChanges()

        if self.connectorToServer:
            self.connectorToServer.addElementToServer(feature)

        return feature

    def getPipeTransformedCrs(self, point):
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")  # Web Mercator

        geom = QgsGeometry.fromPointXY(point)
        geom.transform(QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance()))
        point = geom.asPoint()

        return QgsPointXY(point.x(), point.y())

    def setDefaultValues(self, feature):
        name = "pipeName"
        description = "pipe from QGIS"
        diameter = 0.2
        roughnessAbsolute = 0.045
        roughnessCoefficient = 150

        feature.setAttribute("Name", name)
        feature.setAttribute("Descript", description)
        feature.setAttribute("Diameter", diameter)
        feature.setAttribute("Rough.A", roughnessAbsolute)
        feature.setAttribute("C(H.W.)", roughnessCoefficient)
