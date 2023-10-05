# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.gui import QgsProjectionSelectionDialog
from qgis.core import QgsProject, QgsCoordinateReferenceSystem
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import os
from time import time, gmtime, strftime
from ..file_Converter import fileConverter




FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_InpImport_dialog.ui'))


class WateringINPImport(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self,iface,parent=None):
        """Constructor."""
        super(WateringINPImport, self).__init__(parent)
        self.setupUi(self)
        self.token = os.environ.get('TOKEN')
        self.ProjectFK = None
        self.SourceFK = None
        self.iface = iface
        self.file_path = None
        self.mCrs = None
        self.convertINPFile.clicked.connect(lambda: self.selectorFilePath(0))
        self.selectCRSButton.clicked.connect(lambda: self.selctorCRS(0))
        self.convertINPFile.clicked.connect(lambda: self.onConvertINPFile(0))

    def selectorFilePath(self, behavior):
        self.file_path = self.newINPDirectory.filePath()

    def selctorCRS(self, behavior):
        crs = QgsCoordinateReferenceSystem()
        mySelector = QgsProjectionSelectionDialog(self.iface.mainWindow())
        mySelector.setCrs(crs)
        if mySelector.exec():
            self.mCrs = mySelector.crs()
            self.selectedCRSLabel.setText(self.mCrs.authid())

    
    def onConvertINPFile(self, behavior):
        fileConv = fileConverter()
        fileConv.fileConvertion(self.file_path, self.mCrs)
        self.close()
        