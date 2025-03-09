# -*- coding: utf-8 -*-

# Import QGis
from datetime import datetime
import uuid
import wntr

from qgis.core import QgsProject, Qgis, QgsNetworkAccessManager
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox, QLabel, QMenu, QDockWidget
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from qgis.gui import QgsMapCanvas, QgsMapToolIdentify, QgsVertexMarker, QgsMapToolIdentify
from qgis.utils import iface
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QTimer


from .syncInfrastructureSHPREST.syncManagerSHPREST import syncManagerSHPREST

#
# Initialize Qt resources from file resources.py
from .resources import *
import pickle
import time
import shutil
import json

import ssl
import socket
from qgis.core import QgsSettings

# Import the code for the dialog

from .toolbarManager.toolbarToolManager import toolbarToolManager
from .toolsMap.insertSensorNodeToolPlacement import InsertSensorNodeToolPlacement
from .toolsProcess.ImportINPFileTool import ImportINPFileTool
from .toolsProcess.ImportShapeFileTool import ImportShapeFileTool
from .toolsProcess.exportINPFileTool import ExportINPFileTool
from .toolsProcess.localAnalysisWithWNTRTool import LocalAnalysisWithWNTRTool
from .toolsProcess.analysisOptionsTool import AnalysisOptionsTool
from .toolsProcess.metricsAnalysisTool import MetricsAnalysisTool
from .toolsProcess.addGraphicsTool import AddGraphicsTool
from .toolsProcess.NetworkReviewTool import NetworkReviewTool
from .toolsProcess.SelectionReviewTool import SelectionReviewTool
from .toolsProcess.DemandPatternTool import DemandPatternTool
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

# from .ui.watering_analysis import WateringAnalysis
# from .ui.watering_optimization import WaterOptimization
from .watering_utils import WateringUtils
from .watering_utils import WateringSynchWorker

# from .ui.watering_datachannels import WateringDatachannels
from .ui.watering_INPImport import WateringINPImport
from .ActionManagement.actionManager import actionManager
from .ActionManagement.identifyElementAction import WateringIdentifyTool
from .syncInfrastructureSHPREST.syncManagerSHPREST import syncManagerSHPREST
from .unitofwork.scenarioUnitOfWork import ScenarioUnitOfWork

from signalrcore.hub_connection_builder import HubConnectionBuilder

import os.path

# Import the code for the process INP file.
from .INP_Manager.simulatorQGIS import SimulatorQGIS
# from .INP_Manager.INPManager import INPManager
# from .shpProcessing.waterTanks import ImportTanksShp
from .INP_Manager.customdialog import show_custom_dialog, show_input_dialog
from .INP_Manager.INPManager import INPManager
from .INP_Manager.inp_options_enum import INP_Options
from .INP_Manager.inp_utils import INP_Utils
from .INP_Manager.node_link_ResultType import LinkResultType, NodeResultType
from .NetworkAnalysis.nodeNetworkAnalysisLocal import NodeNetworkAnalysisLocal
from .NetworkAnalysis.pipeNetworkAnalysisLocal import PipeNetworkAnalysisLocal

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
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", "watering_{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&Watering API Connection")
        """self.insertSensorAction = None
        self.insertReservoirNodeAction = None
        self.insertValveNodeAction = None
        self.insertPumpNodeAction = None
        self.insertSensorNodeAction = None
        self.toolDeleteElementAction = None
        self.selectElementAction = None"""
        # self.readAnalysisAction = None
        self.canvas = iface.mapCanvas()
        QgsProject.instance().cleared.connect(self.updateActionStateClose)
        QgsProject.instance().readProject.connect(self.updateActionStateOpen)

        # Toolbar
        self.activeMapTool = None
        self.toolbar = self.iface.addToolBar("WaterIng Toolbar")
        self.toolbar.setObjectName("QGISWatering")
        self.toolbar.setVisible(True)

        self.hub_connection = None
        # Dock
        # self.analysisDockPanel = WateringAnalysis(self.iface)
        # self.iface.addDockWidget(Qt.RightDockWidgetArea, self.analysisDockPanel)

        self.scenarioUnitOFWork = None
        self.syncManager = None
        self.actionManager = None
        self.toolbarToolManager = None
        self.project_info = None
        
        self.simulatorQGIS = SimulatorQGIS()

    # noinspection PyMethodMayBeStatic
    def tr(self, message, context="QGISPlugin_WaterIng"):
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
        parent=None,
    ):

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
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

