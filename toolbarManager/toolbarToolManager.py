from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QToolBar
from qgis.utils import iface
from qgis.gui import QgsMapTool, QgsMapToolPan
from PyQt5.QtCore import Qt

from functools import partial
import os


from ..watering_utils import WateringUtils
from ..ui.watering_datachannels import WateringDatachannels
from ..ui.watering_waterBalance import WateringWaterBalance
from ..ui.watering_getlastmeasurement import WateringOnlineMeasurements
from ..ui.watering_optimization import WaterOptimization
from ..ui.watering_analysis import WateringAnalysis
from ..ui.watering_pumpModels import WateringPumpModels
from ..toolsMap.toolbarAction import toolbarAction
from ..ActionManagement.identifyElementAction import WateringIdentifyTool

from ..ui.watering_analysis_1 import WateringAnalysis_1
from ..ui.watering_resilience_metrics import WateringResilienceMetric


class toolbarToolManager:

    def __init__(self, toolbar, parentWindow, canvas):
        """Constructor."""
        self.activeMapTool = None
        self.activeToolController = None
        self.canvas = canvas
        self.toolbar = toolbar
        self.parentWindow = parentWindow
        self.panTool = QgsMapToolPan(canvas)

        # Actions
        self.editElementsAction = None
        self.toolImportINPFile = None
        self.toolImportShapeFile = None
        self.toolExportINPFile = None
        self.toolReviewNetwork = None
        self.toolSelectionReview = None
        self.toolDemandPattern = None
        self.insertDemandNodeAction = None
        self.insertTankNodeAction = None
        self.insertWaterPipeAction = None
        self.insertReservoirNodeAction = None
        self.insertValveNodeAction = None
        self.insertPumpNodeAction = None
        self.insertSensorNodeAction = None
        self.insertWaterMeterNodeAction = None
        self.toolDeleteElementAction = None
        self.selectElementAction = None
        self.wateringIdentifyAction = None
        self.openOptimizationManagerAction = None
        self.openPumpModels = None
        self.readAnalysisAction = None
        self.readAnalysisAction_1 = None
        self.readMeasurementsAction = None
        self.waterBalanceAction = None
        self.getLastMeasurementAction = None
        self.undoAction = None
        self.redoAction = None
        
        self.analysisOptions = None
        self.localAnalysisWithWNTR = None
        # self.metricsAnalysis = None
        self.addGraphics = None
        self.readAnalysisAction_2 = None
        self.resilienceMetricAction = None

        # Dock
        self.analysisDockPanel = WateringAnalysis(iface)
        iface.addDockWidget(Qt.RightDockWidgetArea, self.analysisDockPanel)
        
        self.analysisDockPanel_1 = WateringAnalysis_1(iface)
        iface.addDockWidget(Qt.RightDockWidgetArea, self.analysisDockPanel_1)
        
        self.resilienceMetric = WateringResilienceMetric(iface)
        iface.addDockWidget(Qt.RightDockWidgetArea, self.resilienceMetric)

    def initializeToolbarButtonActions(self):
        # Edit
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/editElements.svg"
        self.editElementsAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Edit Elements"),
            callback=self.activeControllerTool,
            toolbar=self.toolbar,
            parent=self.parentWindow,
        )
        self.editElementsAction.setCheckable(True)
        # self.editElementsAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.editElementsAction.toggled.connect(self.activateEditTool)

        # Analysis =================================================================================================
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/analysisChart.svg"
        self.readAnalysisAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Water Network Analysis", "QGISWaterIng"),
            # text=self.tr(u'Water Network Analysis'),
            callback=self.activeControllerTool,
            toolbar=self.toolbar,
            parent=self.parentWindow,
        )
        self.readAnalysisAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.readAnalysisAction.setCheckable(True)
        self.readAnalysisAction.toggled.connect(self.activateWaterAnalysisTool)
        
        # Analysis_1 para mostrar el menú de las opciones de análisis.
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/networkAnalysis.svg"
        self.readAnalysisAction_1 = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Water Network Analysis", "QGISWaterIng"),
            # text=self.tr(u'Water Network Analysis'),
            callback=self.activeControllerTool,
            toolbar=self.toolbar,
            parent=self.parentWindow,
        )
        # self.readAnalysisAction_1.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.readAnalysisAction_1.setCheckable(True)
        self.readAnalysisAction_1.toggled.connect(self.activateAnalysisTool)

        # Optimization Tools
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/optimizationTools.svg"
        self.optimizationToolsAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Optimization Tools"),
            callback=self.activeControllerTool,
            toolbar=self.toolbar,
            parent=self.parentWindow,
        )
        self.optimizationToolsAction.setCheckable(True)
        # self.optimizationToolsAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.optimizationToolsAction.toggled.connect(self.activateOptimizationTool)

        # Monitoring Tools
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/monitoring.svg"
        self.monitoringToolsAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Monitoring Tools"),
            callback=self.activeControllerTool,
            toolbar=self.toolbar,
            parent=self.parentWindow,
        )
        self.monitoringToolsAction.setCheckable(True)
        self.monitoringToolsAction.toggled.connect(self.activateMonitoringTool)

        # Measurements
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/monitoring.svg"
        self.readMeasurementsAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Get Measurements"),
            callback=self.activateMeasurementTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.readMeasurementsAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Water Balance
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/monitoring.svg"
        self.waterBalanceAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Water Balance"),
            callback=self.waterBalanceTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.waterBalanceAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Get Last Online Measurement
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/monitoring.svg"
        self.getLastMeasurementAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Get Last Online Measurement"),
            callback=self.getLastOnlineMeasurementTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.getLastMeasurementAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Identify
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/select.svg"
        self.wateringIdentifyAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Identify features"),
            callback=self.activateMapTool,
            toolbar=self.toolbar,
            parent=self.parentWindow,
        )
        self.wateringIdentifyAction.setEnabled(not WateringUtils.isScenarioNotOpened())
        self.wateringIdentifyAction.setCheckable(True)
        # self.wateringIdentifyAction.toggled.connect(self.activateWateringIdentifyTool)

        # Network Review
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/automaticNetworkReview.svg"
        self.toolReviewNetwork = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Network Review"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolReviewNetwork.setCheckable(False)
        self.toolReviewNetwork.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Selection Review
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/automaticNetworkReview.svg"
        self.toolSelectionReview = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Selection Review"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolSelectionReview.setCheckable(False)
        self.toolSelectionReview.setEnabled(not WateringUtils.isScenarioNotOpened())

        # import elements
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/import.svg"
        self.toolImportINPFile = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Import INP File"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolImportINPFile.setCheckable(False)
        self.toolImportINPFile.setEnabled(not WateringUtils.isScenarioNotOpened())

        # import shape file
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/import.svg"
        self.toolImportShapeFile = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Import Shape File"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolImportShapeFile.setCheckable(False)
        self.toolImportShapeFile.setEnabled(not WateringUtils.isScenarioNotOpened())

        # export inp file
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/exportar_inp.svg"
        self.toolExportINPFile = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Export INP File"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolExportINPFile.setCheckable(False)
        self.toolExportINPFile.setEnabled(not WateringUtils.isScenarioNotOpened())

        # demand patterns
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/icon_pattern_GT.svg"
        self.toolDemandPattern = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Demand Patterns"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolDemandPattern.setCheckable(False)
        self.toolDemandPattern.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Demand Nodes
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/node.svg"
        self.insertDemandNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Demand Node"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertDemandNodeAction.setCheckable(True)
        self.insertDemandNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Tanks
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/tank.svg"
        self.insertTankNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Tank Node"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertTankNodeAction.setCheckable(True)
        self.insertTankNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Pipes
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/pipe.svg"
        self.insertWaterPipeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Water Pipe"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertWaterPipeAction.setCheckable(True)
        self.insertWaterPipeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Reservoirs
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/reservoir.svg"
        self.insertReservoirNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Reservoir Node"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertReservoirNodeAction.setCheckable(True)
        self.insertReservoirNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Valves
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/valve.svg"
        self.insertValveNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Valve Node"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertValveNodeAction.setCheckable(True)
        self.insertValveNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Pumps
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/pump.svg"
        self.insertPumpNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Pump Node"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertPumpNodeAction.setCheckable(True)
        self.insertPumpNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Water Meters
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/Icon_waterMeter_GT.svg"
        self.insertWaterMeterNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Water Meter"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertWaterMeterNodeAction.setCheckable(True)
        self.insertWaterMeterNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Sensors
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/sensor.svg"
        self.insertSensorNodeAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Sensor Node"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.insertSensorNodeAction.setCheckable(True)
        self.insertSensorNodeAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Undo
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/backward.svg"
        self.undoAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("unDo"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.undoAction.setCheckable(False)
        self.undoAction.setEnabled(False)

        # Redo
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/forward.svg"
        self.redoAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("reDo"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.redoAction.setCheckable(False)
        self.redoAction.setEnabled(False)

        # Delete Element
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/trash.svg"
        self.toolDeleteElementAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Delete Element"),
            callback=self.activateMapTool,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.toolDeleteElementAction.setCheckable(True)
        self.toolDeleteElementAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Optimization
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/optimization.svg"
        self.openOptimizationManagerAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Optimization"),
            callback=self.waterOptimization,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.openOptimizationManagerAction.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Pump Models
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/optimization.svg"
        self.openPumpModels = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Pump Models"),
            callback=self.wateringPumpModels,
            toolbar=None,
            parent=self.parentWindow,
        )
        self.openPumpModels.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Analysis Options
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/optins.svg"
        self.analysisOptions = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Analysis Options"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )

        self.analysisOptions.setCheckable(False)
        self.analysisOptions.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Local Analysis With WNTR
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/run_epanet.svg"
        self.localAnalysisWithWNTR = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Local Analysis With WNTR"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )

        self.localAnalysisWithWNTR.setCheckable(False)
        self.localAnalysisWithWNTR.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Metrics Analysis
        # icon_path = ":/plugins/QGISPlugin_WaterIng/images/01_01.svg"
        # self.metricsAnalysis = self.addMapToolButtonAction(
        #     icon_path,
        #     text=WateringUtils.tr("Metrics Analysis"),
        #     callback=self.activateActionTool,
        #     toolbar=None,
        #     parent=self.parentWindow,
        # )

        # self.metricsAnalysis.setCheckable(False)
        # self.metricsAnalysis.setEnabled(not WateringUtils.isScenarioNotOpened())

        # Add Graphics
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/analysisChart.svg"
        self.addGraphics = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Add Graphics"),
            callback=self.activateActionTool,
            toolbar=None,
            parent=self.parentWindow,
        )

        self.addGraphics.setCheckable(False)
        self.addGraphics.setEnabled(not WateringUtils.isScenarioNotOpened())
        
        # Analysis =================================================================================================
        icon_path = ":/plugins/QGISPlugin_WaterIng/images/analysisServer.svg"
        self.readAnalysisAction_2 = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Water Network Analysis", "QGISWaterIng"),
            callback=self.activeAnalysisDockPanel,
            toolbar=None,
            parent=self.parentWindow,
        )

        self.readAnalysisAction_2.setCheckable(True)
        self.readAnalysisAction_2.setEnabled(not WateringUtils.isScenarioNotOpened())
        # self.readAnalysisAction_2.toggled.connect(self.activateWaterAnalysisTool)


        icon_path = ":/plugins/QGISPlugin_WaterIng/images/01_01.svg"
        self.resilienceMetricAction = self.addMapToolButtonAction(
            icon_path,
            text=WateringUtils.tr("Water resilience metric", "QGISWaterIng"),
            callback=self.activeRecilienceMetricDockPanel,
            toolbar=None,
            parent=self.parentWindow,
        )

        self.resilienceMetricAction.setCheckable(True)
        self.resilienceMetricAction.setEnabled(not WateringUtils.isScenarioNotOpened())


    def activeAnalysisDockPanel(self, action):
        is_visible = not self.analysisDockPanel_1.isVisible()
        self.analysisDockPanel_1.setVisible(is_visible)
        if (is_visible):
            self.analysisDockPanel_1.initializeRepository()


    def activeRecilienceMetricDockPanel(self, action):
        is_visible = not self.resilienceMetric.isVisible()
        self.resilienceMetric.setVisible(is_visible)
        if (is_visible):
            self.resilienceMetric.initializeRepository()


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
        parent=None,
    ):

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

        # actions.append(action)

        return action

    def activateMapTool(self, mapToolButtonAction):
        if mapToolButtonAction.isChecked():
            print("Setting Map Tool = ", mapToolButtonAction)
            if self.activeMapTool is not None:
                if self.activeMapTool.action() is not None:
                    self.canvas.unsetMapTool(self.activeMapTool)
                    self.activeMapTool.action().setChecked(False)
            # this should be happening at updateActionScenarioStateOpen self.toolInsertDemandNode = InsertDemandNodeTool(self.canvas, self.scenarioUnitOFWork.waterDemandNodeRepository)
            print("maptool -> ", mapToolButtonAction.MapTool)
            self.canvas.setMapTool(mapToolButtonAction.MapTool)
            self.activeMapTool = mapToolButtonAction.MapTool
        else:
            self.canvas.unsetMapTool(mapToolButtonAction.MapTool)
            self.activeMapTool = None

    def activateActionTool(self, toolButtonAction):
        toolButtonAction.MapTool.ExecuteAction()

    def activeControllerTool(self, toolControllerAction):
        if toolControllerAction.isChecked():
            if self.activeToolController is not None:
                self.activeToolController.setChecked(False)
            self.activeToolController = toolControllerAction
        else:
            self.activeToolController = None

    def activateEditTool(self, checked):
        editTools = [
            self.toolImportINPFile,
            self.toolImportShapeFile,
            self.toolExportINPFile,
            self.toolReviewNetwork,
            self.toolSelectionReview,
            self.toolDemandPattern,
            self.insertDemandNodeAction,
            self.insertTankNodeAction,
            self.insertWaterPipeAction,
            self.insertReservoirNodeAction,
            self.insertValveNodeAction,
            self.insertPumpNodeAction,
            self.insertWaterMeterNodeAction,
            self.insertSensorNodeAction,
            self.toolDeleteElementAction,
            self.undoAction,
            self.redoAction,
        ]

        if checked:
            for tool in editTools:
                self.toolbar.addAction(tool)
        else:
            self.canvas.setMapTool(self.panTool)
            for tool in editTools:
                self.toolbar.removeAction(tool)

                tool.setChecked(False)


    def activateAnalysisTool(self, checked):
        """ Análisis local con WNTR, el de opciones de análisis, el de mostrar las métricas así como el de adicionar un gráfico de resultados
            Análisis local con WNTR
            Opciones de análisis
            Análisis de métricas
            Addicionar un gráficos
        """
        analysisTool = [
            self.readAnalysisAction_2,
            self.analysisOptions,
            self.localAnalysisWithWNTR,
            self.resilienceMetricAction,
            # self.metricsAnalysis,
            self.addGraphics]

        if checked:
            for tool in analysisTool:
                self.toolbar.addAction(tool)
        else:
            self.canvas.setMapTool(self.panTool)
            for tool in analysisTool:
                self.toolbar.removeAction(tool)

                tool.setChecked(False)


    def activateOptimizationTool(self, checked):
        optimizationTools = [self.openOptimizationManagerAction, self.openPumpModels]

        if checked:
            for tool in optimizationTools:
                self.toolbar.addAction(tool)
        else:
            self.canvas.setMapTool(self.panTool)
            for tool in optimizationTools:
                self.toolbar.removeAction(tool)

                tool.setChecked(False)

    def activateMonitoringTool(self, checked):
        monitoringTools = [self.readMeasurementsAction, self.waterBalanceAction, self.getLastMeasurementAction]

        if checked:
            for tool in monitoringTools:
                self.toolbar.addAction(tool)
        else:
            self.canvas.setMapTool(self.panTool)
            for tool in monitoringTools:
                self.toolbar.removeAction(tool)
                tool.setChecked(False)

    def waterOptimization(self, second):
        if WateringUtils.isScenarioNotOpened():
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"),
                WateringUtils.tr("Load a project scenario first in Download Elements!"),
                level=1,
                duration=5,
            )
        if os.environ.get("TOKEN") == None:
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"), WateringUtils.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            dlg = WaterOptimization()
            dlg.show()
            dlg.exec_()

    def wateringPumpModels(self, second):
        if WateringUtils.isScenarioNotOpened():
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"),
                WateringUtils.tr("Load a project scenario first in Download Elements!"),
                level=1,
                duration=5,
            )
        if os.environ.get("TOKEN") == None:
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"), WateringUtils.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            dlg = WateringPumpModels()
            dlg.show()
            dlg.exec_()


    def activateMeasurementTool(self, *args):
        if WateringUtils.isScenarioNotOpened():
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"),
                WateringUtils.tr("Load a project scenario first in Download Elements!"),
                level=1,
                duration=5,
            )
        if os.environ.get("TOKEN") == None:
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"), WateringUtils.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            try:
                dlg = WateringDatachannels()
                dlg.show()
                dlg.exec_()
            except:
                iface.messageBar().pushMessage(
                    WateringUtils.tr("Error"),
                    WateringUtils.tr("No data source available for the project."),
                    level=1,
                    duration=5,
                )

    def waterBalanceTool(self, second):
        if WateringUtils.isScenarioNotOpened():
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"),
                WateringUtils.tr("Load a project scenario first in Download Elements!"),
                level=1,
                duration=5,
            )
        if os.environ.get("TOKEN") == None:
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"), WateringUtils.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            dlg = WateringWaterBalance()
            dlg.show()
            dlg.exec_()

    def activateWaterAnalysisTool(self):
        # if WateringUtils.isScenarioNotOpened():
        #     iface.messageBar().pushMessage(
        #         WateringUtils.tr("Error"),
        #         WateringUtils.tr("Load a project scenario first in Download Elements!"),
        #         level=1,
        #         duration=5,
        #     )
        # if os.environ.get("TOKEN") == None:
        #     iface.messageBar().pushMessage(
        #         WateringUtils.tr("Error"), WateringUtils.tr("You must connect to WaterIng!"), level=1, duration=5
        #     )
        # else:
        #     self.analysisDockPanel.initializeRepository()
        # self.analysisDockPanel.show()
            
        is_visible = not self.analysisDockPanel_1.isVisible()
        self.analysisDockPanel_1.setVisible(is_visible)
        if (is_visible):
            self.analysisDockPanel_1.initializeRepository()

    def getLastOnlineMeasurementTool(self, second):
        if WateringUtils.isScenarioNotOpened():
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"),
                WateringUtils.tr("Load a project scenario first in Download Elements!"),
                level=1,
                duration=5,
            )
        if os.environ.get("TOKEN") == None:
            iface.messageBar().pushMessage(
                WateringUtils.tr("Error"), WateringUtils.tr("You must connect to WaterIng!"), level=1, duration=5
            )
        else:
            dlg = WateringOnlineMeasurements()
            dlg.show()
            dlg.exec_()
