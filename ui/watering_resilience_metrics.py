# -*- coding: utf-8 -*-

"""
***************************************************************************
    watering_resilience_metrics.py
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
import os

from matplotlib import pyplot as plt
from pandas import Series
import wntr

from qgis.PyQt import uic  # type: ignore
from PyQt5.QtWidgets import QDockWidget, QLineEdit
from time import time, gmtime, strftime
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QTimer

from ..INP_Manager.inp_utils import INP_Utils
from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_resilience_metrics_dialog.ui"))


class WateringResilienceMetric(QDockWidget, FORM_CLASS):
    def __init__(self, iface):
        """Constructor."""
        super().__init__(iface.mainWindow())
        self.setupUi(self)
        
        # Configurar un QDoubleValidator
        validador = QDoubleValidator()
        validador.setBottom(0.0)  # Valor mínimo permitido (opcional)
        validador.setDecimals(3)  # Número de decimales permitidos (opcional)
        self.pressure_requiredLE.setValidator(validador)

        self.hide_progress_bar()
        self.calculatePushButton.clicked.connect(self.calculateMetric)
        self.showGraphicPushButton.clicked.connect(self.showGraphic)
        # self.set_progress(20)
        
        self.todini = None


    def initializeRepository(self):
        pass


    def hide_progress_bar(self):
        self.progressBar.setVisible(False)


    def show_progress_bar(self):
        self.progressBar.setVisible(True)
        self.start = time()


    def set_progress(self, progress_value):
        t = time() - self.start
        hms = strftime("%H:%M:%S", gmtime(t))
        self.progressBar.setValue(progress_value)
        self.progressBar.setFormat(f"{hms} - %p%")


    def timer_hide_progress_bar(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_progress_bar)
        self.timer.start(1000)
        self.progressBar.setFormat("Loading completed")


    def calculateMetric(self):
        try:
            threshold = float(self.pressure_requiredLE.text())
            
            inpFile = INP_Utils.default_directory_inp()

            self.show_progress_bar()
            wn = wntr.network.WaterNetworkModel(inpFile)
            self.set_progress(20)
            # wn.options.hydraulic.demand_model = 'PDD'

            sim = wntr.sim.EpanetSimulator(wn)
            results = sim.run_sim()
            self.set_progress(60)
            # Cálculo de la métrica de resistencia de Todini
            pressure = results.node[NodeResultType.pressure.name]
            demand = results.node[NodeResultType.demand.name]
            head = results.node[NodeResultType.head.name]
            pump_flowrate = results.link[LinkResultType.flowrate.name].loc[:, wn.pump_name_list]
            self.set_progress(80)
            self.todini = wntr.metrics.todini_index(head, pressure, demand, pump_flowrate, wn, threshold)
            self.showGraphic()
            self.set_progress(100)
            self.timer_hide_progress_bar()
        except ValueError as ve:
            print("El texto ingresado no es un número válido. ", ve)


    def showGraphic(self):
        result: Series = self.todini
        if (result is not None):
            x_values = [x1 / 3600 for x1 in result.index.tolist()]
            y_values = result.values

            # Crear la gráfica
            plt.plot(x_values, y_values, marker='o', linestyle='-')

            # Configurar el título y las etiquetas de los ejes
            plt.title("Comportamineto del índice de Todini")
            plt.xlabel("valores en hora")
            plt.ylabel("Valores de índice")

            # Mostrar la gráfica
            plt.show()