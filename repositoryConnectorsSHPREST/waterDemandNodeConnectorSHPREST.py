import os
import requests

from repositoryConnectorsSHPREST.abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST


from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class waterDemandNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(waterDemandNodeConnectorSHPREST, self).__init__(token, scenarioFK)      
        self.UrlGet = "/api/v1/DemandNode"
