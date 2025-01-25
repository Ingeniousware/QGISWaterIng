# -*- coding: utf-8 -*-

"""
***************************************************************************
    analysisEmentType.py
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


import enum


class AnalysisEmentType(enum.IntEnum):
    """Clase que representa los tipos de elementos a analizar."""
    NODE = 1
    """Análisis de los nodos"""
    PIPE = 2
    """Análisis de las tuberias."""