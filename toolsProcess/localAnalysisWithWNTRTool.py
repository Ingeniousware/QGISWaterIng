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

class LocalAnalysisWithWNTRTool:
    def __init__(self, iface):
        self.iface = iface


    def ExecuteAction(self):
        if WateringUtils.isScenarioNotOpened():
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5
            )
        else:
            print("0001: Run simulation")
            """Se obtienen los resultados de la simulación local"""
            self.removerAnalysis()
            # Se configura el archivo del inp. aqui se debe guardar las opciones del inp si no existen.
            
            inpFile = INPManager()
            inpFile.writeSections()
            
            # options: INPOptions = INPOptions(None)
            # options.load()
            # self.writeSections()

            wn = wntr.network.WaterNetworkModel(inpFile.OutFile)

            inpFileTemp = os.path.dirname(inpFile.OutFile) + "\\temp"

            # Simulate hydraulics
            sim = wntr.sim.EpanetSimulator(wn)
            # sim = wntr.sim.WNTRSimulator(wn)
            self._results = sim.run_sim(inpFileTemp)

            nodeResult_at_0hr = self._results.node[NodeResultType.pressure.name].loc[0 * 3600, :]
            linkResult_at_0hr = self._results.link[LinkResultType.flowrate.name].loc[0 * 3600, :]
            # pressure_at_5hr = results.node[NodeResultType.pressure.name].loc[0*3600, :]
            # print(pressure_at_5hr)
            self._guid = str(uuid.uuid4())
            units = inpFile.options[INP_Options.Hydraulics].inpfile_units
            NodeNetworkAnalysisLocal(nodeResult_at_0hr, self._guid, "00:00")
            PipeNetworkAnalysisLocal(linkResult_at_0hr, self._guid, "00:00", LinkResultType.flowrate, units)


    def removerAnalysis(self):
         # Seeliminan los layes que se crearon para motrar los resultados
        root = QgsProject.instance().layerTreeRoot()
        shapeGroup = root.findGroup("Analysis")
        if shapeGroup:
            layer_ids = [layer.layerId() for layer in shapeGroup.findLayers()]
            root.removeChildNode(shapeGroup)
            for layer_id in layer_ids:
                QgsProject.instance().removeMapLayer(layer_id)