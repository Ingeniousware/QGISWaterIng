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


class sectionAbstract():
    def __init__(self, inpM, id=0):
        from .INPManager import INPManager
        self.__id = id
        self.__name = None
        self.__values = []
        self.__inpManager: INPManager = inpM


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

    @property
    def INPManager(self):
        return self.__inpManager


    def writeSection(self, outfile):
        print("Metodo no implementado...")
