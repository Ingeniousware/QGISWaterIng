import os
import requests
from .abstract_serverRepository import AbstractServerRepository

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class waterDemandNodeServerRESTRepository(AbstractServerRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(waterDemandNodeServerRESTRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/DemandNode"
