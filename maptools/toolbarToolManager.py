from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from functools import partial

from ..watering_utils import WateringUtils

from ..maptools.toolbarAction import toolbarAction

class toolbarToolManager():

    def __init__(self, toolbar, parentWindow, canvas):
        """Constructor."""
        self.activeMapTool = None
        self.canvas = canvas
        self.toolbar = toolbar
        self.parentWindow = parentWindow

        self.insertDemandNodeAction = None
        


    def initializeToolbarButtonActions(self):
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/node.png'
        self.insertDemandNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Demand Node'),
            callback=self.activateMapTool,
            toolbar = self.toolbar,
            parent=self.parentWindow)
        self.insertDemandNodeAction.setCheckable(True)        
        self.insertDemandNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())



    def addMapToolButtonAction(
        self,
        icon_path,
        text,
        callback,
        toolbar,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = toolbarAction(icon, text, parent)
        action.triggered.connect(partial(callback, action))
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            toolbar.addAction(action)

        """ if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action) """

        #actions.append(action)

        return action



    
    def activateMapTool(self, mapToolButtonAction):
        if (mapToolButtonAction.isChecked()):
            print("Setting Map Tool = ", mapToolButtonAction)
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False) 
            #this should be happening at updateActionScenarioStateOpen self.toolInsertDemandNode = InsertDemandNodeTool(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository) 
            print("maptool -> ", mapToolButtonAction.MapTool)
            self.canvas.setMapTool(mapToolButtonAction.MapTool)
            self.activeMapTool = mapToolButtonAction.MapTool
        else:
            self.canvas.unsetMapTool(mapToolButtonAction.MapTool)
            self.activeMapTool = None