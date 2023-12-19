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

from .toolbarManager.toolbarToolManager import toolbarToolManager
from .toolsMap.insertSensorNodeToolPlacement import InsertSensorNodeToolPlacement
from .toolsProcess.ImportINPFileTool import ImportINPFileTool
from .toolsMap.InsertDemandNodeTool import InsertDemandNodeTool
from .toolsMap.insertTankNodeTool import InsertTankNodeTool
from .toolsMap.insertReservoirNodeTool import InsertReservoirNodeTool
from .toolsMap.insertWaterPipeTool import InsertWaterPipeTool
from .toolsMap.insertValveNodeTool import InsertValveNodeTool
from .toolsMap.insertPumpNodeTool import InsertPumpNodeTool
from .toolsMap.insertWaterMeterNodeTool import InsertWaterMeterNodeTool
from .toolsMap.insertSensorNodeTool import InsertSensorNodeTool
from .toolsMap.selectNodeTool import SelectNodeTool
from .toolsMap.deleteElementTool import DeleteElementTool
from .ui.watering_load import WateringLoad
from .ui.watering_login import WateringLogin
#from .ui.watering_analysis import WateringAnalysis
#from .ui.watering_optimization import WaterOptimization
from .watering_utils import WateringUtils
#from .ui.watering_datachannels import WateringDatachannels
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
        """self.insertSensorAction = None        
        self.insertReservoirNodeAction = None
        self.insertValveNodeAction = None
        self.insertPumpNodeAction = None
        self.insertSensorNodeAction = None
        self.toolDeleteElementAction = None
        self.selectElementAction = None"""
        #self.readAnalysisAction = None
        self.canvas = iface.mapCanvas()
        QgsProject.instance().cleared.connect(self.updateActionStateClose)
        QgsProject.instance().readProject.connect(self.updateActionStateOpen)


        #self.readMeasurementsAction = None
                                                  
        # Toolbar
        self.activeMapTool = None
        self.toolbar = self.iface.addToolBar("WaterIng Toolbar")
        self.toolbar.setObjectName("QGISWatering")
        self.toolbar.setVisible(True)

        self.hub_connection = None
        # Dock
        #self.analysisDockPanel = WateringAnalysis(self.iface)
        #self.iface.addDockWidget(Qt.RightDockWidgetArea, self.analysisDockPanel)

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
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/login.svg'
        self.add_action(
            icon_path,
            text=self.tr(u'Watering Login'),
            callback=self.addLogin,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/QGISPlugin_WaterIng/images/loadElements.svg'
        self.add_action(
            icon_path,
            text=self.tr(u'Download Elements'),
            callback=self.addLoad,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/refresh.svg'
        self.add_action(
            icon_path,
            text=self.tr(u'Update Elements'),
            callback=self.updateElements,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/clean.svg'
        self.deleteCacheFromWaterIng = self.add_action(
            icon_path,
            text=self.tr(u'Clean cache'),
            callback=self.cleanCacheMessageBox,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/connection_status_offline.png'
        self.connectionStatusAction = self.add_action(
            icon_path,
            text=self.tr(u'Watering Connection'),
            callback=self.setWateringConnection,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.connectionStatusAction.setCheckable(True)
        
        self.toolbarToolManager.initializeToolbarButtonActions()
        self.toolbarToolManager.editElementsAction.toggled.connect(self.toolbarToolManager.activateEditTool)
        self.toolbarToolManager.optimizationToolsAction.toggled.connect(self.toolbarToolManager.activateOptimizationTool)
        self.toolbarToolManager.readMeasurementsAction.toggled.connect(self.toolbarToolManager.activateMeasurementTool)
        self.toolbarToolManager.readAnalysisAction.toggled.connect(self.toolbarToolManager.activateWaterAnalysisTool)
       

                                                       
        #adding a standard action to our toolbar
        self.iface.actionIdentify().setIcon(QIcon(':/plugins/QGISPlugin_WaterIng/images/select.svg'))
        #self.toolIdentify = QgsMapToolIdentify(self.canvas)
        #self.toolIdentify.setAction(self.iface.actionIdentify())
        self.toolbar.addAction(self.iface.actionIdentify())
        
       

        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Watering API Connection', 'WateringLogin'),
                action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar
        del self.toolbarToolManager.toolbar

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
            self.actionManager = actionManager(os.environ.get('TOKEN'), self.scenarioUnitOFWork.scenarioFK, self.setActiveStateUndo, self.setActiveStateRedo) 
            if not self.dlg.Offline:          
                self.setHubConnection()
                WateringUtils.setProjectMetadata("connection_status", "online")
            else:
                WateringUtils.setProjectMetadata("connection_status", "default text")
            print("before updating options")                
            self.updateActionStateOpen()
            self.updateActionScenarioStateOpen()
             
                
    def importINPFile(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Load a project scenario first in Download Elements!"), level=1, duration=5)
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5)
        else:
            self.dlg = WateringINPImport(self.iface)
            self.dlg.show()
            self.dlg.exec_()


    def executeUnDoAction(self):
        self.actionManager.undoAction()

    def executeReDoAction(self):
        self.actionManager.redoAction()


    def updateActionScenarioStateOpen(self):
        """ self.toolInsertSensorNodePlacement = InsertSensorNodeToolPlacement(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager)              
        self.toolInsertSensorNodePlacement.setAction(self.insertSensorAction)
        self.insertSensorAction.setEnabled(True) """

        
        #TODO toolSelectElements = SelectElementsTool()
        #TODO self.toolbarToolManager.toolImportINPFile.setCurrentTool(toolSelectElements)
        self.toolbarToolManager.selectElementAction.setEnabled(True)


        toolImportINPFile = ImportINPFileTool(self.iface)
        self.toolbarToolManager.toolImportINPFile.setCurrentTool(toolImportINPFile)
        self.toolbarToolManager.toolImportINPFile.setEnabled(True)
    
        toolInsertDemandNode = InsertDemandNodeTool(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertDemandNode.setAction(self.toolbarToolManager.insertDemandNodeAction)
        self.toolbarToolManager.insertDemandNodeAction.setCurrentTool(toolInsertDemandNode)
        self.toolbarToolManager.insertDemandNodeAction.setEnabled(True)

        toolInsertTankNode = InsertTankNodeTool(self.canvas, self.scenarioUnitOFWork.tankNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertTankNode.setAction(self.toolbarToolManager.insertTankNodeAction)
        self.toolbarToolManager.insertTankNodeAction.setCurrentTool(toolInsertTankNode)
        self.toolbarToolManager.insertTankNodeAction.setEnabled(True)

        toolInsertReservoirNode = InsertReservoirNodeTool(self.canvas, self.scenarioUnitOFWork.reservoirNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertReservoirNode.setAction(self.toolbarToolManager.insertReservoirNodeAction)
        self.toolbarToolManager.insertReservoirNodeAction.setCurrentTool(toolInsertReservoirNode)
        self.toolbarToolManager.insertReservoirNodeAction.setEnabled(True)

        toolInsertWaterPipe = InsertWaterPipeTool(self.canvas, self.scenarioUnitOFWork.pipeNodeRepository, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertWaterPipe.setAction(self.toolbarToolManager.insertWaterPipeAction)
        self.toolbarToolManager.insertWaterPipeAction.setCurrentTool(toolInsertWaterPipe)
        self.toolbarToolManager.insertWaterPipeAction.setEnabled(True)

        toolInsertValveNode = InsertValveNodeTool(self.canvas, self.scenarioUnitOFWork.valveNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertValveNode.setAction(self.toolbarToolManager.insertValveNodeAction)
        self.toolbarToolManager.insertValveNodeAction.setCurrentTool(toolInsertValveNode)
        self.toolbarToolManager.insertValveNodeAction.setEnabled(True)

        toolInsertPumpNode = InsertPumpNodeTool(self.canvas, self.scenarioUnitOFWork.pumpNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertPumpNode.setAction(self.toolbarToolManager.insertPumpNodeAction)
        self.toolbarToolManager.insertPumpNodeAction.setCurrentTool(toolInsertPumpNode)
        self.toolbarToolManager.insertPumpNodeAction.setEnabled(True)

        toolInsertWaterMeterNode = InsertWaterMeterNodeTool(self.canvas, self.scenarioUnitOFWork.waterMeterNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertWaterMeterNode.setAction(self.toolbarToolManager.insertWaterMeterNodeAction)
        self.toolbarToolManager.insertWaterMeterNodeAction.setCurrentTool(toolInsertWaterMeterNode)
        self.toolbarToolManager.insertWaterMeterNodeAction.setEnabled(True)
        
        toolInsertSensorNode = InsertSensorNodeTool(self.canvas, self.scenarioUnitOFWork.sensorNodeRepository, self.actionManager, self.toolbarToolManager)
        toolInsertSensorNode.setAction(self.toolbarToolManager.insertSensorNodeAction)
        self.toolbarToolManager.insertSensorNodeAction.setCurrentTool(toolInsertSensorNode)
        self.toolbarToolManager.insertSensorNodeAction.setEnabled(True)
        
        toolDeleteElement = DeleteElementTool(self.canvas)
        toolDeleteElement.setAction(self.toolbarToolManager.toolDeleteElementAction)
        self.toolbarToolManager.toolDeleteElementAction.setCurrentTool(toolDeleteElement)
        self.toolbarToolManager.toolDeleteElementAction.setEnabled(True)
              
    def updateActionStateOpen(self):
        #self.cleanMarkers()
        print("before entering if")
        if WateringUtils.isWateringProject():
            self.toolSelectNode = SelectNodeTool(self.canvas)  #(self.canvas)
            print("before setting to true")
            #self.toolSelectNode.setAction(self.selectElementAction)
            self.toolbarToolManager.readAnalysisAction.setEnabled(True)                            
            self.toolbarToolManager.openOptimizationManagerAction.setEnabled(True)
            self.toolbarToolManager.readMeasurementsAction.setEnabled(True)
            # self.selectElementAction.setEnabled(True)
            print("After setting to true")
    

    def updateActionStateClose(self):
        print("Entering updateActionStateClose")
        self.cleanMarkers()
        
        actions = [self.toolbarToolManager.readAnalysisAction,
                    self.toolbarToolManager.insertSensorNodeAction,
                    self.toolbarToolManager.openOptimizationManagerAction,
                    self.toolbarToolManager.readMeasurementsAction,
                    self.toolbarToolManager.selectElementAction,
                    self.toolbarToolManager.insertDemandNodeAction,
                    self.toolbarToolManager.insertTankNodeAction,
                    self.toolbarToolManager.insertReservoirNodeAction,
                    self.toolbarToolManager.insertWaterPipeAction,
                    self.toolbarToolManager.insertValveNodeAction,
                    self.toolbarToolManager.insertPumpNodeAction,
                    self.toolbarToolManager.insertWaterMeterNodeAction,
                    self.toolbarToolManager.insertSensorNodeAction,
                    self.toolbarToolManager.toolDeleteElementAction]

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

    """
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
                self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"No data source available for the project."), level=1, duration=5)"""


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
        self.toolbarToolManager.undoAction.setEnabled(activeState)
    
    def setActiveStateRedo(self, activeState):
        self.toolbarToolManager.redoAction.setEnabled(activeState)
    
    def deleteElement(self):
        print("Deleted")
    
    def setWateringConnection(self):
        connection_status = WateringUtils.getProjectMetadata("connection_status")
        
        if self.connectionStatusAction.isChecked():
            self.connectionStatusAction.setIcon(QIcon(':/plugins/QGISPlugin_WaterIng/images/connection_status_online.png'))
            if connection_status != "default text":
                self.setHubConnection()
                iface.messageBar().pushMessage(self.tr("Set connection status to online."), level=Qgis.Success, duration=5)
            else:
                self.iface.messageBar().pushMessage(self.tr(u"Error"), self.tr(u"Failed to establish connection. Please reopen the project."), level=1, duration=5)
                self.connectionStatusAction.setIcon(QIcon(':/plugins/QGISPlugin_WaterIng/images/connection_status_offline.png'))
        else:
            self.closeHubConnection()
            iface.messageBar().pushMessage(self.tr("Set connection status to offline."), level=Qgis.Success, duration=5)
            self.connectionStatusAction.setIcon(QIcon(':/plugins/QGISPlugin_WaterIng/images/connection_status_offline.png'))
    
    def setHubConnection(self):
        if self.scenarioUnitOFWork:
            self.syncManager = syncManagerSHPREST(os.environ.get('TOKEN'), self.scenarioUnitOFWork.scenarioFK)
            self.syncManager.connectScenarioUnitOfWorkToServer(self.scenarioUnitOFWork)
            
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
            
    def closeHubConnection(self):
        if self.hub_connection is not None:
            self.hub_connection.stop()
            self.hub_connection = None