# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.gui import QgsProjectionSelectionDialog
from qgis.core import QgsProject, QgsCoordinateReferenceSystem
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import os
from time import time, gmtime, strftime
from ..file_Converter import fileConverter
from ..watering_utils import WateringUtils
import requests




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
        self.ScenarioFK = None
        self.iface = iface
        self.file_path = None
        self.output_file_path = None
        self.mCrs = None
        self.output_file_name = None
        self.UrlGet = "/api/v1/ModelFile"
        self.convertINPFile.clicked.connect(lambda: self.selectorFilePath(0))
        self.selectCRSButton.clicked.connect(lambda: self.selctorCRS(0))
        self.convertINPFile.clicked.connect(lambda: self.onConvertINPFile(0))
        #self.downloadINPFile.clicked.connect(lambda: self.uploadWatering(0))

    def selectorFilePath(self, behavior):
        self.file_path = self.newINPDirectory.filePath()

        file_dir, file_name = os.path.split(self.file_path)
        output_file_name = os.path.splitext(file_name)[0] + '_converted' + os.path.splitext(file_name)[1]
        self.output_file_path = os.path.join(file_dir, output_file_name)
        self.output_file_name = output_file_name


    def selctorCRS(self, behavior):
        crs = QgsCoordinateReferenceSystem()
        mySelector = QgsProjectionSelectionDialog(self.iface.mainWindow())
        mySelector.setCrs(crs)
        if mySelector.exec():
            self.mCrs = mySelector.crs()
            self.selectedCRSLabel.setText(self.mCrs.authid())

    
    def onConvertINPFile(self, behavior):
        try:
            fileConv = fileConverter()
            fileConv.fileConvertion(self.file_path, self.mCrs, self.output_file_path)
            #Post file on watering
            self.ScenarioFK = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
            #url_API = f"https://dev.watering.online/api/v1/ModelFile?scenarioKeyId={self.ScenarioFK}"
            url_API = WateringUtils.getServerUrl() + self.UrlGet
            data = {'scenarioKeyId': self.ScenarioFK}
            headers = {'Authorization': "Bearer {}".format(self.token)}
            print(url_API)
            with open(self.output_file_path, 'rb') as file:
                file_data = file.read()
        
            response = requests.post(url_API, params=data, files = {'file': (self.output_file_name, file_data)} , headers=headers)

            if response.status_code == 200:
                print("File uploaded successfully!")

            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Watering INP")
            message_box.setText("File uploaded")
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()

        except FileNotFoundError:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("ScenariosNotLoaded")
            message_box.setText("Load Watering Data")
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()

        self.close()
        