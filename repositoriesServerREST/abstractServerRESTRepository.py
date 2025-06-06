import requests
from ..watering_utils import WateringUtils
from concurrent.futures import ThreadPoolExecutor, as_completed

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


class abstractServerRESTRepository:

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

    def getFromServer(self, elementJSON): ...

    def postToServer(self, elementJSON):
        """print("posting -> ", elementJSON)
        print(self.ScenarioFK)
        print(self.Token)"""
        data = {"scenarioKeyId": self.ScenarioFK}
        headers = {"Authorization": "Bearer {}".format(self.Token)}
        error_message = "Failed to send element to server. Try again later."
        response = WateringUtils.send_post_request(self.UrlPost, data, elementJSON, headers, error_message)
        return response

    def make_post_request(self, session, url, data, headers, params):
        try:
            response = session.post(url, params=params, json=data, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"

    def make_put_request(self, session, url, data, headers, params, serverKeyId):
        try:
            response = session.put(url + "/" + str(serverKeyId), params=params, json=data, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"

    def make_delete_request(self, session, url, headers, serverKeyId):
        try:
            response = session.delete(url + "/" + str(serverKeyId), headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"

    def postMultipleElements(self, list_of_elementsJSON):
        params = {"scenarioKeyId": self.ScenarioFK}
        headers = {"Authorization": "Bearer {}".format(self.Token)}

        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(self.make_post_request, session, self.UrlPost, data[0], headers, params)
                    for data in list_of_elementsJSON
                ]

    def putMultipleElements(self, list_of_elementsJSON):
        params = {"scenarioKeyId": self.ScenarioFK}
        headers = {"Authorization": "Bearer {}".format(self.Token)}

        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(
                        self.make_put_request, session, self.UrlPut, data, headers, params, data[0]["serverKeyId"]
                    )
                    for data in list_of_elementsJSON
                ]

    def deleteMultipleElements(self, list_of_elementsJSON):
        params = {"scenarioKeyId": self.ScenarioFK}
        headers = {"Authorization": "Bearer {}".format(self.Token)}
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(self.make_delete_request, session, self.UrlPost, headers, key)
                    for key in list_of_elementsJSON
                ]

    def putToServer(self, elementJSON, serverKeyId):
        """print("putting -> ", elementJSON)
        print(self.ScenarioFK)
        print(self.Token)"""
        data = {"scenarioKeyId": self.ScenarioFK}
        headers = {"Authorization": "Bearer {}".format(self.Token)}
        response = requests.put(self.UrlPut + "/" + str(serverKeyId), params=data, headers=headers, json=elementJSON)
        return response

    def deleteFromServer(self, elementJSON):
        # data = {'scenarioKeyId': self.ScenarioFK}
        data = elementJSON["serverKeyId"]
        print("params = ", data)
        full_url = f"{self.UrlPost}/{data}"
        headers = {"Authorization": "Bearer {}".format(self.Token)}
        response = requests.delete(full_url, headers=headers)
        print("response: ", response)
        print("delete responde text: ", response.text)
        print("url: ", response.request.url)

    def updateFeatureAttributes(self, data, layer): ...
