# -*- coding: utf-8 -*-

"""
***************************************************************************
    abstractAnalysisLocal.py
    ---------------------
    Date                 : Enero 2025
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


from abc import abstractmethod
import os
from wntr.sim.results import SimulationResults
from qgis.core import QgsProject # type: ignore

# from ..wntr.epanet.util import EN
from ..INP_Manager.inp_utils import INP_Utils
from .abstractAnalysis import AbstractAnalysis
# from ..wntr.epanet.toolkit import ENepanet


class AbstractAnalysisLocal(AbstractAnalysis):
    """
    Clase base para la visualización de lo los resultado de la modelación en QGIS de proyectos locales.

    Parameters
    ----------
    enData: ENepanet
        Wrapper class to load the EPANET DLL object.
    analysisElemntType: AnalysisEmentType
        Tipo de elemento a análizar.
    analysisExecutionId: str
        Representa el identificador de la ejecución.
    datetime: str
        Representa una hora.
    """
    def __init__(self, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)


    @abstractmethod
    def elementAnalysisResults(self):
         print("Método base no implementado...")


    def addCSVNonSpatialLayerToPanel(self, fileName, layerName):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if not shapeGroup:
            shapeGroup = root.addGroup("Analysis")

        date = self.datetime.replace(":", "")
        project_path = INP_Utils.default_working_directory()
        date_folder_path = os.path.join(project_path, "Analysis", date)

        self.loadCSVLayer(os.path.join(date_folder_path, fileName), layerName, shapeGroup)