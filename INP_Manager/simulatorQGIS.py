# -*- coding: utf-8 -*-

"""
***************************************************************************
    INPManager.py
    ---------------------
    Date                 : Febrero 2025
    Copyright            : (C) 2025 by Ingeniowarest
    Email                : 
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Ingenioware                                                       *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtWidgets import QMessageBox


from ..ui.watering_inp_options import WateringINPOptions
from .INPManager import INPManager



class SimulatorQGIS:
    """
    
    """
    def __init__(self):
        self._inpMan = INPManager()
        self.options = WateringINPOptions()
        print("")

    @property
    def INPMan(self):
        return self._inpMan
    
    def run_1(self, a: str = ""):
        #inpMan1 = INPManager()
        self.INPMan.writeSections()
        self.INPMan.getAnalysisResults()


    def MessageInformation(message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Información")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def viewOptions(self):
        self.options.show()
        if self.options.exec_() == 1:
            print("0001: Dialogo abierto...")
        else:
            print("0002: Dialogo cerrado...")