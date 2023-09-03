import requests


class AbstractRepository():

    def __init__(self, token, scenarioFK, urlget):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        

    def loadElements(self):
        params_element = {'ScenarioFK': "{}".format(self.ScenarioFK)}
        return request.get(self.UrlGet, params=params_element, headers={'Authorization': "Bearer {}".format(self.token)})  

    def setElementFields(self):
        ...

    def createElementShp(self):
        ...

    def setElementSymbol(self):
        ...