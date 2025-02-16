# -*- coding: utf-8 -*-

"""
***************************************************************************
    inp_options.py
    ---------------------
    Date                 : Febrero 2025
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


class INP_Options(enum.IntEnum):
    Hydraulics = 0
    Quality = 1
    Reactions = 2
    Times = 3
    Energy = 4