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

from qgis.PyQt.QtWidgets import QFileDialog # type: ignore
from qgis.core import QgsProject

from ..ui.watering_simulation_manager import WateringSimulationManagerDialog # type: ignore
from ..ui.watering_inp_options import WateringINPOptionsDialog
from .INPManager import INPManager
from .inp_utils import INP_Utils
from .node_link_ResultType import LinkResultType, NodeResultType
from .customdialog import show_input_dialog
from .inp_options_enum import INP_Options
from .dataType import TimeOptions


class SimulatorQGIS:
    """
    
    """
    def __init__(self):
        self._inpMan = INPManager()
        
        self.optionsDialog = WateringINPOptionsDialog(self.INPMan.options)
        # print(self.options.getOption(INP_Options.Hydraulics))
        self.nodeResultType: NodeResultType = NodeResultType.pressure
        self.linkResultType: LinkResultType = LinkResultType.flowrate

    @property
    def INPMan(self):
        return self._inpMan

    def run(self):
        """"""
        self.time = -1
        self.INPMan.getAnalysisResults()
        
        time: TimeOptions = self.INPMan.options[INP_Options.Times]
        _, rtime, _ = INP_Utils.hora_to_int(time.duration)
        print("---------------- Fin de los cáculos ------------------------")
        if (rtime > 0):
            element = [v[0] for v in INP_Utils.static_elements.values()]
            sim_manager = WateringSimulationManagerDialog(rtime, element)
            sim_manager.timeChanged.subscribe(self.onTimeChanged)
            sim_manager.elementDoubleClicked.subscribe(self.onElementDoubleClicked)
            
            sim_manager.show()
            if sim_manager.exec_() == 1:
                print("001: Dialogo abierto...\n")
            # else:
            #     print("0002: Dialogo cerrado...")

    
    def getType(self, value):
        for item in INP_Utils.get_all().values():
            if (item[0] == value):
                return item[1]
        return None
    
    def onElementDoubleClicked(self, index, nodeResultType, linkResultType):
        typeval = self.getType(index)
        self.INPMan.getValues_for_element(index, typeval, nodeResultType, linkResultType)
            
        
        
    def MessageInformation(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Información")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def viewOptions(self):
        self.optionsDialog.show()
        # if self.options.exec_() == 1:
        #     print("001: Dialogo abierto...\n", self.options.classes["Hydraulics"])
            # path = INP_Utils.default_working_directory() + "\\optins.json"
            # print("002: ", path)
            # self.options.save(path)
        # else:
        #     print("0002: Dialogo cerrado...")
    
    
    def exportINP(self):
        # Configurar el título y la ruta inicial del diálogo
        dialogo = QFileDialog()
        dialogo.setWindowTitle("Seleccionar archivo")
        dialogo.setDirectory(QgsProject.instance().homePath())  # Establece el directorio inicial

        # Filtrar tipos de archivos (opcional)
        dialogo.setNameFilter("Archivos de Epanet (*.inp)")

        # # Mostrar el diálogo y capturar la selección del usuario
        # if dialogo.exec_() == QFileDialog.Accepted:
        #     ruta_archivo = dialogo..selectedFiles()[0]  # Obtiene la ruta del archivo seleccionado
        #     print("Archivo seleccionado:", ruta_archivo)
        #     # Aquí puedes agregar más lógica para trabajar con el archivo seleccionado
        
        # Mostrar el diálogo y capturar la selección del usuario
        fileName, _ = dialogo.getSaveFileName(None, "Guardar archivo", "", "Archivos de Epanet (*.inp)")
        
        if fileName:
            fileName = fileName.replace("/", "\\")
            self.INPMan.writeSections(fileName)


    def exportResults(self):
        # pass
        # self.time += 1
        # print(self.time)
        # result = self.INPMan.getResultforTime(self.time)
        # if result is not None:
        #     print(result.values)
        # a = [v for k, v in INP_Utils.static_elements.items()]
        # element = [v[0] for v in INP_Utils.static_elements.values()]
        # # print(element)
        # sim_manager = WateringSimulationManagerDialog(3, element)
        
        # # sim_manager.previousEvent.subscribe(self.onPrevious)
        # # sim_manager.nextEvent.subscribe(self.onNext)
        # sim_manager.timeChanged.subscribe(self.onTimeChanged)
        # sim_manager.elementDoubleClicked.subscribe(self.onElementDoubleClicked)
        
        # sim_manager.show()
        # if sim_manager.exec_() == 1:
        #     print("001: Dialogo abierto...\n")
        # else:
        #     print("0002: Dialogo cerrado...")
        self.INPMan.getMetrics()
    
    
    def onTimeChanged(self, time, nodeResultType, linkResultType):
        self.INPMan.getAnalysisResults_for_time(time, nodeResultType, linkResultType)