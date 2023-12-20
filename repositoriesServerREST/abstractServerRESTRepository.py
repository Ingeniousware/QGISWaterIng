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
        self.currentCRS = QgsCoordinateReferenceSystem(4326)
        self.Response = None
        self.FieldDefinitions = None
        self.Attributes = None
        self.connectorToLocal = None

    def setConnectorToLocal(self, connector):
        self.connector = connector
        self.connector.serverRepository = self 
    
    def unsetConnectorToLocal(self):
        self.connector = None
        
    def getFromServer(self, elementJSON):
        ...


    def postToServer(self, elementJSON):
        """ print("posting -> ", elementJSON)
        print(self.ScenarioFK)
        print(self.Token) """
        data = {'scenarioKeyId': self.ScenarioFK}
        headers = {'Authorization': "Bearer {}".format(self.Token)} 
        response = requests.post(self.UrlPost, params=data, headers=headers, json=elementJSON)
        return response
        
    

    def putToServer(self, elementJSON, serverKeyId):
        """  print("putting -> ", elementJSON)
        print(self.ScenarioFK)
        print(self.Token) """
        data = {'scenarioKeyId': self.ScenarioFK}
        headers = {'Authorization': "Bearer {}".format(self.Token)} 
        response = requests.put(self.UrlPut + "/" + str(serverKeyId), params=data, headers=headers, json=elementJSON)
        return response
        

    def deleteFromServer(self, elementJSON):
        #data = {'scenarioKeyId': self.ScenarioFK}
        data = elementJSON["serverKeyId"]
        print("params = ", data)
        full_url = f'{self.UrlPost}/{data}'
        headers = {'Authorization': "Bearer {}".format(self.Token)} 
        response = requests.delete(full_url, headers=headers)
        print("delete responde text: ", response)
        print("url: ", response.request.url)