from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5 import uic
import os
from ..watering_utils import WateringUtils
import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_waterBalance_dialog.ui'))

class WateringWaterBalance(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(WateringWaterBalance, self).__init__(parent)
        self.setupUi(self)
        self.ScenarioFK = WateringUtils.getScenarioId()
        self.token = os.environ.get('TOKEN')
        self.pushButton.clicked.connect(self.testFunction)
        
    def testFunction(self):
        print("Inside Water Balance")