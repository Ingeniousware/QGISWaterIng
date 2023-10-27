import os
import requests

from ..repositoryConnectorsSHPREST.abstractRepositoryConnectorSHPREST import abstractRepositoryConnectorSHPREST


from qgis.core import QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import QgsVectorFileWriter, QgsPointXY, QgsFeature, QgsSimpleMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase
from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5.QtGui import QColor

class waterDemandNodeConnectorSHPREST(abstractRepositoryConnectorSHPREST):

    def __init__(self):
        """Constructor."""
        super(waterDemandNodeConnectorSHPREST, self).__init__()    
        self.serverRepository = None  
        self.localRepository = None
        self.UrlGet = "/api/v1/DemandNode"

    def sendElementToServer(self, feature):
        #TODO create json and then call the post method of the server repository
        ...

    