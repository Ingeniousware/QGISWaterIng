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

from qgis.core import QgsProject # type: ignore


class INP_Utils:

    # static (class) variable that is a dictionary.
    static_elements = {}

    @classmethod
    def add_element(cls, key, value):
        cls.static_elements[key] = value

    @classmethod
    def get_element(cls, element):
        for key, valor in cls.static_elements.items():
            if (key == element) or (element in valor):
                return valor[0]
        return None

    @classmethod
    def get_key_element(cls, name_element):
        for key, valor in cls.static_elements.items():
            if (name_element in valor):
                return key
        return None

    @classmethod
    def get_all(cls):
        return cls.static_elements

    @classmethod
    def find_element(cls, key):
        if key in cls.static_elements:
            return cls.static_elements[key][0]
        else:
            return None

    @classmethod
    def Clear(cls):
        cls.static_elements.clear()

    def default_directory_optins():
        return INP_Utils.default_working_directory() + "\\optins.json"


    def default_working_directory():
        """Devuelve el directorio de trabajo del proyecto. De no existir se crea el directorio de trabajo."""
        home_Path = QgsProject.instance().homePath() # Obtiene el directorio de base del proyecto
        #working_directory
        scenario_id = QgsProject.instance().readEntry("watering","scenario_id","default text")[0] # Obtiene el esenario de trabajo
        working_directory = home_Path + "/" + scenario_id + "/Simulation"
        #Se comprueba si el directorio de trabajo existe. De no existir se crea el directorio de trabajo
        # if not os.path.exists(working_directory):
        #     os.makedirs(working_directory, exist_ok=True)
        #     os.chmod(working_directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
        # else:
        #    os.chmod(working_directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

        # working_directory = working_directory.replace('/','\\')
        working_directory = INP_Utils.generate_directory(working_directory)

        return working_directory


    def generate_directory(directoryName: str):
        if directoryName != "":
            if not os.path.exists(directoryName):
                os.makedirs(directoryName, exist_ok = True)
                os.chmod(directoryName, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
            else:
                os.chmod(directoryName, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

        newDirectory = directoryName.replace('/','\\')
        
        return newDirectory
    
    
    def int_to_hora(valor: int):
        """
        Convierte un número entero que representa cantidad de segundos a formato hora (HH:MM:SS)
        
        Parameters
        ----------
        valor : int
            Es un número entero que representa una hora.

        Retorna un valor str en el formato `HH:MM:SS` y una lista donde esta `horas`, `minutos` y `segundos`
        """
        horas = int(valor/3600)
        horas_int = int(horas)
        minutos = (horas - horas_int) * 60
        minutos_int = int(minutos)
        segundos = (minutos - minutos_int) * 60
        segundos_int = int(segundos)
        return f'{horas_int:02}:{minutos_int:02}:{segundos_int:02}', [horas_int, minutos_int, segundos_int]


    def hora_to_int(valor: str):
        """
        Convierte una hora (HH:MM:SS) en un entero que representa cantidad de segundos.
        
        Parameters
        ----------
        valor : str
            Es un string que representa una hora en el formato `HH:MM:SS`.
        
        Returns:
            Retorna : Un valor de horas en un entero, un valor decimal que representa una hora y una 
            lista (hora, minutos, segundos)
        """
        partes = valor.split(':')
        horas = int(partes[0])
        minutos = int(partes[1])
        segundos = int(partes[2]) if len(partes) > 2 else 0
        horas_int = (horas + minutos / 60 + segundos / 3600) * 3600
        return horas_int, horas_int / 3600, [horas, minutos, segundos]


    # def read_options(path: str):
    #     """
    #     Read the OPTIONS file and return its content.
    #     Args:
    #         path (str): The file path where the OPTIONS file is located.
    #     Returns:
    #         dict: The content of the OPTIONS file as a dictionary.
    #     Raises:
    #         IOError: If the file cannot be opened or read.
    #     """
    #     try:
    #         with open(path, 'r') as file:
    #             data = json.load(file)
    #         return data
    #     except IOError as e:
    #         print(f"Error al leer el archivo OPTIONS: {e}")
    #         return None


    # def getoption_from_JSON(path: str, inpOption: INP_Options) -> AbstractOption:
    #     data = INP_Utils.read_options(path)[inpOption.name]
    #     result = None

    #     if inpOption == INP_Options.Hydraulics:
    #         result = HydraulicOptions()
    #     elif inpOption == INP_Options.Quality:
    #         result = QualityOptions()
    #     elif inpOption == INP_Options.Reactions:
    #         result = ReactionOptions()
    #     elif inpOption == INP_Options.Times:
    #         result = TimeOptions()
    #     else:
    #         result = EnergyOptions()

    #     result.__dict__.update(data)
    #     return result