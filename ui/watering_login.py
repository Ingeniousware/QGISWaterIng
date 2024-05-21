# -*- coding: utf-8 -*-

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject
from qgis.utils import iface

import os
import requests
from ..watering_utils import WateringUtils
from ..watering_utils import WateringTimer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_login_dialog.ui'))


class WateringLogin(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(WateringLogin, self).__init__(parent)
        self.setupUi(self)
        self.buttonAcceptCancel.accepted.connect(self.login)
        self.buttonAcceptCancel.rejected.connect(self.close)
        self.token = None
            
    def login(self):
        email = self.emailInput.text()
        password = self.passwordInput.text()
        
        server_url = self.serverInput.text() or "https://dev.watering.online"
        QgsProject.instance().writeEntry("watering", "server_url", server_url)
        
        url_login = WateringUtils.getServerUrl() + "/api/v1/AuthManagement/Login"
        
        if len(email)==0 or len(password)==0:
            self.errorLogin.setStyleSheet("color: red")
            self.errorLogin.setText("Please input all fields.")
        else:
            loginParams = {'email': "{}".format(email), 'password': "{}".format(password)}
            try:
                response = requests.post(url_login, json=loginParams)
                if response.status_code == 200:
                    os.environ['TOKEN'] = response.json()["token"]
                    WateringTimer.setTokenTimer()
                    self.token = os.environ['TOKEN']
                    self.nextDlg()
                else:
                    self.errorLogin.setStyleSheet("color: red")
                    self.errorLogin.setText("Invalid email or password.")
            except requests.ConnectionError:
                WateringUtils.error(self.tr("Failed to connect to the WaterIng, check your connection."))
            except requests.Timeout:
                WateringUtils.error(self.tr("Request timed out."))
            except:
                WateringUtils.error(self.tr("Unable to connect to WaterIng."))
                
    def nextDlg(self):
        # Usage of self.close() instead of just closing we call 
        # done(true) to return 1 as result of this dialog modal execution
        self.close()
        self.done(True)