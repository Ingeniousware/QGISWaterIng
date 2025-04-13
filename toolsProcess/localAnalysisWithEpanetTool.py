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

from watering_utils import WateringUtils

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
            
            ep_sim = EpanetSimulator()
            results = ep_sim.run_sim(inpManager.OutFile)
            inpFileTemp = INP_Utils.generate_directory(os.path.join(os.path.dirname(inpManager.OutFile), "Analysis", dataTimeStr))