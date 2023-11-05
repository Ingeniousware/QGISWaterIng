# -*- coding: utf-8 -*-

# Import QGis
from qgis.core import QgsProject, Qgis
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from qgis.gui import QgsMapCanvas, QgsMapToolIdentify, QgsVertexMarker
from qgis.utils import iface
from .syncInfrastructureSHPREST.syncManagerSHPREST import syncManagerSHPREST

# Initialize Qt resources from file resources.py
from .resources import *
import pickle
import time
import shutil
import json

# Import the code for the dialog

from .maptools.toolbarToolManager import toolbarToolManager
from .maptools.insertSensorNodeToolPlacement import InsertSensorNodeToolPlacement
from .maptools.InsertDemandNodeTool import InsertDemandNodeTool
from .maptools.insertTankNodeTool import InsertTankNodeTool
from .maptools.insertReservoirNodeTool import InsertReservoirNodeTool
from .maptools.insertWaterPipeTool import InsertWaterPipeTool
from .maptools.insertValveNodeTool import InsertValveNodeTool
from .maptools.insertPumpNodeTool import InsertPumpNodeTool
from .maptools.insertSensorNodeTool import InsertSensorNodeTool
from .maptools.selectNodeTool import SelectNodeTool
from .ui.watering_load import WateringLoad
from .ui.watering_login import WateringLogin
from .ui.watering_analysis import WateringAnalysis
from .ui.watering_optimization import WaterOptimization
from .watering_utils import WateringUtils
from .ui.watering_datachannels import WateringDatachannels
from .ui.watering_INPImport import WateringINPImport
from .ActionManagement.actionManager import actionManager

from signalrcore.hub_connection_builder import HubConnectionBuilder

import os.path


