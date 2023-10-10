import os
import requests
from .updateAbstractRepository import UpdateAbstractTool


class UpdateTankNode(UpdateAbstractTool):

    def __init__(self):
        """Constructor."""
        super(UpdateTankNode, self).__init__()      
        self.UrlGet = "/api/v1/TankNode"
        self.LayerName = "watering_tanks"
        self.Attributes = ["lastModified", "name", "description", "z", "initialLevel",
                           "minimumLevel","maximumLevel","minimumVolume", "nominalDiameter","canOverflow"]
        self.Fields = ['Last Mdf', 'Name', 'Descript', 'Z[m]', 'Init. Lvl', 'Min. Lvl', 
                        'Max. Lvl', 'Min. Vol.', 'Diameter', 'Overflow']
        self.initializeRepository()