# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
from PyQt5.QtCore import QTimer

from ..watering_utils import WateringUtils
from ..updateTools.updateAbstractRepository import UpdateAbstractTool
from ..updateTools.updateTanks import UpdateTankNode

class WateringUpdate():
    def __init__(self):
        UpdateTankNode()
        
        