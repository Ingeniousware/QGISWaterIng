# -*- coding: utf-8 -*-

from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, Qgis, QgsPointXY, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from qgis.utils import iface
from qgis.gui import QgsVertexMarker
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHeaderView

import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'watering_selection_review_dialog.ui'))

class WateringSelectionReview(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, features, parent=None):
        """Constructor."""
        super(WateringSelectionReview, self).__init__(parent)
        self.setupUi(self)
        self.features = features
        self.initializeRepository()

    def initializeRepository(self):
        features_count = len(self.features) 

        if features_count > 0:
            matrix_table = []
            for i in range(0, 1):
                # matrix_table.append()
                matrix_table = [ [1 ,2 ,3 ],
                                 [4 ,5 ,6 ],
                                 [7 ,8 ,9 ]]
            headers = ["Node 1", "Node 2", "Distance"]         
            model = TableModel(matrix_table, headers)
            proxyModel = QSortFilterProxyModel()
            proxyModel.setSourceModel(model)
            
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.tableView.setModel(proxyModel)
            self.tableView.setSortingEnabled(True)
    
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, headers):
        super(TableModel, self).__init__()
        self._data = data
        self.headers = headers
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # Check if self._data is not empty
        if self._data:
            # The following takes the first sub-list, and returns
            # the length (only works if all rows are an equal length)
            return len(self._data[0])
        else:
            # Return 0 if self._data is empty, indicating no columns
            return 0
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)