from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject
import os

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

        # Dictionary mapping indices to combo boxes
        combo_boxes_map = {
            0: [self.nameComboBox, self.descriptionComboBox, self.zComboBox, self.demandComboBox, self.emitterComboBox],  # Demand Nodes
            1: [self.nameDMAcomboBox, self.descriptionDMAcomboBox],  # Water DMA
            2: [self.nameTankscomboBox, self.descriptionTankscomboBox, self.zTankscomboBox, self.initLevelCBox, self.minTankscomboBox, self.maxTankscomboBox, self.minVTankscomboBox, self.diameterTankscomboBox],  # Tanks
            3: [self.sensorNameCBox, self.sensorDescriptCBox, self.sensorZCBox],  # Sensors
            4: [self.pipeNameCBox, self.pipeDescriptCBox, self.pipeRoughCBox, self.pipeDiameterCBox, self.pipeLengthCBox],  # Pipes
            5: [self.namePumpscomboBox, self.descriptionPumpscomboBox, self.zPumpscomboBox, self.modelCBox, self.relativeSpeedcBox],  # Pumps
            6: [self.reservoirNameCBox, self.reservoirDescriptCBox, self.reservoirZCBox, self.reservoirHeadCBox],  # Reservoirs
            7: [self.valveNameCBox, self.valveDescriptCBox, self.valveZCBox, self.valveDiameterCBox, self.typeValveCBox, self.valveSettingCBox, self.minorValveCBox, self.valveStatusCBox]  # Valves
        }
        combo_boxes = combo_boxes_map.get(index)

        if combo_boxes is None:
            return

        for cBox in combo_boxes:
            cBox.clear()
            cBox.addItem("No match")
            for field in fields:
                cBox.addItem(field.name())

    def checkUserControlState(self):
        index = self.LayerTypeCBox.currentIndex()
        # Hide all tabs
        for i in range(self.TabWidget.count()):
            self.TabWidget.setTabVisible(i, False)
        # Show the tab corresponding to the current index
        if 0 <= index < self.TabWidget.count():
            self.TabWidget.setTabVisible(index, True)

    def get_cBox_index(self):
        layer_name = "New Layer"
        cBox_index = self.LayerTypeCBox.currentIndex()
        
        processing_functions = {
            0: ImportDemandNodesShp.shpProcessing,
            1: ImportDMAShp.shpProcessing,
            2: ImportTanksShp.shpProcessing,
            3: ImportSensorsShp.shpProcessing,
            4: ImportPipesShp.shpProcessing,
            5: ImportPumpsShp.shpProcessing,
            6: ImportReservoirShp.shpProcessing,
            7: ImportValvesShp.shpProcessing
        }
        processing_function = processing_functions.get(cBox_index)
        
        if processing_function:
            processing_function(self, layer_name)    
        self.close()