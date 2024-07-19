import os
from PyQt5.QtWidgets import QMessageBox
from qgis.gui import QgsMapToolIdentifyFeature
from ..watering_utils import WateringUtils

class SelectionReviewTool:

    def __init__(self, iface):
        self.iface = iface
        self.mapTool = None

    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.iface.tr(u"Error"), 
                self.iface.tr(u"Load a project scenario first in Download Elements!"), 
                level=1, duration=5
            )
            return

        if os.environ.get('TOKEN') is None:
            self.iface.messageBar().pushMessage(
                self.iface.tr("Error"), 
                self.iface.tr("You must login to WaterIng first!"), 
                level=1, duration=5
            )
            return

        print("Inside Selection Review")
        self.setupMapTool()

    def setupMapTool(self):
        mc = self.iface.mapCanvas()
        lyr = self.iface.activeLayer()
        if not lyr:
            self.iface.messageBar().pushMessage(
                self.iface.tr(u"Error"), 
                self.iface.tr(u"No active layer found!"), 
                level=1, duration=5
            )
            return

        self.mapTool = QgsMapToolIdentifyFeature(mc)
        self.mapTool.setLayer(lyr)
        mc.setMapTool(self.mapTool)
        self.mapTool.featureIdentified.connect(self.onFeatureIdentified)

    def onFeatureIdentified(self, feature):
        print("Feature selected: " + str(feature.id()))
