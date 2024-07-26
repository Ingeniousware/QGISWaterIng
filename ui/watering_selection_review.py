from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, Qgis, QgsField, QgsFeatureRequest
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from qgis.utils import iface
from PyQt5.QtWidgets import QHeaderView

import os
from ..watering_utils import WateringUtils

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
        self.populateTableView(self.node_node_list, ["Node 1", "Node 2", "Distance", "Node1_fID", "Node2_fID"], self.tableViewNodeVsNode)
        self.populateTableView(self.node_pipe_list, ["Node", "Pipe", "Distance", "Node_fID", "Pipe_fID"], self.tableViewNodeVsPipe)
        self.nodeVsNodeCheckBox.stateChanged.connect(self.updateCheckboxText)
        self.nodeVsPipeCheckBox.stateChanged.connect(self.updateCheckboxText)
        self.NodeXNodeBtn.clicked.connect(self.onNodeXNodeBtnClicked)

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

            table_view.setColumnHidden(len(headers) - 2, True)  # Hide Node1_fID
            table_view.setColumnHidden(len(headers) - 1, True)  # Hide Node2_fID
   
    def onNodeXNodeBtnClicked(self):
        selected_row = self.tableViewNodeVsNode.selectionModel().currentIndex().row()
        if selected_row != -1:
            node1_fID = int(self.tableViewNodeVsNode.model().data(self.tableViewNodeVsNode.model().index(selected_row, 3)))
            node2_fID = int(self.tableViewNodeVsNode.model().data(self.tableViewNodeVsNode.model().index(selected_row, 4)))
            if self.nodeVsNodeCheckBox.isChecked():
                self.mergeNodes(node1_fID, node2_fID, True)
            else:
                self.mergeNodes(node1_fID, node2_fID, False)
        else:
            WateringUtils.error_message("No selection. Please select a row in the table.")

    def mergeNodes(self, node1_fID, node2_fID, merge_node2_into_node1):
        layer = QgsProject.instance().mapLayersByName('watering_demand_nodes')[0]
        node1 = next(layer.getFeatures(QgsFeatureRequest(node1_fID)))
        node2 = next(layer.getFeatures(QgsFeatureRequest(node2_fID)))
        
        if node1 and node2:
            if merge_node2_into_node1:
                target_node, source_node = node1, node2
            else:
                target_node, source_node = node2, node1
            
            #target_node.setGeometry(target_node.geometry().combine(source_node.geometry()))
            
            layer.startEditing()
            layer.updateFeature(target_node)
            layer.deleteFeature(source_node.id()) #TODO - create Watering Utils delete feature
            layer.commitChanges()
            
            WateringUtils.success_message("Nodes merged successfully")
        else:
            WateringUtils.error_message("One or both nodes not found")

    def on_row_clicked(self, index, table_view):
        if index.isValid():
            row = index.row()
            table_view.selectRow(row)
            visible_columns = table_view.model().columnCount()
            hidden_columns_start = visible_columns - 2 # 2 == hidden columns (fID_1 and fID_2)

            print("Index: ", index)
            print("TableView: ", table_view)
            print("Row: ", row)
            
            visible_data = [table_view.model().data(table_view.model().index(row, col)) for col in range(visible_columns - 2)]
            print("Visible Data: ", visible_data)
            
            hidden_data = [table_view.model().data(table_view.model().index(row, col)) for col in range(hidden_columns_start, visible_columns)]
            print("Hidden Data: ", hidden_data)
            
    def updateCheckboxText(self):
        sender = self.sender()
        if sender == self.nodeVsNodeCheckBox:
            if self.nodeVsNodeCheckBox.isChecked():
                self.nodeVsNodeCheckBox.setText("Merge Node 2 into Node 1")
            else:
                self.nodeVsNodeCheckBox.setText("Merge Node 1 into Node 2")
        elif sender == self.nodeVsPipeCheckBox:
            if self.nodeVsPipeCheckBox.isChecked():
                self.nodeVsPipeCheckBox.setText("Connect Node to Pipe")
            else:
                self.nodeVsPipeCheckBox.setText("Connect Pipe to Node")
            
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