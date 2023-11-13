from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from functools import partial
import os

from ..watering_utils import WateringUtils
from ..ui.watering_optimization import WaterOptimization
from ..maptools.toolbarAction import toolbarAction

class toolbarToolManager():

    def __init__(self, toolbar, parentWindow, canvas):
        """Constructor."""
        self.activeMapTool = None
        self.activeToolController = None
        self.canvas = canvas
        self.toolbar = toolbar
        self.parentWindow = parentWindow

        self.editElementsAction = None
        self.insertDemandNodeAction = None
        self.insertTankNodeAction = None
        self.insertWaterPipeAction = None
        self.insertReservoirNodeAction = None
        self.insertValveNodeAction = None
        self.insertPumpNodeAction = None
        self.insertSensorNodeAction = None
        self.toolDeleteElementAction = None
        self.selectElementAction = None
        self.openOptimizationManagerAction = None
        self.teste = None
        self.undoAction = None
        self.redoAction = None

    def initializeToolbarButtonActions(self):
        # Edit
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Edit.png'
        self.editElementsAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Edit Elements'),
            callback=self.activeControllerTool,
            toolbar = self.toolbar,
            parent=self.parentWindow)
        self.editElementsAction.setCheckable(True)        
        #self.editElementsAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.editElementsAction.toggled.connect(self.activateEditTool)
        
        # Optimization Tools        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/optimizationManager.png'
        self.optimizationToolsAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Optimization Tools'),
            callback=self.activeControllerTool,
            toolbar = self.toolbar,
            parent=self.parentWindow)
        self.optimizationToolsAction.setCheckable(True)        
        #self.editElementsAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.optimizationToolsAction.toggled.connect(self.activateOptimizationTool)
        
        # Demand Nodes
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/node.png'
        self.insertDemandNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Demand Node'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertDemandNodeAction.setCheckable(True)        
        self.insertDemandNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Tanks
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Tank.png'
        self.insertTankNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Tank Node'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertTankNodeAction.setCheckable(True)        
        self.insertTankNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Pipes
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/pipe.png'
        self.insertWaterPipeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Water Pipe'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertWaterPipeAction.setCheckable(True)        
        self.insertWaterPipeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Reservoirs
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Reservoir.png'
        self.insertReservoirNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Reservoir Node'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertReservoirNodeAction.setCheckable(True)        
        self.insertReservoirNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Valves
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Valve.png'
        self.insertValveNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Valve Node'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertValveNodeAction.setCheckable(True)        
        self.insertValveNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Pumps
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Pump.png'
        self.insertPumpNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Pump Node'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertPumpNodeAction.setCheckable(True)        
        self.insertPumpNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        
        # Undo
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Backward.png'
        self.undoAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'unDo'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.undoAction.setCheckable(False)        
        self.undoAction.setEnabled(False)

        # Redo
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Forward.png'
        self.redoAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'reDo'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.redoAction.setCheckable(False)        
        self.redoAction.setEnabled(False)

        # Delete Element
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/trash.png'
        self.toolDeleteElementAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Delete Element'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.toolDeleteElementAction.setCheckable(True)        
        self.toolDeleteElementAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        
        # Select 
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_select.png'
        self.selectElementAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Select Element'),
            callback=self.activateMapTool,
            toolbar = self.toolbar,
            parent=self.parentWindow)
        self.selectElementAction.setCheckable(True)
        self.selectElementAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Optimization
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_optimization.png'
        self.openOptimizationManagerAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Optimization'),
            callback=self.waterOptimization,
            toolbar = None,
            parent=self.parentWindow)
        self.openOptimizationManagerAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Sensors
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/sensor.png'
        self.insertSensorNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr(u'Add Sensor Node'),
            callback=self.activateMapTool,
            toolbar = None,
            parent=self.parentWindow)
        self.insertSensorNodeAction.setCheckable(True)        
        self.insertSensorNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

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
            if toolbar:
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
    
    def activeControllerTool(self, toolControllerAction):
        if (toolControllerAction.isChecked()):
            if(self.activeToolController is not None):
                self.activeToolController.setChecked(False) 
            self.activeToolController = toolControllerAction
        else:
            self.activeToolController = None
        
            
    def activateEditTool(self, checked):    
        editTools = [self.insertDemandNodeAction,
                         self.insertTankNodeAction,
                         self.insertWaterPipeAction,
                         self.insertReservoirNodeAction,
                         self.insertValveNodeAction,
                         self.insertPumpNodeAction,
                         self.toolDeleteElementAction, 
                         self.undoAction,
                         self.redoAction]
        
        if checked:
            for tool in editTools:
                self.toolbar.addAction(tool)
        else:
            for tool in editTools:
                self.toolbar.removeAction(tool)
                
                tool.setChecked(False)
                
                if tool.MapTool:
                    self.canvas.unsetMapTool(tool.MapTool)
                
    def activateOptimizationTool(self, checked):
                
        optimizationTools = [self.openOptimizationManagerAction,
                            self.insertSensorNodeAction,]
        
        if checked:
            for tool in optimizationTools:
                self.toolbar.addAction(tool)
        else:
            for tool in optimizationTools:
                self.toolbar.removeAction(tool)
                
                tool.setChecked(False)
                
                if tool.MapTool:
                    self.canvas.unsetMapTool(tool.MapTool)

    def waterOptimization(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"You must connect to WaterIng!"), level=1, duration=5)
        else:
            self.dlg = WaterOptimization()
            self.dlg.show()
            self.dlg.exec_()