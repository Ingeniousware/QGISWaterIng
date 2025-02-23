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

import json
import os

from .inp_utils import INP_Utils
from .inp_options_enum import INP_Options
from .dataType import HydraulicOptions, QualityOptions, ReactionOptions, TimeOptions, EnergyOptions
# from __future__ import annotations

class INPOptions(dict):
    def __init__(self, inpM, *args, **kwargs):
        super(INPOptions, self).__init__(*args, **kwargs)
        self.__inpManager = inpM
        
        self[INP_Options.Hydraulics] = HydraulicOptions(self.__inpManager)
        self[INP_Options.Quality] = QualityOptions(self.__inpManager)
        self[INP_Options.Reactions] = ReactionOptions(self.__inpManager)
        self[INP_Options.Times] = TimeOptions(self.__inpManager)
        self[INP_Options.Energy] = EnergyOptions(self.__inpManager)


    def __setitem__(self, key: INP_Options, value):
        super().__setitem__(key.name, value)


    def __getitem__(self, key: INP_Options):
        """
        Retrieve an item from the INP_Options dictionary.

        Args:
            key (INP_Options): The key to look up in the dictionary.

        Returns:
            The value associated with the key.
        """
        result = super().__getitem__(key.name)
        return result


    def __delitem__(self, key: INP_Options):
        try:
            super().__delitem__(key.name)
        except KeyError:
            print(f"Clave {key} no encontrada")


    # def get(self, key, default=None):
    #     return super().get(key, default)


    # def update(self, *args, **kwargs):
    #     super().update(*args, **kwargs)


    # def keys(self):
    #     return super().keys()


    # def values(self):
    #     return super().values()


    # def items(self):
    #     return super().items()


    def serialize_public_properties(self):
        """Serializa un objeto a un diccionario, excluyendo las propiedades privadas."""
        result = {}
        for k, value in self.items():
            result[k] = {k: v for k, v in vars(value).items() if not k.startswith('_')}
        
        return result


    def load(self, filename: str = None):
        filename = filename or INP_Utils.default_directory_optins()

        if not os.path.exists(filename):
            self.save(filename)

        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                # Actualizar el diccionario del objeto con los datos leídos
                for key, attributes in data.items():
                    option = self[INP_Options[key]]
                    for attr, value in attributes.items():
                        setattr(option, attr, value)
        except IOError as e:
            raise e


    def save(self, filename: str = None):
        filename = filename or INP_Utils.default_directory_optins()
        # Serializar las propiedades públicas
        data = self.serialize_public_properties()
        

        # Guardar las propiedades en un archivo JSON
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent = 4)
        except IOError as e:
            raise e