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
        self.loginBtn.clicked.connect(self.login)
        self.buttonAcceptCancel.accepted.connect(self.nextDlg)
        self.buttonAcceptCancel.rejected.connect(self.close)
        self.token = None
        self.logged = False
            
    def login(self):
        
        #url_login = "api/v1/AuthManagement/Login"
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
                print(response)
                if response.status_code == 200:
                    self.errorLogin.setStyleSheet("color: lightgreen")
                    self.errorLogin.setText("Login Successful.")
                    os.environ['TOKEN'] = response.json()["token"]
                    WateringTimer.setTokenTimer()
                    self.token = os.environ['TOKEN']
                    self.logged = True
                else:
                    self.errorLogin.setStyleSheet("color: red")
                    self.errorLogin.setText("Invalid email or password.")
            except requests.ConnectionError:
                iface.messageBar().pushMessage(self.tr("Error"), self.tr("Failed to connect to the WaterIng, check your connection."), level=1, duration=5)
            except requests.Timeout:
                iface.messageBar().pushMessage(self.tr("Error"), self.tr("Request timed out."), level=1, duration=5)
            except:
                iface.messageBar().pushMessage(self.tr("Error"), self.tr("Unable to connect to WaterIng."), level=1, duration=5)
                
                
    def nextDlg(self):
        if self.logged == False:
            self.errorLogin.setStyleSheet("color: red")
            self.errorLogin.setText("Complete the login to WaterIng.")
        else:
            #run Load Elements dialog
            self.close()
            self.done(True)  #self.close()  instead of just closing we call done(true) to return 1 as result of this dialog modal execution