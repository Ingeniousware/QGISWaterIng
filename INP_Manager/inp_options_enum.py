# -*- coding: utf-8 -*-

"""
***************************************************************************
    inp_options_enum.py
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
    Hydraulics = 1
    Quality = 2
    Reactions = 3
    Times = 4
    Energy = 5