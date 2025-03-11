# -*- coding: utf-8 -*-

"""
***************************************************************************
    watering_simulation_manager.py
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


from abc import ABC, abstractmethod
import os

from qgis.PyQt import uic # type: ignore
from qgis.PyQt import QtWidgets # type: ignore
from PyQt5.QtWidgets import QMessageBox, QHeaderView, QAbstractItemView, QTableWidgetItem, QComboBox, QLabel, QDialog, QLineEdit, QFormLayout, QPushButton
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QIntValidator

from ..INP_Manager.node_link_ResultType import LinkResultType, NodeResultType


class Event:
    def __init__(self):
        self.__event = None


    def subscribe(self, func):
        self.__event = func


    # def unsubscribe(self, func):
    #     self.__subscribers.remove(func)

    def notify(self, time, nodeResultType: NodeResultType = NodeResultType.pressure, linkResultType: LinkResultType = LinkResultType.flowrate):
        if self.__event is not None:
            self.__event(time, nodeResultType, linkResultType)

class EventBase(ABC):
    def __init__(self):
        self.__event = None
    def connect(self, func):
        self.__event = func
    @abstractmethod
    def notify(self, *value):
        self.__event(*value)

class Event_1(EventBase):
    def __init__(self):
        super().__init__()
    def notify(self, *value, **v1):
        super().notify(*value, **v1)
        # self.__event(value, v1)

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_simulation_manager_dialog.ui"))


class WateringSimulationManagerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, maxTime, listElement = None, parent = None):
        """Constructor."""
        super(WateringSimulationManagerDialog, self).__init__(parent)
        self.setupUi(self)

        self._maxTime = int(maxTime)
        self._time = 0
        self._nodeResultType = NodeResultType.pressure
        self._linkResultType = LinkResultType.flowrate
        self._listElement = listElement
        # for item in NodeResultType:
        #     self.nodeComboBox.addItem(item.name)
        
        self.nodeComboBox.addItems([item.name for item in NodeResultType])
        self.nodeComboBox.setCurrentText(self._nodeResultType.name)
        self.nodeComboBox.currentTextChanged.connect(self.nodeResultTypeChanged)

        self.linkComboBox.addItems([item.name for item in LinkResultType])
        self.linkComboBox.setCurrentText(self._linkResultType.name)
        self.linkComboBox.currentTextChanged.connect(self.linkResultTypeChanged)

        self.previousButton.clicked.connect(self.__previousClick)
        self.nextButton.clicked.connect(self.__nextClick)

        self.timeLabel.setCursor(Qt.PointingHandCursor)
        self.timeLabel.mousePressEvent = self.label_clicked

        self.timeChanged = Event()
        
        self.textEdit.textChanged.connect(self.filter_list)
        
        self.model = QStringListModel(self._listElement)
        self.listView.setModel(self.model)
        self.listView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Deshabilitar la edición
        self.listView.doubleClicked.connect(self.on_item_double_clicked)  # Conectar doble clic a la función
        
        self.elementDoubleClicked = Event()


    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = max(0, min(value, self._maxTime))
        self.timeChanged.notify(self._time, self._nodeResultType, self._linkResultType)
        self.timeLabel.setText(str(self._time))


    def nodeResultTypeChanged(self):
        self._nodeResultType = NodeResultType[self.nodeComboBox.currentText()]


    def linkResultTypeChanged(self):
        self._linkResultType = LinkResultType[self.linkComboBox.currentText()]


    def __previousClick(self):
        self.time -= 1
        if (self.time < 0):
            self.time = 0


    def __nextClick(self):
        self.time += 1
        if (self.time > self._maxTime):
            self.time = self._maxTime


    def label_clicked(self, event):
        dialog = InputDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.time = dialog.value # max(0, min(dialog.value, self._maxTime))
            # if (dialog.value < 0):
            #     self.time = 0
            # elif (dialog.value > self._maxTime):
            #     self.time = self._maxTime
            # else:
            #     self.time = dialog.value


    def filter_list(self):
        filter_text = self.textEdit.toPlainText()
        all_items = self._listElement
        filtered_items = [item for item in all_items if filter_text.lower() in item.lower()]
        self.model.setStringList(filtered_items)


    def on_item_double_clicked(self, index):
        item_text = self.model.data(index, Qt.DisplayRole)
        self.elementDoubleClicked.notify(item_text, self._nodeResultType, self._linkResultType)


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Go to time')
        self.layout = QFormLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Enter the time')
        self.name_input.setValidator(QIntValidator(0, 10000, self)) # Agregar validador para permitir solo números enteros

        self.layout.addRow('Time: ', self.name_input)
        self.submit_button = QPushButton('Enviar')
        self.submit_button.clicked.connect(self.submit_data)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)


    def submit_data(self):
        self.value = int(self.name_input.text())
        self.accept()