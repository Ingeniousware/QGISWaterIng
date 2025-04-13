# -*- coding: utf-8 -*-

"""
***************************************************************************
    localAnalysisWithWNTRTool.py
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

from datetime import datetime
import json
import os
import uuid
import wntr


from qgis.core import QgsProject  # type: ignore


from ..watering_utils import WateringUtils

from ..INP_Manager.INPManager import INPManager
from ..INP_Manager.inp_options_enum import INP_Options
from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType
from ..NetworkAnalysis.nodeNetworkAnalysisLocal import NodeNetworkAnalysisLocal
from ..NetworkAnalysis.pipeNetworkAnalysisLocal import PipeNetworkAnalysisLocal
from ..INP_Manager.inp_utils import INP_Utils
from ..INP_Manager.dataType import Time_Options

class LocalAnalysisWithWNTRTool:
    def __init__(self, iface):
        self.iface = iface


    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        else:
            """Se obtienen los resultados de la simulación local"""
            self.removerAnalysis()
            # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.

            date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            # fecha_to_int = int(fecha_hora.strftime("%y%m%d%H%M%S"))
            # tempFile = f"S_{fecha_to_int}"
            dataTimeStr = date_time.translate(str.maketrans({":": "-", ".": "-"}))
            # tempFile = f"{fecha_hora}"


            inpManager = INPManager()
            inpManager.writeSections()

            # options: INPOptions = INPOptions(None)
            # options.load()
            # self.writeSections()

            wn = wntr.network.WaterNetworkModel(inpManager.OutFile)
            # os.path.join(inpFile.OutFile, "Simulaciones", tempFile)
            # inpFileTemp = INP_Utils.generate_directory(inpFile.OutFile + "\\Simulaciones\\" + tempFile)
            inpFileTemp = INP_Utils.generate_directory(os.path.join(os.path.dirname(inpManager.OutFile), "Analysis", dataTimeStr))
            # inpFileTemp += "\\" + tempFile
            # inpFileTemp = inpFileTemp + f"\\{dataTimeStr}"

            # Simulate hydraulics
            sim = wntr.sim.EpanetSimulator(wn)
            # sim = wntr.sim.WNTRSimulator(wn)
            self._results = sim.run_sim(inpFileTemp + f"\\{dataTimeStr}")

            node_Result = NodeResultType.pressure

            nodeResult_at_0hr = self._results.node[node_Result.name].loc[0 * 3600, :]
            linkResult_at_0hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
            # pressure_at_5hr = results.node[NodeResultType.pressure.name].loc[0*3600, :]
            # print(pressure_at_5hr)
            # self._guid = str(uuid.uuid4())
            analysis_id = str(uuid.uuid4())
            time = datetime.now()
            units = inpManager.options[INP_Options.Hydraulics].inpfile_units
            nodeAnalysis = NodeNetworkAnalysisLocal(nodeResult_at_0hr, inpFileTemp, analysis_id, date_time, node_Result)
            nodeAnalysis.Execute()

            pipeAnalysis = PipeNetworkAnalysisLocal(linkResult_at_0hr, inpFileTemp, analysis_id, date_time, units)
            pipeAnalysis.Execute()

            time: Time_Options = inpManager.options[INP_Options.Times]
            _, rtime, _ = INP_Utils.hora_to_int(time.duration)
            # print("---------------- Fin de los cáculos ------------------------")
            if (rtime > 0):
                for i in range(1, int(rtime)):
                    analysis_id = str(uuid.uuid4())
                    nodeResult_at_hr = self._results.node[node_Result.name].loc[i * 3600, :]
                    linkResult_at_hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
                    nodeAnalysis.elementAnalysisResults(nodeResult_at_hr, analysis_id)
                    pipeAnalysis.elementAnalysisResults(linkResult_at_hr, analysis_id, units)

            self.updateData(inpFileTemp, date_time)


    def removerAnalysis(self):
        # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)


    # def updateJSON(self, path: str ):
    #     """Äctualiza el archivo JSON con los resultados de la simulación"""
    #     directorios = []

    #     for directory_name in os.listdir(path):
    #         directory_path = os.path.join(path, directory_name)
    #         if os.path.isdir(directory_path):
    #             temp = directory_name.split("_")
    #             date = datetime.strptime(temp[1], "%y%m%d%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
    #             directorios.append({
    #                 "directoryName": directory_name,
    #                 "directoryDate": date,
    #                 "directoryPath": directory_path
    #             })

    #     ruta_json = os.path.join(path, "inf.json")

    #     with open(ruta_json, 'w') as archivo_json:
    #         json.dump(directorios, archivo_json, indent=4)


    def updateData(self, pathWork: str, dateTime: str):
        """
        ES - Método que actualiza los datos de las simulaciones en JSON.

        EN - Method that updates simulation data in JSON.

        Parameters
        ----------
        analysisExecutionId : str
            ES - ID del análisis ejecutado (GUID).

            EN - ID of the executed analysis (GUID).

        time_for_analysis: int
            ES - Hora del análisis.

            EN - Hour of the analysis.
        """
        file_path = os.path.dirname(os.path.normpath(pathWork))
        fileName = os.path.join(file_path, "simulations.json")
        dataTimeStr = dateTime.translate(str.maketrans({":": "-", ".": "-"}))
        directoryPath = os.path.join(os.path.dirname(fileName), dataTimeStr)

        contenido = None
        temp = {"IsLocalcalculated": True,
            "category": 1,
            "directoryName": dataTimeStr,
            "datetime": dateTime,
            "description": "",
            "directoryPath": directoryPath}

        try:
            with open(fileName, "r") as f:
                contenido = json.load(f)
            contenido.append(temp)
            with open(fileName, "w") as f:
                json.dump(contenido, f, indent=4)
        except FileNotFoundError:
            contenido = [temp]
            with open(fileName, "w") as f:
                json.dump(contenido, f, indent=4)