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
from ..epanet import EpanetSimulator

logger = logging.getLogger(__name__)

def todini_index(head, pressure, demand, flow, headloss, es: EpanetSimulator, Pstar):
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

    wn : wntr WaterNetworkModel
        Water network model.  The water network model is needed to
        find the start and end node to each pump.

    Pstar : float
        Pressure threshold.

    Returns
    -------
    A pandas Series that contains a time-series of Todini indexes
    """
    # Obtener IDs de componentes
    junctions = es.getNodeJunctionNameID()
    reservoirs = es.getNodeReservoirNameID()
    pumps = es.getLinkPumpNameID()

    # Cálculos vectorizados
    elevation = head[junctions] - pressure[junctions]
    Pout = demand[junctions] * head[junctions]
    Pexp = demand[junctions] * (Pstar + elevation)

    # Energía de reservorios (fuente)
    Pin_res = -demand[reservoirs] * head[reservoirs]

    # Energía de bombas
    Pin_pump = flow[pumps] * headloss[pumps].abs()

    # Cálculo final del índice
    numerator = Pout.sum(axis=1) - Pexp.sum(axis=1)
    denominator = Pin_res.sum(axis=1) + Pin_pump.sum(axis=1) - Pexp.sum(axis=1)

    return numerator / denominator