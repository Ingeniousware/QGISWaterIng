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
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsProject

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
        self.INPMan.writeSections(self.options)
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
            self.INPMan.writeSections(self.options, fileName)
        
        
        
        # options = QFileDialog.Options()
        # fileName, _ = QFileDialog.getSaveFileName(self, "Seleccionar archivo", "", "Archivo de Epanet(*.inp)", options = options)
        # if fileName:
        #     print(fileName)
    
    # Función para abrir el QFileDialog
    def abrir_dialogo_archivo(self):
        # Configurar el título y la ruta inicial del diálogo
        dialogo = QFileDialog()
        dialogo.setWindowTitle("Seleccionar archivo")
        dialogo.setDirectory("C:\\Temp")  # Establece el directorio inicial

        # Filtrar tipos de archivos (opcional)
        dialogo.setNameFilter("Archivos de texto (*.txt);;Todos los archivos (*)")

        # # Mostrar el diálogo y capturar la selección del usuario
        # if dialogo.exec_() == QFileDialog.Accepted:
        #     ruta_archivo = dialogo..selectedFiles()[0]  # Obtiene la ruta del archivo seleccionado
        #     print("Archivo seleccionado:", ruta_archivo)
        #     # Aquí puedes agregar más lógica para trabajar con el archivo seleccionado
        
        # Mostrar el diálogo y capturar la selección del usuario
        ruta_archivo, _ = dialogo.getSaveFileName(None, "Guardar archivo", "", "Archivos de texto (*.txt);;Todos los archivos (*)")
        
        if ruta_archivo:
            print("Archivo guardado en:", ruta_archivo)
            # Aquí puedes agregar lógica para guardar datos en el archivo seleccionado



# class SelectDirectoryAlgorithm(QgsProcessingAlgorithm):
#     OUTPUT_DIR = 'OUTPUT_DIR'

#     def initAlgorithm(self, config=None):
#         self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_DIR,
#             'Seleccione el directorio de salida'
#         ))

#     def processAlgorithm(self, parameters, context, feedback):
#         output_dir = self.parameterAsString(parameters, self.OUTPUT_DIR, context)
#         feedback.pushInfo(f'Directorio seleccionado: {output_dir}')
#         return {self.OUTPUT_DIR: output_dir}

#     def name(self):
#         return 'select_directory'

#     def displayName(self):
#         return 'Seleccionar Directorio'

#     def group(self):
#         return 'Mis Herramientas'

#     def groupId(self):
#         return 'mis_herramientas'

#     def createInstance(self):
#         return SelectDirectoryAlgorithm()