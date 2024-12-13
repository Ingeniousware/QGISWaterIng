import os
import requests

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
)
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

from ..watering_utils import WateringUtils


from ..repositoriesServerREST.abstractServerRESTRepository import abstractServerRESTRepository


class waterMeterNodeServerRESTRepository(abstractServerRESTRepository):

    def __init__(self, token, scenarioFK):
        """Constructor."""
        super(waterMeterNodeServerRESTRepository, self).__init__(token, scenarioFK)
        self.UrlGet = WateringUtils.getServerUrl() + "/api/v1/WaterMeter"
        self.UrlPost = WateringUtils.getServerUrl() + "/api/v1/WaterMeter"
        self.UrlPut = WateringUtils.getServerUrl() + "/api/v1/WaterMeter"