#-------------- Acciones que se reslizan para la simulación -------------------
    def simulator_run(self):
        # print("001: Simulation no implementada...")
        # self.simulatorQGIS.MessageInformation("001: Simulation no implementada...")
        self.simulatorQGIS.run()


    def simulator_patterns(self):
        print("002: Patterns de patrones no implementado...")
        self.simulatorQGIS.MessageInformation("002: Patterns no implementada...")


    def simulator_curves(self):
        print("003: Curves no implementado...")
        self.simulatorQGIS.MessageInformation("003: Curves no implementada...")


    def simulator_controls(self):
        print("004: Controls no implementado...")
        self.simulatorQGIS.MessageInformation("004: Controls no implementada...")


    def simulator_options(self):
        # print("005: Options no implementada...")
        # self.simulatorQGIS.MessageInformation("005: Options no implementada...")
        self.simulatorQGIS.viewOptions()

    def simulator_resilience(self):
        print("006: Resilience no implementada...")
        self.simulatorQGIS.MessageInformation("006: Resilience no implementada...")


#-------------- Acciones que se reslizan para la simulación -------------------

    def initGui(self):

        self.toolbarToolManager = toolbarToolManager(self.toolbar, self.iface.mainWindow(), self.canvas)

        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/QGISPlugin_WaterIng/images/login.svg"
        self.add_action(
            icon_path,
            text=self.tr("Watering Login"),
            callback=self.addLogin,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        # Esto es la simulación de de redes hidráulicas.
        # Crear el submenú
        # submenu = QMenu("Submenu", self.toolbar)
        
        # Crear acciones para el submenú
        # Patterns
        # icon1 = QIcon(":/plugins/QGISPlugin_WaterIng/images/01_01.svg")
        # action1 = QAction(icon1, self.tr("Patterns"), self.toolbar)
        # action1.triggered.connect(self.simulator_patterns)
        # submenu.addAction(action1)

        # Curves
        # icon2 = QIcon(":/plugins/QGISPlugin_WaterIng/images/01_01.svg")
        # action2 = QAction(icon2, self.tr("Curves"), self.toolbar)
        # action2.triggered.connect(self.simulator_curves)
        # submenu.addAction(action2)

        # Controls
        # icon3 = QIcon(":/plugins/QGISPlugin_WaterIng/images/01_01.png")
        # action3 = QAction(icon3, self.tr("Controls"), self.toolbar)
        # action3.triggered.connect(self.simulator_controls)
        # submenu.addAction(action3)

        # Options
        # icon4 = QIcon(":/plugins/QGISPlugin_WaterIng/images/01_01.svg")
        # action4 = QAction(icon4, self.tr("Options"), self.toolbar)
        # action4.triggered.connect(self.simulator_options)
        # submenu.addAction(action4)
        
        # icon5 = QIcon(":/plugins/QGISPlugin_WaterIng/images/01_01.svg")
        # action5 = QAction(icon5, self.tr("Resilience metrics"), self.toolbar)
        # action5.triggered.connect(self.simulator_resilience)
        # submenu.addAction(action5)

        # # Crear una acción para el toolbar que abra el submenú
        # icon3 = QIcon(":/plugins/QGISPlugin_WaterIng/images/refresh.svg")
        # menu_action = QAction(icon3, self.tr("Run simulation"), self.toolbar)
        # menu_action.triggered.connect(self.simulator_run)
        # menu_action.setMenu(submenu)
        # self.toolbar.addAction(menu_action)
        
        # self.action1 = QAction("Open Input Dialog", self.iface.mainWindow())
        # self.action1.triggered.connect(self.open_dock_widget)
        # self.iface.addToolBarIcon(self.action1)
        # self.iface.addPluginToMenu("&My Plugin", self.action1)
        
        
        # icon_path = ":/plugins/QGISPlugin_WaterIng/images/run_epanet.svg"
        # self.add_action(
        #     icon_path,
        #     text=self.tr("Watering Run simulación"),
        #     callback=self.simulator_run,
        #     toolbar = self.toolbar,
        #     parent=self.iface.mainWindow())
        
        # icon_path = ":/plugins/QGISPlugin_WaterIng/images/optins.svg"
        # self.add_action(
        #     icon_path,
        #     text=self.tr("Watering Opciones"),
        #     callback=self.simulator_options,
        #     toolbar = self.toolbar,
        #     parent=self.iface.mainWindow())


        icon_path = ":/plugins/QGISPlugin_WaterIng/images/01_01.svg"
        self.add_action(
            icon_path,
            text=self.tr("Watering view metrics"),
            callback=self.viewResult,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
# =================================================================
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/loadElements.svg"
        self.add_action(
            icon_path,
            text=self.tr("Download Elements"),
            callback=self.addLoad,
            toolbar=self.toolbar,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/QGISPlugin_WaterIng/images/refresh.svg"
        self.synchAction = self.add_action(
            icon_path,
            text=self.tr("Update Elements"),
            callback=self.onSynchButtonClicked,
            toolbar=self.toolbar,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/QGISPlugin_WaterIng/images/clean.svg"
        self.deleteCacheFromWaterIng = self.add_action(
            icon_path,
            text=self.tr("Clean cache"),
            callback=self.cleanCacheMessageBox,
            toolbar=self.toolbar,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/QGISPlugin_WaterIng/images/connection_status_offline.png"
        self.connectionStatusAction = self.add_action(
            icon_path,
            text=self.tr("Watering Connection"),
            callback=self.setWateringConnection,
            toolbar=self.toolbar,
            parent=self.iface.mainWindow(),
        )
        self.connectionStatusAction.setCheckable(True)

        icon_path = ":/plugins/QGISPlugin_WaterIng/images/waterMeterButton.png"
        self.getWaterMeterNodes = self.add_action(
            icon_path,
            text=self.tr("Connect Water Meters to Nodes"),
            callback=self.getClosestNode,
            toolbar=self.toolbar,
            parent=self.iface.mainWindow(),
        )

        self.toolbarToolManager.initializeToolbarButtonActions()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Watering API Connection", "WateringLogin"), action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar
        del self.toolbarToolManager.toolbar

    def addLogin(self):
        print("Check Internet Connection: ", WateringUtils.isInternetConnection())
        self.getWateringCertificate()
        self.dlg = WateringLogin()
        self.dlg.show()
        if self.dlg.exec_() == 1:
            if WateringUtils.isProjectOpened() and WateringUtils.isWateringProject():
                # self.setHubConnection()
                WateringUtils.setProjectMetadata("connection_status", "online")
            self.addLoad()


    def viewResult(self):
        # self.simulatorQGIS.exportResults()
        # fecha = datetime.now().date()
        # time = datetime.now().time()
        # fecha_to_int = int(fecha.strftime("%Y%m%d"))
        # time_to_int = int(time.strftime("%H%M%S"))
        # print(f"fecha en ertero: {fecha_to_int}")
        # print(f"time en entero: {time_to_int}")
        # fecha = datetime.strptime(str(fecha_to_int), "%Y%m%d").strftime("%d/%m/%Y")
        # time = datetime.strptime(str(time_to_int), "%H%M%S").strftime("%H:%M:%S")
        # print(f"fecha en string: {fecha}")
        # print(f"time en string: {time}")
        
        # fecha_hora = datetime.now()
        # fecha_to_int = int(fecha_hora.strftime("%y%m%d%H%M%S"))
        # fecha_hora_new_format = datetime.strptime(str(fecha_to_int), "%y%m%d%H%M%S").strftime("%/%m/%YY => %H:%M")
        # print(f"La fecha de la PC es: {fecha_hora}")
        # print(f"La fecha de la PC en entero es: {fecha_to_int}")
        # print(f"La fecha de la PC con un nuevo formato: {fecha_hora_new_format}")
        
        self.removerAnalysis()
            # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.
            
        fecha_hora = datetime.now()
        fecha_to_int = int(fecha_hora.strftime("%y%m%d%H%M%S"))
        tempFile = f"S_{fecha_to_int}"
            
        inpFile = INPManager()
        inpFile.writeSections()
            
            # options: INPOptions = INPOptions(None)
            # options.load()
            # self.writeSections()

        wn = wntr.network.WaterNetworkModel(inpFile.OutFile)

        # os.path.join(inpFile.OutFile, "Simulaciones", tempFile)
        # inpFileTemp = INP_Utils.generate_directory(inpFile.OutFile + "\\Simulaciones\\" + tempFile)
        inpFileTemp = INP_Utils.generate_directory(os.path.join(os.path.dirname(inpFile.OutFile), "Simulaciones", tempFile))
        # inpFileTemp += "\\" + tempFile
        inpFileTemp = os.path.join(inpFileTemp, tempFile)

            # Simulate hydraulics
        sim = wntr.sim.EpanetSimulator(wn)
            # sim = wntr.sim.WNTRSimulator(wn)
        self._results = sim.run_sim(inpFileTemp)

        nodeResult_at_0hr = self._results.node[NodeResultType.pressure.name].loc[0 * 3600, :]
        linkResult_at_0hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
            # pressure_at_5hr = results.node[NodeResultType.pressure.name].loc[0*3600, :]
            # print(pressure_at_5hr)
        self._guid = str(uuid.uuid4())
        units = inpFile.options[INP_Options.Hydraulics].inpfile_units
        NodeNetworkAnalysisLocal(nodeResult_at_0hr, self._guid, "00:00")
        PipeNetworkAnalysisLocal(linkResult_at_0hr, self._guid, "00:00", LinkResultType.flowrate, units)
        
        self.updateJSON(os.path.join(os.path.dirname(inpFile.OutFile), "Simulaciones"))
        
    def removerAnalysis(self):
         # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)

    def updateJSON(self, path: str):
        """Äctualiza el archivo JSON con los resultados de la simulación"""
        directorios = []

        for directory_name in os.listdir(path):
            directory_path = os.path.join(path, directory_name)
            if os.path.isdir(directory_path):
                temp = directory_name.split("_")
                date = datetime.strptime(temp[1], "%y%m%d%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
                directorios.append({
                    "directoryName": directory_name,
                    "directoryDate": date,
                    "directoryPath": directory_path
                })
        
        ruta_json = os.path.join(path, "inf.json")

        with open(ruta_json, 'w') as archivo_json:
            json.dump(directorios, archivo_json, indent=4)


    def addLoad(self):
        print("calling watering load dialog")
        self.dlg = WateringLoad()
        self.dlg.show()
        if self.dlg.exec_() == 1:
            if hasattr(self.dlg, 'myScenarioUnitOfWork'):
                self.scenarioUnitOFWork = self.dlg.myScenarioUnitOfWork
            self.actionManager = actionManager(
                os.environ.get("TOKEN"), self.dlg.current_scenario_fk, self.setActiveStateUndo, self.setActiveStateRedo
            )
            if WateringUtils.isInternetConnection() and not self.hub_connection:
                print("setting hub connection")
                self.setHubConnection()
            self.updateActionStateOpen()
            self.updateActionScenarioStateOpen()
            self.setOnAttributeChange()
            self.setStatusBarInfo(self.dlg.current_project_name, self.dlg.current_scenario_name)

    def importINPFile(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        if os.environ.get("TOKEN") == None:
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5
            )
        else:
            self.dlg = WateringINPImport(self.iface)
            self.dlg.show()
            self.dlg.exec_()

    def executeUnDoAction(self):
        self.actionManager.undoAction()

    def executeReDoAction(self):
        self.actionManager.redoAction()

    def updateActionScenarioStateOpen(self):
        # TODO toolSelectElements = SelectElementsTool()
        # TODO self.toolbarToolManager.toolImportINPFile.setCurrentTool(toolSelectElements)
        toolImportINPFile = ImportINPFileTool(self.iface)
        self.toolbarToolManager.toolImportINPFile.setCurrentTool(toolImportINPFile)
        self.toolbarToolManager.toolImportINPFile.setEnabled(True)

        toolImportShapeFile = ImportShapeFileTool(self.iface)
        self.toolbarToolManager.toolImportShapeFile.setCurrentTool(toolImportShapeFile)
        self.toolbarToolManager.toolImportShapeFile.setEnabled(True)
        
        toolExportINPFile = ExportINPFileTool(self.iface)
        self.toolbarToolManager.toolExportINPFile.setCurrentTool(toolExportINPFile)
        self.toolbarToolManager.toolExportINPFile.setEnabled(True)
        
        localAnalysisWithWNTRTool = LocalAnalysisWithWNTRTool(self.iface)
        self.toolbarToolManager.localAnalysisWithWNTR.setCurrentTool(localAnalysisWithWNTRTool)
        self.toolbarToolManager.localAnalysisWithWNTR.setEnabled(True)
        
        analysisOptionsTool = AnalysisOptionsTool(self.iface)
        self.toolbarToolManager.analysisOptions.setCurrentTool(analysisOptionsTool)
        self.toolbarToolManager.analysisOptions.setEnabled(True)
        
        metricsAnalysisTool = MetricsAnalysisTool(self.iface)
        self.toolbarToolManager.metricsAnalysis.setCurrentTool(metricsAnalysisTool)
        self.toolbarToolManager.metricsAnalysis.setEnabled(True)
        
        addGraphicsTool = AddGraphicsTool(self.iface)
        self.toolbarToolManager.addGraphics.setCurrentTool(addGraphicsTool)
        self.toolbarToolManager.addGraphics.setEnabled(True)

        # toolReviewNetwork = NetworkReviewTool(self.iface)
        # self.toolbarToolManager.toolReviewNetwork.setCurrentTool(toolReviewNetwork)
        # self.toolbarToolManager.toolReviewNetwork.setEnabled(True)

        toolSelectionReview = SelectionReviewTool(self.iface)
        self.toolbarToolManager.toolSelectionReview.setCurrentTool(toolSelectionReview)
        self.toolbarToolManager.toolSelectionReview.setEnabled(True)

        toolDemandPattern = DemandPatternTool(self.iface)
        self.toolbarToolManager.toolDemandPattern.setCurrentTool(toolDemandPattern)
        self.toolbarToolManager.toolDemandPattern.setEnabled(True)

        toolInsertDemandNode = InsertDemandNodeTool(
            self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertDemandNode.setAction(self.toolbarToolManager.insertDemandNodeAction)
        self.toolbarToolManager.insertDemandNodeAction.setCurrentTool(toolInsertDemandNode)
        self.toolbarToolManager.insertDemandNodeAction.setEnabled(True)

        toolInsertTankNode = InsertTankNodeTool(
            self.canvas, self.scenarioUnitOFWork.tankNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertTankNode.setAction(self.toolbarToolManager.insertTankNodeAction)
        self.toolbarToolManager.insertTankNodeAction.setCurrentTool(toolInsertTankNode)
        self.toolbarToolManager.insertTankNodeAction.setEnabled(True)

        toolInsertReservoirNode = InsertReservoirNodeTool(
            self.canvas, self.scenarioUnitOFWork.reservoirNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertReservoirNode.setAction(self.toolbarToolManager.insertReservoirNodeAction)
        self.toolbarToolManager.insertReservoirNodeAction.setCurrentTool(toolInsertReservoirNode)
        self.toolbarToolManager.insertReservoirNodeAction.setEnabled(True)

        toolInsertWaterPipe = InsertWaterPipeTool(
            self.canvas,
            self.scenarioUnitOFWork.pipeNodeRepository,
            self.scenarioUnitOFWork.waterDemandNodeRepository,
            self.actionManager,
            self.toolbarToolManager,
        )
        toolInsertWaterPipe.setAction(self.toolbarToolManager.insertWaterPipeAction)
        self.toolbarToolManager.insertWaterPipeAction.setCurrentTool(toolInsertWaterPipe)
        self.toolbarToolManager.insertWaterPipeAction.setEnabled(True)

        toolInsertValveNode = InsertValveNodeTool(
            self.canvas, self.scenarioUnitOFWork.valveNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertValveNode.setAction(self.toolbarToolManager.insertValveNodeAction)
        self.toolbarToolManager.insertValveNodeAction.setCurrentTool(toolInsertValveNode)
        self.toolbarToolManager.insertValveNodeAction.setEnabled(True)

        toolInsertPumpNode = InsertPumpNodeTool(
            self.canvas, self.scenarioUnitOFWork.pumpNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertPumpNode.setAction(self.toolbarToolManager.insertPumpNodeAction)
        self.toolbarToolManager.insertPumpNodeAction.setCurrentTool(toolInsertPumpNode)
        self.toolbarToolManager.insertPumpNodeAction.setEnabled(True)

        toolInsertWaterMeterNode = InsertWaterMeterNodeTool(
            self.canvas, self.scenarioUnitOFWork.waterMeterNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertWaterMeterNode.setAction(self.toolbarToolManager.insertWaterMeterNodeAction)
        self.toolbarToolManager.insertWaterMeterNodeAction.setCurrentTool(toolInsertWaterMeterNode)
        self.toolbarToolManager.insertWaterMeterNodeAction.setEnabled(True)

        toolInsertSensorNode = InsertSensorNodeTool(
            self.canvas, self.scenarioUnitOFWork.sensorNodeRepository, self.actionManager, self.toolbarToolManager
        )
        toolInsertSensorNode.setAction(self.toolbarToolManager.insertSensorNodeAction)
        self.toolbarToolManager.insertSensorNodeAction.setCurrentTool(toolInsertSensorNode)
        self.toolbarToolManager.insertSensorNodeAction.setEnabled(True)

        toolDeleteElement = DeleteElementTool(
            self.canvas, self.scenarioUnitOFWork, self.actionManager, self.toolbarToolManager
        )
        toolDeleteElement.setAction(self.toolbarToolManager.toolDeleteElementAction)
        self.toolbarToolManager.toolDeleteElementAction.setCurrentTool(toolDeleteElement)
        self.toolbarToolManager.toolDeleteElementAction.setEnabled(True)

        toolIdentifyElement = WateringIdentifyTool(self.canvas, self.actionManager, self.toolbarToolManager)
        toolIdentifyElement.setAction(self.toolbarToolManager.wateringIdentifyAction)
        self.toolbarToolManager.wateringIdentifyAction.setCurrentTool(toolIdentifyElement)
        self.toolbarToolManager.wateringIdentifyAction.setEnabled(True)

        # Connection button
        if (os.environ.get("TOKEN") != None) and not self.connectionStatusAction.isChecked():
            self.setHubConnection()
            self.connectionStatusAction.setChecked(True)

    def updateActionStateOpen(self):
        # self.cleanMarkers()
        print("before entering if")
        if WateringUtils.isWateringProject():
            self.toolSelectNode = SelectNodeTool(self.canvas)  # (self.canvas)
            print("before setting to true")
            self.toolbarToolManager.readAnalysisAction.setEnabled(True)
            self.toolbarToolManager.openOptimizationManagerAction.setEnabled(True)
            self.toolbarToolManager.openPumpModels.setEnabled(True)
            self.toolbarToolManager.readMeasurementsAction.setEnabled(True)
            self.toolbarToolManager.waterBalanceAction.setEnabled(True)
            self.toolbarToolManager.getLastMeasurementAction.setEnabled(True)
            print("After setting to true")

    def updateActionStateClose(self):
        print("Entering updateActionStateClose")
        # if QgsProject.instance().fileName():
        #     self.cleanMarkers()

        if self.project_info:
            iface.mainWindow().statusBar().removeWidget(self.project_info)
            self.project_info = None

        actions = [
            self.toolbarToolManager.readAnalysisAction,
            self.toolbarToolManager.openOptimizationManagerAction,
            self.toolbarToolManager.openPumpModels,
            self.toolbarToolManager.readMeasurementsAction,
            self.toolbarToolManager.waterBalanceAction,
            self.toolbarToolManager.getLastMeasurementAction,
            self.toolbarToolManager.insertDemandNodeAction,
            self.toolbarToolManager.insertTankNodeAction,
            self.toolbarToolManager.insertReservoirNodeAction,
            self.toolbarToolManager.insertWaterPipeAction,
            self.toolbarToolManager.insertValveNodeAction,
            self.toolbarToolManager.insertPumpNodeAction,
            self.toolbarToolManager.insertWaterMeterNodeAction,
            self.toolbarToolManager.insertSensorNodeAction,
            self.toolbarToolManager.toolDeleteElementAction,
            self.toolbarToolManager.toolExportINPFile,
            self.toolbarToolManager.localAnalysisWithWNTR,
            self.toolbarToolManager.analysisOptions,
            self.toolbarToolManager.metricsAnalysis,
            self.toolbarToolManager.addGraphics,
        ]

        for action in actions:
            if action:
                if action.isEnabled():
                    action.setEnabled(False)
                if action.isChecked():
                    action.setChecked(False)

        if self.hub_connection:
            self.hub_connection.stop()

        print("Before stopping the sync manager...............................................")
        if self.syncManager:
            self.syncManager.stop()

    def cleanMarkers(self):
        scene = self.canvas.scene() if self.canvas else None
        if scene:
            vertex_items = [item for item in scene.items() if isinstance(item, QgsVertexMarker)]
            for vertex in vertex_items:
                scene.removeItem(vertex)
            self.canvas.refresh()

    def createOnlineConnectionChannels(self):
        print("Entering creation of online connection channels")
        scenarioFK = QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]
        scenarioName = QgsProject.instance().readEntry("watering", "scenario_name", "default text")[0]

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
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        if os.environ.get("TOKEN") == None or not self.connectionStatusAction.isChecked():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            # To be constructed
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Double click the button to synch!"), level=1, duration=5
            )

    def startSynchronization(self):
        if hasattr(self, "thread") and self.thread is not None:
            if self.thread.isRunning():
                self.worker.requestStop()
                self.thread.quit()
                self.thread.wait()

        self.thread = QThread()
        self.worker = WateringSynchWorker(self.scenarioUnitOFWork)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.runSynch)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.onSynchFinished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def onSynchButtonClicked(self):
        if self.hub_connection and self.scenarioUnitOFWork:
            self.scenarioUnitOFWork.update_all()
            return

        WateringUtils.error_message(
            "Sync function is currently unavailable. Please open a project or press the connection button to proceed."
        )

    def synchSingleClicked(self):
        print("Synch button single Clicked!")
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        if os.environ.get("TOKEN") == None or not self.connectionStatusAction.isChecked():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            # self.synchAction.setChecked(self.synchAction.isChecked())
            # To Do
            # Real time synch procedures and activation
            print("Reach single click end")

    def synchDoubleClicked(self):
        print("Synch button double Clicked!")
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        if os.environ.get("TOKEN") == None or not self.connectionStatusAction.isChecked():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            self.startSynchronization()

    def cleanCache(self):
        project = QgsProject.instance()

        if WateringUtils.isWateringProject():
            WateringUtils.saveProjectBox()
            if project:
                project.clear()

        watering_appdata_folder = WateringUtils.get_app_data_path() + "/QGISWatering/"

        for item in os.listdir(watering_appdata_folder):
            item_path = os.path.join(watering_appdata_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # remove file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # remove directory

        projectsJSON_path = watering_appdata_folder + "projects.json"

        data = {}
        with open(projectsJSON_path, "w") as json_file:
            json.dump(data, json_file)

        iface.messageBar().pushMessage(
            self.tr("WaterIng projects from cache memory cleared successfully!"), level=Qgis.Success, duration=5
        )

    def cleanCacheMessageBox(self):
        response = QMessageBox.question(
            None,
            "Clean cache",
            "Are you sure you want to delete all WaterIng projects from the cache memory?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )

        if response == QMessageBox.Yes:
            self.cleanCache()

    def setActiveStateUndo(self, activeState):
        print("Entering the activation of undo button")
        self.toolbarToolManager.undoAction.setEnabled(activeState)

    def setActiveStateRedo(self, activeState):
        self.toolbarToolManager.redoAction.setEnabled(activeState)

    def deleteElement(self):
        print("Deleted")

    def setWateringConnection(self):
        connection_status = WateringUtils.getProjectMetadata("connection_status")

        if self.connectionStatusAction.isChecked() and not self.hub_connection:
            self.setHubConnection()
        else:
            if self.syncManager:
                self.syncManager.stop()
                self.syncManager.setStatusOffline()
                self.syncManager = None
            self.closeHubConnection()
            self.connectionStatusAction.setIcon(
                QIcon(":/plugins/QGISPlugin_WaterIng/images/connection_status_offline.png")
            )
            iface.messageBar().pushMessage(self.tr("Set connection status to offline."), level=Qgis.Success, duration=5)

    def setHubConnection(self):
        token = os.environ.get("TOKEN")
        if token is not None:
            if not self.scenarioUnitOFWork:
                scenario_folder = WateringUtils.getProjectMetadata("scenario_folder")
                scenario_fk = WateringUtils.getProjectMetadata("scenario_fk")
                self.scenarioUnitOFWork = ScenarioUnitOfWork(token, scenario_folder, scenario_fk)

            if not self.actionManager:
                self.actionManager = actionManager(
                    token, self.scenarioUnitOFWork.scenario_fk, self.setActiveStateUndo, self.setActiveStateRedo
                )

            if not self.syncManager:
                self.syncManager = syncManagerSHPREST(token, self.scenarioUnitOFWork.scenario_fk)
                self.syncManager.connectScenarioUnitOfWorkToServer(self.scenarioUnitOFWork)

            server_url = WateringUtils.getServerUrl() + "/hubs/waternetworkhub"

            if not self.hub_connection:
                self.hub_connection = (
                    HubConnectionBuilder()
                    .with_url(
                        server_url,
                        options={
                            "verify_ssl": False,
                            "headers": {"Authorization": "Bearer {}".format(os.environ.get("TOKEN"))},
                        },
                    )
                    .with_automatic_reconnect(
                        {"type": "interval", "keep_alive_interval": 10, "intervals": [1, 3, 5, 6, 7, 87, 3]}
                    )
                    .build()
                )

                # self.hub_connection.on_open(lambda: print("connection opened and handshake received ready to send messages"))
                self.hub_connection.on_open(self.createOnlineConnectionChannels)
                self.hub_connection.on_close(lambda: print("connection closed"))
                self.hub_connection.on_error(lambda data: print(f"An exception was thrown closed{data.error}"))

                self.hub_connection.on("UPDATE_IMPORTED", self.processINPImportUpdate)

                self.hub_connection.start()

            self.connectionStatusAction.setIcon(
                QIcon(":/plugins/QGISPlugin_WaterIng/images/connection_status_online.png")
            )
            self.connectionStatusAction.setChecked(True)

            iface.messageBar().pushMessage(self.tr("Set connection status to online."), level=Qgis.Success, duration=5)

            print("before updating options")
            self.updateActionStateOpen()
            self.updateActionScenarioStateOpen()

        else:
            print("Token is none")
            iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("You must login to WaterIng or reopen the project!"), level=1, duration=5
            )
            self.connectionStatusAction.setChecked(False)

    def closeHubConnection(self):
        if self.hub_connection is not None:
            self.hub_connection.stop()
            self.hub_connection = None

    def setOnAttributeChange(self):
        layer_list = [
            "watering_tanks",
            "watering_demand_nodes",
            "watering_pumps",
            "watering_pipes",
            "watering_reservoirs",
            "watering_sensors",
            "watering_valves",
            "watering_waterMeter",
        ]

        print("Setting up attribute and geometry change listeners for layers:")

        for layer in layer_list:
            print(f"Processing layer: {layer}")
            real_layer = QgsProject.instance().mapLayersByName(layer)

            if not real_layer:
                print(f"Layer {layer} not found in the project.")
                continue

            real_layer = real_layer[0]
            print(f"Connected to real layer: {real_layer.name()}")

            def on_attribute_change(
                feature_id, attribute_index, new_value, layer=real_layer, sync=self.scenarioUnitOFWork.syncSystem
            ):
                print(
                    f"Attribute changed in layer {layer.name()}: feature_id={feature_id}, attribute_index={attribute_index}, new_value={new_value}"
                )
                WateringUtils.onChangesInAttribute(feature_id, attribute_index, new_value, layer, sync)

            # def on_geometry_change(feature_id, new_geometry, layer=real_layer, sync=self.scenarioUnitOFWork.syncSystem):
            #     print(f"Geometry changed in layer {layer.name()}: feature_id={feature_id}, new_geometry={new_geometry}")
            #     WateringUtils.onGeometryChange(feature_id, new_geometry, layer, sync)

            real_layer.attributeValueChanged.connect(on_attribute_change)
            # real_layer.geometryChanged.connect(lambda fid, geom: on_geometry_change(fid, geom, real_layer, self.scenarioUnitOFWork.syncSystem))

            print("Setup complete.")

    def onSynchFinished(self):
        iface.messageBar().pushMessage(
            "Success", "Synchronization completed successfully!", level=Qgis.Success, duration=6
        )

    def getClosestNode(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        elif os.environ.get("TOKEN") == None:
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5
            )
        elif (
            QgsProject.instance().mapLayersByName("watering_waterMeter")[0]
            and QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        ):
            WateringUtils.getClosestNodeToWaterMeter()

    def setStatusBarInfo(self, project_name, scenario_name):
        status_bar = iface.mainWindow().statusBar()

        if self.project_info:
            status_bar.removeWidget(self.project_info)
            # project_info_label.deleteLater()

        self.project_info = QLabel(f" Project: {project_name} | Scenario: {scenario_name} ", status_bar)
        status_bar.addWidget(self.project_info, 1)

    def getWateringCertificate(self):
        req = QNetworkRequest(QUrl("https://dev.watering.online"))
        reply = QgsNetworkAccessManager.instance().get(req)
        print("reply : ", reply)
        # cert_pem = self.get_certificate("dev.watering.online")
        # self.add_certificate_to_qgis(cert_pem)

    def get_certificate(self, hostname):
        conn = ssl.create_default_context().wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=hostname,
        )
        conn.connect((hostname, 443))
        cert_bin = conn.getpeercert(True)
        cert = ssl.DER_cert_to_PEM_cert(cert_bin)
        return cert

    def add_certificate_to_qgis(self, cert_pem):
        settings = QgsSettings()
        cert_pem_str = cert_pem.strip()
        trusted_certs = settings.value("network/ssl/trustedCertificates", [], type=str)

        if cert_pem_str not in trusted_certs:
            trusted_certs.append(cert_pem_str)
            settings.setValue("network/ssl/trustedCertificates", trusted_certs)
            print("Certificate added to trusted certificates.")
        else:
            print("Certificate is already trusted.")

        trusted_certs = settings.value("network/ssl/trustedCertificates", [], type=str)
        print("Trusted Certificates:", trusted_certs)
