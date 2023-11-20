import os
from ..ui.watering_INPImport import WateringINPImport
from ..watering_utils import WateringUtils


class ImportINPFileTool:

    def __init__(self, iface):
        self.iface = iface
    
    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5)
        else:
            self.dlg = WateringINPImport(self.iface)
            self.dlg.show()
            self.dlg.exec_()