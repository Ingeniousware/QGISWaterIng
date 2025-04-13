# -*- coding: utf-8 -*-

"""
***************************************************************************
    AbstractAnalysisTool.py
    ---------------------
    Date                 : Abril 2025
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

from abc import ABC, abstractmethod


class AbstractAnalysisTool(ABC):
    def __init__(self, iface):
        self.iface = iface
        self.__nameMethod = "Analysis"


    @property
    def NameMethod(self):
        return self.__nameMethod
    @NameMethod.setter
    def NameMethod(self, value):
        self.__nameMethod = value


    @abstractmethod
    def ExecuteAction(self):
        """
        Método que implemte la lógica de los métodos para realizar la simulación a la rede hidruálica.

        .. nota::

            Se debe implementar una condicón para cuando se ejecute este método como se muestra a continuación.
            
        if WateringUtils.isScenarioNotOpened():
        
            self.iface.messageBar().pushMessage(
                self.tr("Error"), self.tr("Load a project scenario first in Download Elements!"), level=1, duration=5)

        else:
            
            # Aquí se implemeta la logica del método de simulación
            pass
        """
        pass