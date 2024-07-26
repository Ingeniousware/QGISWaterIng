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
    def __init__(self, node_node_list, node_pipe_list , parent=None):
        """Constructor."""
        super(WateringSelectionReview, self).__init__(parent)
        self.setupUi(self)
        self.node_node_list = node_node_list
        self.node_pipe_list = node_pipe_list
        self.initializeRepository()
        
    def initializeRepository(self):
        self.populateTableView(self.node_node_list, ["Node 1", "Node 2", "Distance"], self.tableViewNodeVsNode)
        self.populateTableView(self.node_pipe_list, ["Node", "Pipe", "Distance"], self.tableViewNodeVsPipe)
        self.nodeVsNodeCheckBox.stateChanged.connect(self.updateCheckboxText)


    def populateTableView(self, data_list, headers, table_view):
        features_count = len(data_list)

        if features_count > 0:
            model = TableModel(data_list, headers)
            proxy_model = QSortFilterProxyModel()
            proxy_model.setSourceModel(model)

            table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table_view.setModel(proxy_model)
            table_view.setSortingEnabled(True)
            table_view.clicked.connect(lambda index: self.on_row_clicked(index, table_view))

    def on_row_clicked(self, index, table_view):
        if index.isValid():
            row = index.row()
            table_view.selectRow(row)
            print("Index: ", index)
            print("TableView: ", table_view)
            print("Row: ", row)
            
    def updateNodeVsNodeCheckboxText(self):
        if self.nodeVsNodeCheckBox.isChecked():
            self.nodeVsNodeCheckBox.setText("Merge Node 2 into Node 1")
        else:
            self.nodeVsNodeCheckBox.setText("Merge Node 1 into Node 2")
            
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