class QGISPlugin_WaterIng:
    """QGIS Plugin Implementation."""
    
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'watering_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Watering API Connection')
        self.insertSensorAction = None
        self.insertTankNodeAction = None
        self.insertReservoirNodeAction = None
        self.insertValveNodeAction = None
        self.insertPumpNodeAction = None
        self.insertSensorNodeAction = None
        self.selectElementAction = None
        self.readAnalysisAction = None
        self.canvas = iface.mapCanvas()
        QgsProject.instance().cleared.connect(self.updateActionStateClose)
        QgsProject.instance().readProject.connect(self.updateActionStateOpen)


        self.readMeasurementsAction = None
                                                  
        # Toolbar
        self.activeMapTool = None
        self.toolbar = self.iface.addToolBar("WaterIng Toolbar")
        self.toolbar.setObjectName("QGISWatering")
        self.toolbar.setVisible(True)

        self.hub_connection = None
        # Dock
        self.analysisDockPanel = WateringAnalysis(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.analysisDockPanel)

        self.scenarioUnitOFWork = None
        self.syncManager = None
        self.actionManager = None
        self.toolbarToolManager = None

    

    # noinspection PyMethodMayBeStatic
    def tr(self, message, context = "QGISPlugin_WaterIng"):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(context, message)


    def add_action(
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
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        self.toolbarToolManager = toolbarToolManager(self.toolbar, self.iface.mainWindow(), self.canvas)

        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_login.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Watering Login'),
            callback=self.addLogin,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_load_elements.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Download Elements'),
            callback=self.addLoad,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Import.png'
        self.importFileINP = self.add_action(
            icon_path,
            text=self.tr(u'Import INP File'),
            callback=self.importINPFile,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.importFileINP.setEnabled(not WateringUtils.isScenarioNotOpened())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_update.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Update Elements'),
            callback=self.updateElements,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_analysis.png'
        self.readAnalysisAction = self.add_action(
            icon_path,
            text=self.tr(u'Water Network Analysis', 'QGISWaterIng'),
            #text=self.tr(u'Water Network Analysis'),
            callback=self.waterAnalysis,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())     
        self.readAnalysisAction.setEnabled(not WateringUtils.isScenarioNotOpened())   

        """ for the moment we are not going to use this select
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_select.png'
        self.selectElementAction = self.add_action(
            icon_path,
            text=self.tr(u'Select Element'),
            callback=self.activateToolSelectMapElement,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.selectElementAction.setCheckable(True)
        self.selectElementAction.setEnabled(not WateringUtils.isScenarioNotOpened()) """
                
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_optimization.png'
        self.openOptimizationManagerAction = self.add_action(
            icon_path,
            text=self.tr(u'Optimization'),
            callback=self.waterOptimization,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.openOptimizationManagerAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        
        """ icon_path = ':/plugins/QGISPlugin_WaterIng/images/sensor.png'
        self.insertSensorAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Sensor Optimization'),
            callback=self.activateToolInsertSensorPlacement,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertSensorAction.setCheckable(True)        
        self.insertSensorAction.setEnabled(not WateringUtils.isScenarioNotOpened()) """




        self.toolbarToolManager.initializeToolbarButtonActions()
        


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Tank.png'
        self.insertTankNodeAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Tank Node'),
            callback=self.activateToolInsertTankNode,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertTankNodeAction.setCheckable(True)        
        self.insertTankNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/pipe.png'
        self.insertWaterPipeAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Water Pipe'),
            callback=self.activateToolInsertWaterPipe,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertWaterPipeAction.setCheckable(True)        
        self.insertWaterPipeAction.setEnabled(not WateringUtils.isScenarioNotOpened())


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Reservoir.png'
        self.insertReservoirNodeAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Reservoir Node'),
            callback=self.activateToolInsertReservoirNode,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertReservoirNodeAction.setCheckable(True)        
        self.insertReservoirNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Valve.png'
        self.insertValveNodeAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Valve Node'),
            callback=self.activateToolInsertValveNode,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertValveNodeAction.setCheckable(True)        
        self.insertValveNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Pump.png'
        self.insertPumpNodeAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Pump Node'),
            callback=self.activateToolInsertPumpNode,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertPumpNodeAction.setCheckable(True)        
        self.insertPumpNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/sensor.png'
        self.insertSensorNodeAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Sensor Node'),
            callback=self.activateToolInsertSensorNode,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertSensorNodeAction.setCheckable(True)        
        self.insertSensorNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Backward.png'
        self.undoAction = self.add_action(
            icon_path,
            text=self.tr(u'unDo'),
            callback=self.executeUnDoAction,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.undoAction.setCheckable(False)        
        self.undoAction.setEnabled(False)


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Forward.png'
        self.redoAction = self.add_action(
            icon_path,
            text=self.tr(u'reDo'),
            callback=self.executeReDoAction,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.redoAction.setCheckable(False)        
        self.redoAction.setEnabled(False)


        icon_path = ':/plugins/QGISPlugin_WaterIng/images/Monitoring.png'
        self.readMeasurementsAction = self.add_action(
            icon_path,
            text=self.tr(u'Get Measurements'),
            callback=self.getMeasurements,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.readMeasurementsAction.setEnabled(not WateringUtils.isScenarioNotOpened())
                                                       
        #adding a standard action to our toolbar
        self.iface.actionIdentify().setIcon(QIcon(':/plugins/QGISPlugin_WaterIng/images/selection.png'))

        self.toolIdentify = QgsMapToolIdentify(self.canvas)
        self.toolIdentify.setAction(self.iface.actionIdentify())
        self.toolbar.addAction(self.iface.actionIdentify())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_cache.png'
        self.deleteCacheFromWaterIng = self.add_action(
            icon_path,
            text=self.tr(u'Clean cache'),
            callback=self.cleanCacheMessageBox,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())

        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Watering API Connection', 'WateringLogin'),
                action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar

    def addLogin(self):
        self.dlg = WateringLogin()
        self.dlg.show()
        self.dlg.exec_()

        
    def addLoad(self):
        #self.InitializeProjectToolbar()
        print("calling watering load dialog")
        self.dlg = WateringLoad()
        self.dlg.show() 
        if (self.dlg.exec_() == 1):
            self.scenarioUnitOFWork = self.dlg.myScenarioUnitOfWork   
            if not self.dlg.Offline:          
                print(self.scenarioUnitOFWork)
                self.actionManager = actionManager(os.environ.get('TOKEN'), self.scenarioUnitOFWork.scenarioFK, self.setActiveStateUndo, self.setActiveStateRedo)
                self.syncManager = syncManagerSHPREST(os.environ.get('TOKEN'), self.scenarioUnitOFWork.scenarioFK)
                self.syncManager.connectScenarioUnitOfWorkToServer(self.scenarioUnitOFWork)
                self.updateActionScenarioStateOpen()
                
                
                server_url = WateringUtils.getServerUrl() + "/hubs/waternetworkhub"

                self.hub_connection = HubConnectionBuilder()\
                    .with_url(server_url, options={"verify_ssl": False, 
                                                "headers": {'Authorization': "Bearer {}".format(os.environ.get('TOKEN'))}}) \
                    .with_automatic_reconnect({
                            "type": "interval",
                            "keep_alive_interval": 10,
                            "intervals": [1, 3, 5, 6, 7, 87, 3]
                        }).build()

                #self.hub_connection.on_open(lambda: print("connection opened and handshake received ready to send messages"))
                self.hub_connection.on_open(self.createOnlineConnectionChannels)
                self.hub_connection.on_close(lambda: print("connection closed"))
                self.hub_connection.on_error(lambda data: print(f"An exception was thrown closed{data.error}"))
                    
                self.hub_connection.on("UPDATE_IMPORTED", self.processINPImportUpdate)

                
                self.hub_connection.start()

            print("before updating options")                
            self.updateActionStateOpen()
             
                
    def importINPFile(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5)
        else:
            self.dlg = WateringINPImport(self.iface)
            self.dlg.show()
            self.dlg.exec_()

                
    def waterAnalysis(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"You must connect to WaterIng!"), level=1, duration=5)
        else:
            self.analysisDockPanel.initializeRepository()
            self.analysisDockPanel.show()
            #self.dlg.exec_()
            
    def waterOptimization(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"You must connect to WaterIng!"), level=1, duration=5)
        else:
            self.dlg = WaterOptimization()
            self.dlg.show()
            self.dlg.exec_()

    
    def activateToolInsertSensorPlacement(self):
        if (self.insertSensorAction.isChecked()):
            print("Setting Map Tool = toolInsertSensorNodePlacement")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False) 
            #this should be happening at updateActionScenarioStateOpen self.toolInsertSensorNodePlacement = InsertSensorNodeTool(self.canvas) 
            self.canvas.setMapTool(self.toolInsertSensorNodePlacement)
            self.activeMapTool = self.toolInsertSensorNodePlacement
        else:
            self.canvas.unsetMapTool(self.toolInsertSensorNodePlacement)
            self.activeMapTool = None  


        """  def activateToolInsertDemandNode(self):
        if (self.insertDemandNodeAction.isChecked()):
            print("Setting Map Tool = toolInsertDemandNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False) 
            #this should be happening at updateActionScenarioStateOpen self.toolInsertDemandNode = InsertDemandNodeTool(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository) 
            self.canvas.setMapTool(self.toolInsertDemandNode)
            self.activeMapTool = self.toolInsertDemandNode
        else:
            self.canvas.unsetMapTool(self.toolInsertDemandNode)
            self.activeMapTool = None """

    
    def activateToolInsertTankNode(self):
        if (self.insertTankNodeAction.isChecked()):
            print("Setting Map Tool = toolInsertTankNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False)
            #this should be happening at updateActionScenarioStateOpen self.toolInsertTankNode = InsertTankNodeTool(self.canvas, self.scenarioUnitOFWork.tankNodeRepository) 
            self.canvas.setMapTool(self.toolInsertTankNode)
            self.activeMapTool = self.toolInsertTankNode
        else:
            self.canvas.unsetMapTool(self.toolInsertTankNode)
            self.activeMapTool = None


    def activateToolInsertWaterPipe(self):
        if (self.insertWaterPipeAction.isChecked()):
            print("Setting Map Tool = insertWaterPipeAction")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False) 
            self.canvas.setMapTool(self.toolInsertWaterPipe)
            self.activeMapTool = self.toolInsertWaterPipe
        else:
            self.canvas.unsetMapTool(self.toolInsertWaterPipe)
            self.activeMapTool = None
    

    def activateToolInsertReservoirNode(self):
        if (self.insertReservoirNodeAction.isChecked()):
            print("Setting Map Tool = toolInsertReservoirNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False)
            #this should be happening at updateActionScenarioStateOpen self.toolInsertReservoirNode = InsertReservoirNodeTool(self.canvas, self.scenarioUnitOFWork.reservoirNodeRepository) 
            self.canvas.setMapTool(self.toolInsertReservoirNode)
            self.activeMapTool = self.toolInsertReservoirNode
        else:
            self.canvas.unsetMapTool(self.toolInsertReservoirNode)
            self.activeMapTool = None


    def activateToolInsertValveNode(self):
        if (self.insertValveNodeAction.isChecked()):
            print("Setting Map Tool = toolInsertValveNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False)
            #this should be happening at updateActionScenarioStateOpen self.toolInsertValveNode = InsertValveNodeTool(self.canvas, self.scenarioUnitOFWork.valveNodeRepository) 
            self.canvas.setMapTool(self.toolInsertValveNode)
            self.activeMapTool = self.toolInsertValveNode
        else:
            self.canvas.unsetMapTool(self.toolInsertValveNode)
            self.activeMapTool = None

    
    def activateToolInsertPumpNode(self):
        if (self.insertPumpNodeAction.isChecked()):
            print("Setting Map Tool = toolInsertPumpNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False)
            #this should be happening at updateActionScenarioStateOpen self.toolInsertPumpNode = InsertPumpNodeTool(self.canvas, self.scenarioUnitOFWork.pumpNodeRepository) 
            self.canvas.setMapTool(self.toolInsertPumpNode)
            self.activeMapTool = self.toolInsertPumpNode
        else:
            self.canvas.unsetMapTool(self.toolInsertPumpNode)
            self.activeMapTool = None

    
    def activateToolInsertSensorNode(self):
        if (self.insertSensorNodeAction.isChecked()):
            print("Setting Map Tool = toolInsertSensorNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False)
            #this should be happening at updateActionScenarioStateOpen self.toolInsertSensorNode = InsertSensorNodeTool(self.canvas, self.scenarioUnitOFWork.sensorNodeRepository) 
            self.canvas.setMapTool(self.toolInsertSensorNode)
            self.activeMapTool = self.toolInsertSensorNode
        else:
            self.canvas.unsetMapTool(self.toolInsertSensorNode)
            self.activeMapTool = None


    def activateToolSelectMapElement(self):
        #For sensors optimization
        if (self.selectElementAction.isChecked()):
            print("Setting Map Tool = toolSelectNode")
            if (self.activeMapTool is not None):
                if(self.activeMapTool.action() is not None):
                    self.canvas.unsetMapTool(self.activeMapTool)  
                    self.activeMapTool.action().setChecked(False)  
            self.toolSelectNode = SelectNodeTool(self.canvas) 
            self.canvas.setMapTool(self.toolSelectNode)
            self.activeMapTool = self.toolSelectNode
            self.insertSensorAction.setChecked(False)  
        else:
            self.canvas.unsetMapTool(self.toolSelectNode)
            self.activeMapTool = None



    def executeUnDoAction(self):
        self.actionManager.undoAction()

    def executeReDoAction(self):
        self.actionManager.redoAction()


    def updateActionScenarioStateOpen(self):
        """ self.toolInsertSensorNodePlacement = InsertSensorNodeToolPlacement(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager)              
        self.toolInsertSensorNodePlacement.setAction(self.insertSensorAction)
        self.insertSensorAction.setEnabled(True) """
            
        toolInsertDemandNode = InsertDemandNodeTool(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager)
        toolInsertDemandNode.setAction(self.toolbarToolManager.insertDemandNodeAction)
        self.toolbarToolManager.insertDemandNodeAction.setCurrentTool(toolInsertDemandNode)
        self.toolbarToolManager.insertDemandNodeAction.setEnabled(True)

        self.toolInsertTankNode = InsertTankNodeTool(self.canvas, self.scenarioUnitOFWork.tankNodeRepository, self.actionManager)
        self.toolInsertTankNode.setAction(self.insertTankNodeAction)
        self.insertTankNodeAction.setEnabled(True)

        self.toolInsertReservoirNode = InsertReservoirNodeTool(self.canvas, self.scenarioUnitOFWork.reservoirNodeRepository, self.actionManager)
        self.toolInsertReservoirNode.setAction(self.insertReservoirNodeAction)
        self.insertReservoirNodeAction.setEnabled(True)

        self.toolInsertWaterPipe = InsertWaterPipeTool(self.canvas, self.scenarioUnitOFWork.pipeNodeRepository, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager)
        self.toolInsertWaterPipe.setAction(self.insertWaterPipeAction)
        self.insertWaterPipeAction.setEnabled(True)

        self.toolInsertValveNode = InsertValveNodeTool(self.canvas, self.scenarioUnitOFWork.valveNodeRepository, self.actionManager)
        self.toolInsertValveNode.setAction(self.insertValveNodeAction)
        self.insertValveNodeAction.setEnabled(True)

        self.toolInsertPumpNode = InsertPumpNodeTool(self.canvas, self.scenarioUnitOFWork.pumpNodeRepository, self.actionManager)
        self.toolInsertPumpNode.setAction(self.insertPumpNodeAction)
        self.insertPumpNodeAction.setEnabled(True)

        self.toolInsertSensorNode = InsertSensorNodeTool(self.canvas, self.scenarioUnitOFWork.sensorNodeRepository, self.actionManager)
        self.toolInsertSensorNode.setAction(self.insertSensorNodeAction)
        self.insertSensorNodeAction.setEnabled(True)
        
              
    def updateActionStateOpen(self):
        #self.cleanMarkers()
        print("before entering if")
        if WateringUtils.isWateringProject():
            self.toolSelectNode = SelectNodeTool(self.canvas)  #(self.canvas)
            print("before setting to true")
            #self.toolSelectNode.setAction(self.selectElementAction)
            self.readAnalysisAction.setEnabled(True)                            
            self.openOptimizationManagerAction.setEnabled(True)
            self.readMeasurementsAction.setEnabled(True)
            self.importFileINP.setEnabled(True)
            # self.selectElementAction.setEnabled(True)
            print("After setting to true")
    

    def updateActionStateClose(self):
        print("Entering updateActionStateClose")
        self.cleanMarkers()
        
        actions = [self.readAnalysisAction,
                    self.insertSensorAction,
                    self.openOptimizationManagerAction,
                    self.readMeasurementsAction,
                    self.importFileINP,
                    self.selectElementAction,
                    self.toolbarToolManager.insertDemandNodeAction,
                    self.insertTankNodeAction,
                    self.insertReservoirNodeAction,
                    self.insertValveNodeAction,
                    self.insertPumpNodeAction,
                    self.insertSensorNodeAction]

        for action in actions:
            if action:
                if action.isEnabled():
                    action.setEnabled(False)
                if action.isChecked():
                    action.setChecked(False) 
                    
        if (self.hub_connection): self.hub_connection.stop()

        print("Before stopping the sync manager...............................................")
        if (self.syncManager): self.syncManager.stop()

        
    def cleanMarkers(self):
        if self.canvas and self.canvas.scene() and self.canvas.items():
            vertex_items = [i for i in self.canvas.scene().items() if isinstance(i, QgsVertexMarker)]
            for vertex in vertex_items:
                self.canvas.scene().removeItem(vertex)
            self.canvas.refresh()  


    def getMeasurements(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"You must connect to WaterIng!"), level=1, duration=5)
        else:
            try:
                self.dlg = WateringDatachannels()
                self.dlg.show()
                self.dlg.exec_()
            except:
                self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"No data source available for the project."), level=1, duration=5)


    def createOnlineConnectionChannels(self):
        print("Entering creation of online connection channels")
        scenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        scenarioName = QgsProject.instance().readEntry("watering","scenario_name","default text")[0]
        
        print(scenarioFK)
        print(scenarioName)
        
        invoresult = self.hub_connection.send("joingroup", [scenarioFK]) 
        print(invoresult.invocation_id)


    def processINPImportUpdate(self, paraminput):
        print(paraminput)

    def processPOSTRESERVOIR(self, paraminput):
        print(paraminput)
        print("preparing")
        print(self.scenarioUnitOFWork.reservoirNodeRepository)
        self.scenarioUnitOFWork.reservoirNodeRepository.addElementFromSignalR(paraminput[0])
        print("Reservoir inserted")

    def processDELETERESERVOIR(self, paraminput):
        self.scenarioUnitOFWork.reservoirNodeRepository.deleteElement(paraminput[0])
        print(paraminput)
        
    
    def updateElements(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"You must connect to WaterIng!"), level=1, duration=5)
        else:
            self.scenarioUnitOFWork.updateAll()


    def cleanCache(self):
        project = QgsProject.instance()
        
        if WateringUtils.isWateringProject():
            WateringUtils.saveProjectBox()
            if project: project.clear()
            
        watering_appdata_folder = WateringUtils.get_app_data_path() + "/QGISWatering/"
        
        for item in os.listdir(watering_appdata_folder):
            item_path = os.path.join(watering_appdata_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # remove file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # remove directory

        projectsJSON_path = watering_appdata_folder + 'projects.json'
        
        data = {}  
        with open(projectsJSON_path, 'w') as json_file:
            json.dump(data, json_file)
            
        iface.messageBar().pushMessage(self.tr("WaterIng projects from cache memory cleared successfully!"), level=Qgis.Success, duration=5)

    def cleanCacheMessageBox(self):
        response = QMessageBox.question(None,
                                        "Clean cache",
                                        "Are you sure you want to delete all WaterIng projects from the cache memory?",
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if response == QMessageBox.Yes: self.cleanCache()

    def setActiveStateUndo(self, activeState):
        print("Entering the activation of undo button")
        self.undoAction.setEnabled(activeState)
    
    def setActiveStateRedo(self, activeState):
        self.redoAction.setEnabled(activeState)
    
    