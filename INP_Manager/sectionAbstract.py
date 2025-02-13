# -*- coding: utf-8 -*-

"""
***************************************************************************
    sectionAbstract.py
    ---------------------
    Date                 : Noviembre 2024
    Copyright            : (C) 2024 by Ingeniowarest
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
from .inp_utils import INP_Utils
from ..ui.watering_inp_options import WateringINPOptions


class sectionAbstract():
    def __init__(self, id=0):
        self.__id = id
        self.__name = None
        self.__values = []


    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def values(self):
        return self.__values

    @values.setter
    def values(self, value):
        self.__values = value


    def writeSection(self, outfile):
        print("Metodo no implementado...")
    
    
    def getPath(self) -> str:
        path = INP_Utils.default_directory_optins()
        if not os.path.exists(path):
            options = WateringINPOptions()
            options.save(path, False)
        return path
