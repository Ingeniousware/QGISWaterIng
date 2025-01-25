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


import os
import stat
from qgis.core import QgsProject


class INP_Utils():
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
