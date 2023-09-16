# -*- coding: utf-8 -*-

# Import QGis
from qgis.core import QgsProject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.gui import QgsMapCanvas


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog

from .maptools.insertDemandNodeTool import InsertDemandNodeTool
from .maptools.selectNodeTool import SelectNodeTool
from .ui.watering_load import WateringLoad
from .ui.watering_login import WateringLogin
from .ui.watering_analysis import WateringAnalysis

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
            'Watering_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Watering API Connection')
        self.insertSensorAction = None
        self.selectElementAction = None
        self.canvas = iface.mapCanvas()
        self.first_click = True
        
        # Toolbar
        self.activeMapTool = None
        self.toolbar = self.iface.addToolBar("WaterIng Toolbar")
        self.toolbar.setObjectName("QGISWatering")
        self.toolbar.setVisible(True)
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Watering', message)


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
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_analysis.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Water Analysis'),
            callback=self.waterAnalysis,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        
        

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Watering API Connection'),
                action)
            self.iface.removeToolBarIcon(action)

        del self.toolbar

    def addLogin(self):
        self.dlg = WateringLogin()
        self.dlg.show()
        self.dlg.exec_()


    def InitializeProjectToolbar(self):
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_select.png'
        self.selectElementAction = self.add_action(
            icon_path,
            text=self.tr(u'Select Element'),
            callback=self.activateToolSelectMapElement,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.selectElementAction.setCheckable(True)
        self.toolSelectNode = SelectNodeTool(self.canvas)  #(self.canvas)
        self.toolSelectNode.setAction(self.selectElementAction)
        
        icon_path = ':/plugins/QGISPlugin_WaterIng/images/icon_add_node.png'
        self.insertSensorAction = self.add_action(
            icon_path,
            text=self.tr(u'Add Demand Node'),
            callback=self.activateToolInsertSensor,
            toolbar = self.toolbar,
            parent=self.iface.mainWindow())
        self.insertSensorAction.setCheckable(True)
        self.toolInsertNode = InsertDemandNodeTool(self.canvas)  
        self.toolInsertNode.setAction(self.insertSensorAction)

        
    def addLoad(self):
        if os.environ.get('TOKEN') == None:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("You must login to WaterIng first!"), level=1, duration=5)
        else:
            self.dlg = WateringLoad()
            self.dlg.show()      
            print("Before callong exec for watering load")    
            loadResult = self.dlg.exec_()
            print("Load result:")
            print(loadResult)
            if (loadResult == 1):
                #a project has been loaded as the result of showing the dialog
                print("Initializing toolbar after connecting to project")
                self.InitializeProjectToolbar()


                
            
    def waterAnalysis(self):
        if self.checkExistingProject() == False:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("Load a scenario first in Download Elements!"), level=1, duration=5)
        else:
            self.dlg = WateringAnalysis()
            self.dlg.show()
            self.dlg.exec_()
    


    def activateToolInsertSensor(self):
        if self.checkExistingProject() == False:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("Load a project scenario first!"), level=1, duration=5)
        else:
            if (self.insertSensorAction.isChecked()):
              print("Setting Map Tool = toolInsertNode")
              if (self.activeMapTool is not None):
                self.canvas.unsetMapTool(self.activeMapTool)  
                self.activeMapTool.action().setChecked(False)  
                #self.selectElementAction.setChecked(False)   
                
              self.canvas.setMapTool(self.toolInsertNode)
              self.activeMapTool = self.toolInsertNode
            else:
              self.canvas.unsetMapTool(self.toolInsertNode)
              self.activeMapTool = None

    def activateToolSelectMapElement(self):
        if self.checkExistingProject() == False:
            self.iface.messageBar().pushMessage(self.tr("Error"), self.tr("Load a project scenario first!"), level=1, duration=5)
        else:            
            if (self.selectElementAction.isChecked()):
              print("Setting Map Tool = toolSelectNode")
              if (self.activeMapTool is not None):
                self.canvas.unsetMapTool(self.activeMapTool)  
                self.activeMapTool.action().setChecked(False)  
                #self.insertSensorAction.setChecked(False)                      
              self.canvas.setMapTool(self.toolSelectNode)
              self.activeMapTool = self.toolSelectNode
            else:
              self.canvas.unsetMapTool(self.toolSelectNode)
              self.activeMapTool = None

            
    def checkExistingProject(self):
        scenario_id =  QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        return False if scenario_id == "default text" else True
        
    def print(self):
        print("Working")