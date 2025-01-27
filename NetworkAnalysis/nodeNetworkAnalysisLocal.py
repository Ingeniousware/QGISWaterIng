# -*- coding: utf-8 -*-

"""
***************************************************************************
    nodeNetworkAnalysisLocal.py
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
import enum
import os
import stat

from qgis.PyQt.QtGui import QColor # type: ignore
from qgis.core import QgsProject # type: ignore

from ..watering_utils import WateringUtils
from ..wntr.epanet.util import EN
from ..wntr.epanet.toolkit import ENepanet
from .abstractAnalysis import AbstractAnalysis
from .abstractAnalysisLocal import AbstractAnalysisLocal
from .analysisEmentType import AnalysisEmentType


    

# class AbstractAnalysisLocal(Abstract_Analysis):
#     """"
#     Clase base para la visualización de lo los resultado de la modelación en
#     QGIS de proyectos locales.
#     """
#     def __init__(self, enData: ENepanet, analysisExecutionId, datetime):
#         """Constructor of AbstractAnalysisLocal"""
#         super().__init__(analysisExecutionId, datetime)
#         self.__enData = enData
    
    
#     def elementAnalysisResults(self):
#         return super().elementAnalysisResults()
    
    
#     def analysis_to_csv(self, pathFile, fileName, analysisElemntType: AnalysisEmentType):
#         """Define donde se va a generar el fichero CSV de la simulación
        
#         Parametros
#         -------------
#         pathFile: str
#             Representa el directorio donde se van a crear el fichero.
#         fileName: str
#             Representa el nombre del fichero.
#         analysisElemntType: AnalysisEmentType
#             Elementos a realizar el análisis.
#         """
#         if analysisElemntType == AnalysisEmentType.NODE:
#             # Poner las cosas cuando se cumpla la condición
#             print("NODE")
#             file_csv = os.path.join(pathFile, fileName)
#             print(file_csv)
#             nNodes = self.__enData.ENgetcount(EN.NODECOUNT)
#             datos = []
#             datos.append(["keyID, pressure", "waterDemand", "waterAge"])
#             for i in range(1, nNodes + 1):
#                 subdatos = []
#                 subdatos.append(self.__enData.ENgetnodeid(i))
#                 subdatos.append(self.__enData.ENgetnodevalue(i, EN.PRESSURE))
#                                 #  self.__enData.ENgetnodevalue(i, EN.BASEDEMAND),
#                                 #  self.__enData.ENgetnodevalue(i, EN.HEAD))
#                 subdatos.append(self.__enData.ENgetnodevalue(i, EN.BASEDEMAND))
#                 subdatos.append(self.__enData.ENgetnodevalue(i, EN.HEAD))
#                 datos.append(subdatos)
            
#             with open(file_csv, 'w', newline='') as csvfile:
#                 writer_csv = csv.writer(csvfile)
#                 [writer_csv.writerow(fila) for fila in datos]
                    
#         elif analysisElemntType == AnalysisEmentType.PIPP:
#             # Pkdfldf
#             print("PIPE")
#         else:
#             print("Problema con el tipo de datos.")


class NodeNetworkAnalysisLocal(AbstractAnalysisLocal):
    """
    Clase que representa los resultdos de los nodes.
    """
    def __init__(self, enData: ENepanet, analysisExecutionId, datetime, analysisElemntType = AnalysisEmentType.NODE):
        """Constructor of NodeNetworkAnalysisLocal"""
        super().__init__(enData, analysisElemntType, analysisExecutionId, datetime)
        
        self.UrlGet = ""
        self.KeysApi = ["Name", "pressure", "waterDemand", "waterDemandCovered", "waterAge"]
        self.Attributes = ["Pressure", "Demand", "Demand C", "Age"]
        self.LayerName = "watering_demand_nodes"
        
        self.Field = f"Nodes_{datetime}_pressure"
        self.StartColor = QColor(255, 0, 0)
        self.EndColor = QColor(0, 0, 139)
        self.Size = 3
        self.join_field = "Name"
        self.fields_to_add = ["pressure", "waterDemand", "waterAge"]
        self.elementAnalysisResults()
        # print("001: before entering addCSVNonSpatialLayerToPanel in NodeNetworkAnalysisRepository")
        # self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime}")
        # self.joinLayersAttributes(f"Nodes_{datetime}", self.LayerName, self.join_field, self.fields_to_add)
        
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime.replace(':', '_')}")
        self.joinLayersAttributes(f"Nodes_{datetime.replace(':', '_')}", self.LayerName, self.join_field, self.fields_to_add)

