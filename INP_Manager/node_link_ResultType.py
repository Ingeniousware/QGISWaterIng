# -*- coding: utf-8 -*-

"""
***************************************************************************
    node_link_ResultType.py
    ---------------------
    Date                 : Febrero 2024
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


import enum


class NodeResultType(enum.IntEnum):
    """
    - Node parameters: :attr:`demand`, :attr:`head`, :attr:`pressure`, :attr:`quality`
    """
    # Node parameters
    demand = 1
    head = 2
    pressure = 3
    quality = 4


class LinkResultType(enum.IntEnum):
    """
    - Link parameters: :attr:`flowrate`, :attr:`velocity`, :attr:`headloss`, :attr:`status`, :attr:`setting`, :attr:`friction_factor`, :attr:`reaction_rate`
    """

    # Link parameters
    flowrate = 1
    velocity = 2
    headloss = 3
    status = 4
    setting = 5
    friction_factor = 6
    reaction_rate = 7