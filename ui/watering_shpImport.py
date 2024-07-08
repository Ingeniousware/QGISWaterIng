# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import os
from ..watering_utils import WateringUtils

from ..shpProcessing.abstractShpImport import AbstractShpImport
from ..shpProcessing.waterDemandNodes import ImportDemandNodesShp
from ..shpProcessing.waterPipes import ImportPipesShp
from ..shpProcessing.waterReservoirs import ImportReservoirShp
from ..shpProcessing.waterTanks import ImportTanksShp
from ..shpProcessing.waterValves import ImportValvesShp
from ..shpProcessing.waterSensors import ImportSensorsShp
from ..shpProcessing.waterDMA import ImportDMAShp
from ..shpProcessing.waterPumps import ImportPumpsShp

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_shpImport_dialog.ui'))


class WateringShpImport(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self,iface,parent=None):
        """Constructor."""
        super(WateringShpImport, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.TabWidget.hide()
        self.LayerTypeCBox.setPlaceholderText("Please select the layer type you wish to import")
        self.add_items_to_combobox()
        self.LayerTypeCBox.currentIndexChanged.connect(self.checkUserControlState)
        self.uploadShpFile.setEnabled(False)
        self.loadLayerButton.clicked.connect(self.addSelected_Layer)
        self.uploadShpFile.clicked.connect(self.get_cBox_index)
        
    def add_items_to_combobox(self):
        layer_types = ["Demand Nodes", "Water DMA", "Tanks", "Sensors", "Pipes", "Pumps", "Reservoirs", "Valves"]
        self.LayerTypeCBox.clear()
        for item in layer_types:
            self.LayerTypeCBox.addItem(item)

    def addSelected_Layer(self):
        self.file_path = self.newSHPDirectory.filePath()
        AbstractShpImport.addSelected_Layer(self, self.file_path)
        self.loadLayerButton.setEnabled(False)

    def attribute_matcher(self):
        layer = QgsProject.instance().mapLayersByName("New Layer")[0]
        fields = layer.fields()
        index = self.LayerTypeCBox.currentIndex()
        if index == 0:  # Demand Nodes
            comboBoxes = [
                (self.nameComboBox),
                (self.descriptionComboBox),
                (self.zComboBox),
                (self.demandComboBox),
                (self.emitterComboBox)
            ]
        elif index == 1: # Water DMA
            comboBoxes = [
                (self.nameDMAcomboBox),
                (self.descriptionDMAcomboBox)
            ]
        elif index == 2: # Tanks
            comboBoxes = [
                (self.nameTankscomboBox),
                (self.descriptionTankscomboBox),
                (self.zTankscomboBox),
                (self.initLevelCBox),
                (self.minTankscomboBox),
                (self.maxTankscomboBox),
                (self.minVTankscomboBox),
                (self.diameterTankscomboBox)
            ]
        elif index == 3: # Sensors
            comboBoxes = [
                (self.sensorNameCBox),
                (self.sensorDescriptCBox),
                (self.sensorZCBox)
            ]
        elif index == 4: # Pipes
            comboBoxes = [
                (self.pipeNameCBox),
                (self.pipeDescriptCBox),
                (self.pipeRoughCBox),
                (self.pipeDiameterCBox),
                (self.pipeLengthCBox)
            ]
        elif index == 5: # Pumps
            comboBoxes = [
                (self.namePumpscomboBox),
                (self.descriptionPumpscomboBox),
                (self.zPumpscomboBox),
                (self.modelCBox),
                (self.relativeSpeedcBox)
            ]
        elif index == 6: # Reservoirs
            comboBoxes = [
                (self.reservoirNameCBox),
                (self.reservoirDescriptCBox),
                (self.reservoirZCBox),
                (self.reservoirHeadCBox)
            ]
        elif index == 7: # Valves
            comboBoxes = [
                (self.valveNameCBox),
                (self.valveDescriptCBox),
                (self.valveZCBox),
                (self.valveDiameterCBox),
                (self.typeValveCBox),
                (self.valveSettingCBox),
                (self.minorValveCBox),
                (self.valveStatusCBox)
            ]
        else:
            return
        for cBox in comboBoxes:
            cBox.clear()
            cBox.addItem("No match")
            for field in fields:
                cBox.addItem(field.name())

    def checkUserControlState(self):
        index = self.LayerTypeCBox.currentIndex()
        for i in range(self.TabWidget.count()):
            self.TabWidget.setTabVisible(i, False)
        if index == 0:
            self.TabWidget.setTabVisible(0, True)
        elif index == 1:
            self.TabWidget.setTabVisible(1, True)
        elif index == 2:
            self.TabWidget.setTabVisible(2, True)
        elif index == 3:
            self.TabWidget.setTabVisible(3, True)
        elif index == 4:
            self.TabWidget.setTabVisible(4, True)
        elif index == 5:
            self.TabWidget.setTabVisible(5, True)
        elif index == 6:
            self.TabWidget.setTabVisible(6, True)
        elif index == 7:
            self.TabWidget.setTabVisible(7, True)

    def get_cBox_index(self):
        layer_name = "New Layer"
        cBox_index = self.LayerTypeCBox.currentIndex()
        if cBox_index == 0:
            ImportDemandNodesShp.shpProcessing(self, layer_name)
            print("The layer imported is of Demand Nodes")
        elif cBox_index == 1:
            ImportDMAShp.shpProcessing(self, layer_name)
            print("The layer imported is of Water DMA")
        elif cBox_index == 2: 
            ImportTanksShp.shpProcessing(self, layer_name)
            print("The layer imported is of Tanks")
        elif cBox_index == 3: 
            ImportSensorsShp.shpProcessing(self, layer_name)
            print("The layer imported is of Sensors")
        elif cBox_index == 4: 
            ImportPipesShp.shpProcessing(self, layer_name)
            print("The layer imported is of Pipes")
        elif cBox_index == 5: 
            ImportPumpsShp.shpProcessing(self, layer_name)
            print("The layer imported is of Pumps")
        elif cBox_index == 6: 
            ImportReservoirShp.shpProcessing(self, layer_name)
            print("The layer imported is of Reservoirs")
        elif cBox_index == 7: 
            ImportValvesShp.shpProcessing(self, layer_name)
            print("The layer imported is of Valves")
        self.close()