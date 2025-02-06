# -*- coding: utf-8 -*-

"""
***************************************************************************
    inp_utils.py
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
import os
import stat
from qgis.core import QgsProject


class INP_Utils:

    # static (class) variable that is a dictionary.
    static_elements = {}

    @classmethod
    def add_element(cls, key, value):
        cls.static_elements[key] = value

    @classmethod
    def get_element(cls, key):
        return cls.static_elements.get(key, None)

    @classmethod
    def get_all(cls):
        return cls.static_elements

    @classmethod
    def find_element(cls, key):
        if key in cls.static_elements:
            return cls.static_elements[key]
        else:
            return None


    def default_working_directory():
        home_Path = QgsProject.instance().homePath()
        #working_directory
        scenario_id = QgsProject.instance().readEntry("watering","scenario_id","default text")[0]
        working_directory = home_Path + "/" + scenario_id + "/epanet2_2"

        if not os.path.exists(working_directory):
            os.makedirs(working_directory, exist_ok=True)
            os.chmod(working_directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
        else:
           os.chmod(working_directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

        working_directory = working_directory.replace('/','\\')

        return working_directory


    def generate_directory(directoryName: str):
        if directoryName != "":
            if not os.path.exists(directoryName):
                os.makedirs(directoryName, exist_ok=True)
                os.chmod(directoryName, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
            else:
                os.chmod(directoryName, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

        newDirectory = directoryName.replace('/','\\')
        
        return newDirectory



class NodeLinkResultType(enum.IntEnum):
    """
    - Node parameters: :attr:`demand`, :attr:`head`, :attr:`pressure`, :attr:`quality`
    - Link parameters: :attr:`flowrate`, :attr:`velocity`, :attr:`headloss`, :attr:`status`, :attr:`setting`, :attr:`friction_factor`, :attr:`reaction_rate`
    """
    # Node parameters
    demand = 1
    head = 2
    pressure = 3
    quality = 4
    """Este parámetros es el mismo para los nodos y las tuberías (node, link)."""

    # Link parameters
    flowrate = 5
    velocity = 6
    headloss = 7
    status = 8
    setting = 10
    friction_factor = 10
    reaction_rate = 11