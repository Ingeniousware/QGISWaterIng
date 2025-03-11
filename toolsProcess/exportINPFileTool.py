# -*- coding: utf-8 -*-

"""
***************************************************************************
    exportINPFileTool.py
    ---------------------
    Date                 : Marzo 2025
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

from ..INP_Manager.INPManager import INPManager
from qgis.PyQt.QtWidgets import QFileDialog # type: ignore
from qgis.core import QgsProject

from ..watering_utils import WateringUtils


class ExportINPFileTool:
    def __init__(self, iface):
        self.iface = iface


    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        else:
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
                inpFile = INPManager()
                inpFile.writeSections(fileName)
                # self.INPMan.writeSections(fileName)