from qgis.PyQt import uic, QtWidgets
from qgis.core import QgsProject, Qgis, QgsGeometry, QgsFeatureRequest, QgsWkbTypes, QgsPoint, QgsPointXY
from qgis.core import QgsFeature, QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from qgis.utils import iface
from PyQt5.QtWidgets import QHeaderView
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsRuleBasedRenderer, QgsSymbol, QgsFillSymbol


import os
from ..watering_utils import WateringUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "watering_selection_review_dialog.ui"))


class WateringSelectionReview(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, node_node_list, node_pipe_list, parent=None):
        """Constructor."""
        super(WateringSelectionReview, self).__init__(parent)
        self.setupUi(self)
        self.node_node_list = node_node_list
        self.node_pipe_list = node_pipe_list
        self.initializeRepository()

    def initializeRepository(self):
        self.populateTableView(
            self.node_node_list, ["Node 1", "Node 2", "Distance", "Node1_fID", "Node2_fID"], self.tableViewNodeVsNode
        )
        self.populateTableView(
            self.node_pipe_list, ["Node", "Pipe", "Distance", "Node_fID", "Pipe_fID"], self.tableViewNodeVsPipe
        )
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
        if self.tableViewNodeVsNode.model().rowCount() == 0:
            WateringUtils.error_message("The table is empty. Please add nodes to the table first.")
            return

        selected_row = self.tableViewNodeVsNode.selectionModel().currentIndex().row()
        if selected_row != -1:
            node1_fID = int(
                self.tableViewNodeVsNode.model().data(self.tableViewNodeVsNode.model().index(selected_row, 3))
            )
            node2_fID = int(
                self.tableViewNodeVsNode.model().data(self.tableViewNodeVsNode.model().index(selected_row, 4))
            )
            if self.nodeVsNodeCheckBox.isChecked():
                self.mergeNodes(node1_fID, node2_fID, True)
            else:
                self.mergeNodes(node1_fID, node2_fID, False)
        else:
            WateringUtils.error_message("No selection. Please select a row in the table.")

    def mergeNodes(self, node1_fID, node2_fID, merge_node2_into_node1):
        node_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]
        pipe_layer = QgsProject.instance().mapLayersByName("watering_pipes")[0]

        node1 = next(node_layer.getFeatures(QgsFeatureRequest(node1_fID)), None)
        node2 = next(node_layer.getFeatures(QgsFeatureRequest(node2_fID)), None)

        if not node1 or not node2:
            WateringUtils.error_message("One or both nodes not found")
            return

        target_node, source_node = (node1, node2) if merge_node2_into_node1 else (node2, node1)

        node_layer.startEditing()

        target_node_geom = target_node.geometry().asPoint()

        source_node_geom = source_node.geometry().asPoint()

        pipe_layer.startEditing()

        matching_pipe, matching_vertex = self.find_vertex_within_tolerance(source_node_geom, pipe_layer, 0.01)

        if matching_pipe and matching_vertex:
            geom = matching_pipe.geometry()
            new_polyline = []
            for polyline in geom.asMultiPolyline():
                new_polyline.append(
                    [
                        QgsPointXY(target_node_geom) if QgsPointXY(vertex) == matching_vertex else vertex
                        for vertex in polyline
                    ]
                )
            matching_pipe.setGeometry(QgsGeometry.fromMultiPolylineXY(new_polyline))

            pipe_layer.updateFeature(matching_pipe)

        node_layer.deleteFeature(source_node.id())  # TODO : delete Pipe if length goes to 0 after merging

        node_layer.commitChanges()

        pipe_layer.commitChanges()

        WateringUtils.success_message("Nodes and pipes updated and merged successfully")

    def find_vertex_within_tolerance(self, point, polyline_layer, tolerance):
        for feature in polyline_layer.getFeatures():
            geom = feature.geometry()

            for polyline in geom.asMultiPolyline():
                for vertex in polyline:
                    vertex_point = QgsPointXY(vertex)
                    if point.distance(vertex_point) <= tolerance:
                        return feature, vertex_point

        return None, None

    def on_row_clicked(self, index, table_view):
        if index.isValid():
            row = index.row()
            table_view.selectRow(row)
            visible_columns = table_view.model().columnCount()
            hidden_columns_start = visible_columns - 2  # 2 == hidden columns (fID_1 and fID_2)

            hidden_data = [
                table_view.model().data(table_view.model().index(row, col))
                for col in range(hidden_columns_start, visible_columns)
            ]
            print("Hidden Data: ", hidden_data)

            node1_fID = int(hidden_data[0])
            node2_fID = int(hidden_data[1])

            self.highlight_features([node1_fID, node2_fID])

    def highlight_features(self, feature_ids):
        node_layer = QgsProject.instance().mapLayersByName("watering_demand_nodes")[0]

        node_layer.removeSelection()
        node_layer.selectByIds(feature_ids)

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
