import requests
from ..watering_utils import WateringUtils

from qgis.core import (
    QgsField,
    QgsFields,
    QgsProject,
    QgsVectorLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsCoordinateReferenceSystem,
    QgsLayerTreeLayer,
)
from qgis.core import (
    QgsGeometry,
    QgsFeature,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsVectorFileWriter,
    QgsExpression,
    QgsFeatureRequest,
)
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor
from qgis.utils import iface


class abstractRepositoryConnectorSHPREST:

    def __init__(self, scenarioFK):
        """Constructor."""
        self.ScenarioFK = scenarioFK

    def getElementsFromServer(self):
        """params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        url = WateringUtils.getServerUrl() + self.UrlGet
        response =  requests.get(url, params=params_element,
                            headers={'Authorization': "Bearer {}".format(self.Token)})
        return response"""
        ...

    def addElementToServer(self, feature): ...

    def updateElementToServer(self): ...

    def removeElementFromServer(self): ...
