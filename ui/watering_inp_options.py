# -*- coding: utf-8 -*-

"""
***************************************************************************
    watering_inp_options.py
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
import json


from qgis.PyQt import uic # type: ignore
from PyQt5.QtWidgets import QMessageBox, QHeaderView, QTableWidgetItem, QComboBox
from PyQt5.QtCore import Qt
from qgis.PyQt import QtWidgets # type: ignore

from ..INP_Manager.dataType import AbstractOption
from ..INP_Manager.inp_utils import INP_Utils
from ..INP_Manager.inp_options_enum import INP_Options
from ..INP_Manager.inp_options import INPOptions

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_inp_options_dialog.ui"))


class WateringINPOptionsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, options: INPOptions,  parent=None):
        """Constructor."""
        super(WateringINPOptionsDialog, self).__init__(parent)
        self.setupUi(self)
        self._options = options
        self.obj: AbstractOption = None

        self.comboBox.addItems(self._options.keys())

        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.verticalHeader().setVisible(False) # Para ocultar la cabecra de cada fila.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_table()

        # Conectar el cambio en el ComboBox a la actualización de la tabla
        self.comboBox.currentIndexChanged.connect(self.update_table)
        self.table.cellChanged.connect(self.update_object)

        self.buttonBox.accepted.connect(self.accept_function)
        self.buttonBox.rejected.connect(self.cancel_function)


    def update_table(self):
        selected_class_name = self.comboBox.currentText()

        # Obtener las propiedades de la clase seleccionada
        self.obj = self._options.get(selected_class_name)

        # Filtrar propiedades que no comienzan con "_"
        self.public_properties = {k: v for k, v in vars(self.obj).items() if not k.startswith('_')}

        self.clear_widgets()

        self.table.setRowCount(len(self.public_properties))

        for row, (prop, value) in enumerate(self.public_properties.items()):
            # Obtener el texto predefinido para la propiedad, si existe
            display_text = self.obj._descriptions.get(prop, prop)
            item = QTableWidgetItem(display_text) # prop.replace("_", " ")
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Hacer el nombre de la propiedad no editable
            self.table.setItem(row, 0, item)

            if (prop in self.obj._properties.keys()):
                combo_box = QComboBox()
                combo_box.addItems([str(v) for v in self.obj._properties[prop]])
                combo_box.setCurrentText(str(value))
                combo_box.currentTextChanged.connect(lambda text, row = row: self.update_properties(row, text))
                self.table.setCellWidget(row, 1, combo_box)
            else:
                result = value if value is not None else ""
                self.table.setItem(row, 1, QTableWidgetItem(str(result)))


    def update_properties(self, row, value):
        display_text = self.table.item(row, 0).text()
        if self.obj._descriptions and display_text in self.obj._descriptions.values():
            prop = list(self.obj._descriptions.keys())[list(self.obj._descriptions.values()).index(display_text)]
        else:
            prop = display_text
        setattr(self.obj, prop, value)


    def update_object(self, row, column):
        if column == 1:  # Solo actualizar si se cambia la columna de valores
            display_text = self.table.item(row, 0).text()
            if self.obj._descriptions and display_text in self.obj._descriptions.values():
                prop = list(self.obj._descriptions.keys())[list(self.obj._descriptions.values()).index(display_text)]
            else:
                prop = display_text
            # prop = self.table.item(row, 0).text() # .replace(" ", "_")
            # prop = list(self.obj._properties.keys())[row - 1]
            if (prop not in self.obj._properties.keys()):  # No actualizar las propiedades con posibles valores aquí, se maneja en update_properties
                value = self.table.item(row, 1).text()
                setattr(self.obj, prop, value)


    def clear_widgets(self):
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                widget = self.table.cellWidget(row, col)
                if widget:
                    widget.setParent(None) # Desvincula el widget de la tabla
                    widget.deleteLater() # Elimina el widget de la memoria
        self.table.clearContents() # Limpia el contenido visual restante


    def accept_function(self):
        # Código para manejar la acción de aceptar
        path = INP_Utils.default_directory_optins()
        self.save(path)


    def cancel_function(self):
        # Código para manejar la acción de cancelar
        pass
        # Aquí puedes limpiar los datos, cerrar la ventana, etc.


    def serialize_public_properties(self, obj):
        """Serializa un objeto a un diccionario, excluyendo las propiedades privadas."""
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}


    def save(self, path: str, show_QMessageBox = True):
        """
        Save the properties of the classes to a JSON file.
        Args:
            path (str): The file path where the JSON file will be saved.
        Raises:
            IOError: If the file cannot be opened or written to.
        Side Effects:
            Displays a message box informing the user of the success of the operation.
        """
        # Crear un diccionario para JSON
        # data = {}
        # for key, value in self.classes.items():
        #     data[key] = self.serialize_public_properties(value)
            
        # data = {key: self.serialize_public_properties(value) for key, value in self.classes.items()}
        
        # data = {
        #     "Energy": self.serialize_public_properties(self.classes['Energy']),
        #     "Reactions": self.serialize_public_properties(self.classes['Reactions']),
        #     "Times": self.serialize_public_properties(self.classes['Times']),
        #     "Hydraulics": self.serialize_public_properties(self.classes['Hydraulics'])
        # }
        
        # Guardar las propiedades en un archivo JSON
        try:
            # with open(path, 'w') as file:
            #     json.dump(data, file, indent = 4)
            self._options.save(path)

            if show_QMessageBox:
                QMessageBox.information(self, "Éxito", "Los cambios han sido guardados exitosamente.")
        except IOError as e:
            if show_QMessageBox:
                QMessageBox.information(self, "Error", f"Error al guardar los cambios {e}.")
                raise