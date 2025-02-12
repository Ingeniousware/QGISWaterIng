# -*- coding: utf-8 -*-

"""
***************************************************************************
    simulatorQGIS.py
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
from .inp_utils import INP_Utils



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
    
    def run(self):
        """"""
        self.INPMan.writeSections()
        self.INPMan.getAnalysisResults()


    def MessageInformation(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Información")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def viewOptions(self):
        self.options.show()
        if self.options.exec_() == 1:
            print("001: Dialogo abierto...\n", self.options.classes["Hydraulics"])
            # path = INP_Utils.default_working_directory() + "\\optins.json"
            # print("002: ", path)
            # self.options.save(path)
        # else:
        #     print("0002: Dialogo cerrado...")