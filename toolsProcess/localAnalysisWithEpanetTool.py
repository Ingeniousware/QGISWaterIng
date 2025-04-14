# -*- coding: utf-8 -*-

"""
***************************************************************************
    localAnalysisWithEpanetTool.py
    ---------------------
    Date                 : Abril 2025
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

import datetime
import os
import shutil
import uuid

from ..INP_Manager.dataType import Time_Options
from ..INP_Manager.inp_options_enum import INP_Options
from ..NetworkAnalysis.nodeNetworkAnalysisLocal import NodeNetworkAnalysisLocal
from ..NetworkAnalysis.pipeNetworkAnalysisLocal import PipeNetworkAnalysisLocal
from ..watering_utils import WateringUtils
from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType
from ..INP_Manager.inp_utils import INP_Utils
from ..QGISEpanet.epanet import EpanetSimulator
from ..INP_Manager.INPManager import INPManager
from .abstractAnalysisTool import AbstractAnalysisTool


class LocalAnalysisWithEpanetTool(AbstractAnalysisTool):
    def __init__(self, iface):
        """
        ES - Esta herramienta realiza la simulación de la red hidráulica por el método del toolkit de Epant 2.2.
        
        EN - This tool performs the simulation of the hydraulic network by the method of the Epant 2.2 toolkit.
        """
        super().__init__(iface)
        self.NameMethod = "Epanet 2.2"


    def ExecuteAction(self):
        # return super().ExecuteAction()
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5)
        else:
            """Se obtienen los resultados de la simulación local con el Toolkit de Epanet 2.2"""
            self.removerAnalysis()
            # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.

            date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            # fecha_to_int = int(fecha_hora.strftime("%y%m%d%H%M%S"))
            # tempFile = f"S_{fecha_to_int}"
            dataTimeStr = date_time.translate(str.maketrans({":": "-", ".": "-"}))
            # tempFile = f"{fecha_hora}"

            inpManager = INPManager()
            inpManager.writeSections()

            inpFileTemp = INP_Utils.generate_directory(os.path.join(os.path.dirname(inpManager.OutFile), "Analysis", dataTimeStr))
            inp_for_sim = inpFileTemp + f"\\{dataTimeStr}"

            try:
                shutil.copy(inpManager.OutFile, inp_for_sim)
            except FileNotFoundError:
                print("El archivo de origen no existe.")
            except PermissionError:
                print("No tienes permisos suficientes para copiar el archivo.")

            ep_sim = EpanetSimulator()
            results = ep_sim.run_sim(inpManager.OutFile)

            node_result = NodeResultType.pressure
            link_result = LinkResultType.flowrate

            nodeResult_at_0hr = results.node[node_result.name].loc[0 * 3600, :]
            linkResult_at_0hr = results.link[link_result.name].loc[0 * 3600, :]

            analysis_id = str(uuid.uuid4())
            time = datetime.now()
            units = inpManager.options[INP_Options.Hydraulics].inpfile_units
            nodeAnalysis = NodeNetworkAnalysisLocal(nodeResult_at_0hr, inpFileTemp, analysis_id, date_time, node_result)
            nodeAnalysis.Execute()

            pipeAnalysis = PipeNetworkAnalysisLocal(linkResult_at_0hr, inpFileTemp, analysis_id, date_time, units, link_result)
            pipeAnalysis.Execute()

            time: Time_Options = inpManager.options[INP_Options.Times]
            _, rtime, _ = INP_Utils.hora_to_int(time.duration)
            # print("---------------- Fin de los cáculos ------------------------")
            if (rtime > 0):
                for i in range(1, int(rtime)):
                    analysis_id = str(uuid.uuid4())
                    nodeResult_at_hr = self._results.node[node_result.name].loc[i * 3600, :]
                    linkResult_at_hr = self._results.link[link_result.name].loc[0 * 3600, :]
                    nodeAnalysis.elementAnalysisResults(nodeResult_at_hr, analysis_id)
                    pipeAnalysis.elementAnalysisResults(linkResult_at_hr, analysis_id, units)

            self.updateData(inpFileTemp, date_time)