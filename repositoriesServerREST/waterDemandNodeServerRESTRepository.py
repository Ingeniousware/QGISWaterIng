import os
import requests

from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor


from ..repositoriesServerREST.abstractServerRESTRepository import abstractServerRESTRepository

class waterDemandNodeServerRESTRepository(abstractServerRESTRepository):

    def __init__(self,token, scenarioFK):
        """Constructor."""
        super(waterDemandNodeServerRESTRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/DemandNode"
        


