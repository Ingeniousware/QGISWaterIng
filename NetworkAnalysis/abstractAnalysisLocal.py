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


import csv
import os

from qgis.core import QgsProject

from ..wntr.epanet.util import EN
from ..INP_Manager.inp_utils import INP_Utils
from .analysisEmentType import AnalysisEmentType
from .abstractAnalysis import AbstractAnalysis
from ..wntr.epanet.toolkit import ENepanet


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
    def __init__(self, enData: ENepanet, analysisElemntType: AnalysisEmentType, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)
        self.__enData = enData
        self.__analysisElemntType = analysisElemntType


    def elementAnalysisResults(self):
        print("Ingresando elementos...")
        filename = self.analysisExecutionId
        # elements = []
        # subelement = []
        # for item in self.fields_to_add:
        #     subelement.append(item.name)
        # elements.append(subelement)
        # elements = [[item.name for item in self.fields_to_add]]
        elements = ["nodeKey, pressure", "waterDemand", "waterAge"]
        if self.__analysisElemntType == AnalysisEmentType.NODE:
            print("Ingresando elementos de tipo nodo...")
            nNodes = self.__enData.ENgetcount(EN.NODECOUNT)
            for i in range(1, nNodes + 1):
                subdatos = [self.__enData.ENgetnodeid(i),
                            self.__enData.ENgetnodevalue(i, EN.PRESSURE),
                            self.__enData.ENgetnodevalue(i, EN.BASEDEMAND),
                            self.__enData.ENgetnodevalue(i, EN.HEAD)]
                elements.append(subdatos)
            
            print("Escribiendo los datos en fichero .csv")
            date = self.datetime.replace(":", "")
            working_directory = INP_Utils.default_working_directory()
            date_folder_path = os.path.join(working_directory, "Analysis", date)
            date_folder_path = INP_Utils.generate_directory(date_folder_path)
            nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")
            
            with open(nodes_filepath, 'w', newline='') as csvfile:
                 writer_csv = csv.writer(csvfile)
                 [writer_csv.writerow(fila) for fila in elements]
            print("Fin de la escritura de información de los nodes")
            
        elif self.__analysisElemntType == AnalysisEmentType.PIPE:
            print("Ingresando elementos de tipo tubería...")
        else:
            print("Problema con el tipo de datos.")


    def addCSVNonSpatialLayerToPanel(self, fileName, layerName):
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if not shapeGroup:
            shapeGroup = root.addGroup("Analysis")

        date = self.datetime.replace(":", "")
        project_path = INP_Utils.default_working_directory()
        date_folder_path = os.path.join(project_path, "Analysis", date)
        print("000001: ", date_folder_path)
        self.loadCSVLayer(os.path.join(date_folder_path, fileName), layerName, shapeGroup)