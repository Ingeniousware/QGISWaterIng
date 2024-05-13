import os
from ..watering_utils import WateringUtils
from ..ui.watering_shpImport import WateringShpImport

class ImportShapeFileTool:

    def __init__(self, iface):
        self.iface = iface
    
    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5)
        else:
            self.dlg = WateringShpImport(self.iface)
            self.dlg.show()
            self.dlg.exec_()