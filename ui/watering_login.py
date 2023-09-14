# -*- coding: utf-8 -*-

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

import os
import requests
from .watering_load import WateringLoad

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_login_dialog.ui'))


class WateringLogin(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(WateringLogin, self).__init__(parent)
        self.setupUi(self)
        self.loginBtn.clicked.connect(self.login)
        self.buttonNext.accepted.connect(self.nextDlg)
        self.buttonNext.rejected.connect(self.close)
        self.token = None
        self.logged = False
            
    def login(self):
        
        url_login = "https://dev.watering.online/api/v1/AuthManagement/Login"
        email = self.emailInput.text()
        password = self.passwordInput.text()
        
        if len(email)==0 or len(password)==0:
            self.errorLogin.setStyleSheet("color: red")
            self.errorLogin.setText("Please input all fields.")
        else:
            myobj = {'email': "{}".format(email), 'password': "{}".format(password)}
            response = requests.post(url_login, json=myobj)
            if response.status_code == 200:
                self.errorLogin.setStyleSheet("color: lightgreen")
                self.errorLogin.setText("Login Successful.")
                os.environ['TOKEN'] = response.json()["token"]
                self.token = os.environ['TOKEN']
                self.logged = True
            else:
                self.errorLogin.setStyleSheet("color: red")
                self.errorLogin.setText("Invalid email or password.")
                
    def nextDlg(self):
        if self.logged == False:
            self.errorLogin.setStyleSheet("color: red")
            self.errorLogin.setText("Complete the login to WaterIng.")
        else:
            #run Load Elements dialog
            self.close()
            self.dlgLoad = WateringLoad()
            self.dlgLoad.show()
            self.dlgLoad.exec_()