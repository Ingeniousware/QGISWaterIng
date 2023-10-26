import requests
from ..watering_utils import WateringUtils

from qgis.core import QgsField, QgsFields, QgsProject, QgsVectorLayer, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.core import QgsGeometry, QgsFeature, QgsCoordinateTransform, QgsPointXY, QgsVectorFileWriter, QgsExpression, QgsFeatureRequest
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from qgis.utils import iface

class abstractServerRESTRepository():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.sourceCrs = QgsCoordinateReferenceSystem(4326)
        self.Response = None
        self.FieldDefinitions = None
        self.Attributes = None

    def getFromServer(self, elementJSON):
        ...

    def postToServer(self, elementJSON):
        ...

    def putToServer(self, elementJSON):
        ...

    def deleteFromServer(self, elementJSON):
        ...