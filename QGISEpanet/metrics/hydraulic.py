# -*- coding: utf-8 -*-

"""
***************************************************************************
    hydraulic.py
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


import logging

import numpy as np
import pandas as pd
from ..epanet import EpanetSimulator

logger = logging.getLogger(__name__)

def todini_index(head, pressure, demand, flowrate, es: EpanetSimulator, Pstar):
    """
    Compute Todini index, equations from :cite:p:`todi00`.

    The Todini index is related to the capability of a system to overcome
    failures while still meeting demands and pressures at the nodes. The
    Todini index defines resilience at a specific time as a measure of surplus
    power at each node and measures relative energy redundancy.

    Parameters
    ----------
    head : pandas DataFrame
        A pandas DataFrame containing node head
        (index = times, columns = node names).

    pressure : pandas DataFrame
        A pandas DataFrame containing node pressure
        (index = times, columns = node names).

    demand : pandas DataFrame
        A pandas DataFrame containing node demand
        (index = times, columns = node names).

    flowrate : pandas DataFrame
        A pandas DataFrame containing pump flowrates
        (index = times, columns = pump names).

    es : EpanetSimulator
        Water network model.  The water network model is needed to
        find the start and end node to each pump.

    Pstar : float
        Pressure threshold.

    Returns
    -------
    A pandas Series that contains a time-series of Todini indexes
    """

    # 1. Validación de inputs
    if not all(df.index.equals(head.index) for df in [pressure, demand, flowrate]):
        raise ValueError("Todos los DataFrames deben tener el mismo índice de tiempo")

    # Obtener IDs de componentes
    junctions = es.getNodeJunctionNameID()
    reservoirs = es.getNodeReservoirNameID()

    # 2. Cálculo de energía disponible en nodos (Pout)
    # Pout = Qdemanda * Htotal en cada nodo
    Pout = demand[junctions] * head[junctions]

    # 3. Cálculo de energía mínima requerida (Pexp)
    # Pexp = Qdemanda * (Pstar + Zelevación)
    elevation = head[junctions] - pressure[junctions]
    Pexp = demand[junctions] * (Pstar + elevation)

    # 4. Cálculo de energía aportada por reservorios (Pin_res)
    # Pin_res = -Qentrante * Hreservorio
    Pin_res = -demand[reservoirs] * head[reservoirs]

    # 5. Cálculo de energía aportada por bombas (pump_energy)
    # pump_energy = Qbomba * ΔH (diferencia de altura que aporta la bomba)
    pump_energy = pd.DataFrame(index=flowrate.index)
    pumps = es.getLinkPumpNodesNameID()

    for item in pumps:
        for pump_index, node_name_id in item.items():
            start_node = node_name_id[0]
            end_node = node_name_id[1]

            # ΔH = Hsalida - Hentrada (debe ser positivo para bombas funcionando correctamente)
            delta_head = head[end_node] - head[start_node]

            # Energía = Q * ΔH (solo consideramos valores positivos)
            pump_energy[pump_index] = flowrate[pump_index] * delta_head.clip(lower=0)

    # 6. Cálculo final del Índice de Todini
    numerator = Pout.sum(axis=1) - Pexp.sum(axis=1)
    denominator = Pin_res.sum(axis=1) + pump_energy.sum(axis=1) - Pexp.sum(axis=1)

    todini_index = numerator / denominator

    # Manejo de casos especiales (división por cero)
    todini_index = todini_index.replace([np.inf, -np.inf], np.nan)

    return todini_index