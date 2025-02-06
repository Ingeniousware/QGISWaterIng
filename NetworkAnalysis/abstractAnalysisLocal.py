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
import wntr
from wntr.sim.results import SimulationResults
from qgis.core import QgsProject # type: ignore

# from ..wntr.epanet.util import EN
from ..INP_Manager.inp_utils import INP_Utils, NodeLinkResultType
from .analysisEmentType import AnalysisEmentType
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
    def __init__(self, results: SimulationResults, analysisElemntType: AnalysisEmentType, resultType: NodeLinkResultType, analysisExecutionId, datetime):
        super().__init__(analysisExecutionId, datetime)
        self.__results = results
        self.__analysisElemntType = analysisElemntType
        self.__resultType = resultType


    # def elementAnalysisResults(self):
    #     print("Ingresando elementos...")
    #     filename = self.analysisExecutionId
    #     # elements = []
    #     # subelement = []
    #     # for item in self.fields_to_add:
    #     #     subelement.append(item.name)
    #     # elements.append(subelement)
    #     # elements = [[item.name for item in self.fields_to_add]]
    #     elements = []
    #     date = self.datetime.replace(":", "")
    #     working_directory = INP_Utils.default_working_directory()
    #     date_folder_path = os.path.join(working_directory, "Analysis", date)
    #     date_folder_path = INP_Utils.generate_directory(date_folder_path)

    #     if self.__analysisElemntType == AnalysisEmentType.NODE:
    #         elements.append(["Name", "pressure", "waterDemand", "waterAge"])
    #         nNodes = self.__enData.ENgetcount(EN.NODECOUNT)
    #         for i in range(1, nNodes + 1):
    #             subdatos = [self.__enData.ENgetnodeid(i),
    #                         self.__enData.ENgetnodevalue(i, EN.PRESSURE),
    #                         self.__enData.ENgetnodevalue(i, EN.BASEDEMAND),
    #                         self.__enData.ENgetnodevalue(i, EN.HEAD)]
    #             elements.append(subdatos)

    #         nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")

    #         with open(nodes_filepath, 'w', newline='') as csvfile:
    #              writer_csv = csv.writer(csvfile)
    #              [writer_csv.writerow(fila) for fila in elements]

    #     elif self.__analysisElemntType == AnalysisEmentType.PIPE:
    #         elements.append(["Name", "velocity", "flow", "headLoss"])
    #         nLinks = self.__enData.ENgetcount(EN.LINKCOUNT)
    #         for i in range(1, nLinks + 1):
    #             subdatos = [self.__enData.ENgetlinkid(i),
    #                         self.__enData.ENgetlinkvalue(i, EN.VELOCITY),
    #                         self.__enData.ENgetlinkvalue(i, EN.FLOW),
    #                         self.__enData.ENgetlinkvalue(i, EN.HEADLOSS)]
    #             elements.append(subdatos)

    #         nodes_filepath = os.path.join(date_folder_path, f"{filename}_Pipes.csv")

    #         with open(nodes_filepath, 'w', newline='') as csvfile:
    #              writer_csv = csv.writer(csvfile)
    #              [writer_csv.writerow(fila) for fila in elements]

    #     else:
    #         print("Problema con el tipo de datos.")
    def elementAnalysisResults(self):
        filename = self.analysisExecutionId

        elements = []
        date = self.datetime.replace(":", "")
        working_directory = INP_Utils.default_working_directory()
        date_folder_path = os.path.join(working_directory, "Analysis", date)
        date_folder_path = INP_Utils.generate_directory(date_folder_path)

        if self.__analysisElemntType == AnalysisEmentType.NODE:
            elements.append(["Name", self.__resultType.name])
                            #  NodeLinkResultType.demand.name,
                            #  NodeLinkResultType.head.name,
                            #  NodeLinkResultType.pressure.name,
                            #  NodeLinkResultType.quality.name])
            range_1 = len(self.__results.node[self.__resultType.name].columns)

            resultValue = self.__results.node[self.__resultType.name].values.tolist()
            
            # headValue = self.__results.node[NodeLinkResultType.head.name].values.tolist()
            # pressureValue = self.__results.node[NodeLinkResultType.pressure.name].values.tolist()
            # qualityValue = self.__results.node[NodeLinkResultType.quality.name].values.tolist()

            name = self.__results.node[self.__resultType.name].columns.tolist()

            for i in range(range_1):
                subdatos = [name[i], resultValue[0][i]]
                            # demandValue[0][i],
                            # headValue[0][i],
                            # pressureValue[0][i],
                            # qualityValue[0][i]]
                elements.append(subdatos)

            nodes_filepath = os.path.join(date_folder_path, f"{filename}_Nodes.csv")

            with open(nodes_filepath, 'w', newline='') as csvfile:
                 writer_csv = csv.writer(csvfile)
                 [writer_csv.writerow(fila) for fila in elements]

        elif self.__analysisElemntType == AnalysisEmentType.PIPE:
            elements.append(["Name", self.__resultType.name])
            range_1 = len(self.__results.link[self.__resultType.name].columns)

            resultValue = self.__results.link[self.__resultType.name].values.tolist()

            name = self.__results.link[self.__resultType.name].columns.tolist()

            for i in range(range_1):
                subdatos = [name[i], resultValue[0][i]]

                elements.append(subdatos)

            pipes_filepath = os.path.join(date_folder_path, f"{filename}_Pipes.csv")

            with open(pipes_filepath, 'w', newline='') as csvfile:
                writer_csv = csv.writer(csvfile)
                [writer_csv.writerow(fila) for fila in elements]

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

        self.loadCSVLayer(os.path.join(date_folder_path, fileName), layerName, shapeGroup)