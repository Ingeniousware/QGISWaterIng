from .abstractAnalysisRepository import AbstractAnalysisRepository
from ..watering_utils import WateringUtils
from qgis.PyQt.QtGui import QColor # type: ignore


class NodeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self, token, analysisExecutionId, datetime, nodeProperty, behavior, field=None):
        """Constructor."""
        super().__init__(token, analysisExecutionId, datetime, behavior)
        self.UrlGet = "/api/v1/WaterAnalysisResults/nodes"
        self.KeysApi = ["nodeKey", "pressure", "waterDemand", "waterDemandCovered", "waterAge"]
        self.Attributes = ["Pressure", "Demand", "Demand C", "Age"]
        self.LayerName = "watering_demand_nodes"
        # self.Field = "Pressure"
        # self.Field = (f"Nodes_{datetime}_pressure")
        self.Field = f"Nodes_{datetime}_{nodeProperty}"
        self.StartColor = QColor(255, 0, 0)
        self.EndColor = QColor(0, 0, 139)
        self.Size = 3
        self.join_field = "nodeKey"
        self.fields_to_add = ["pressure", "waterDemand", "waterAge"]
        self.elementAnalysisResults()
        print("before entering addCSVNonSpatialLayerToPanel in NodeNetworkAnalysisRepository")
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime}")
        self.joinLayersAttributes(f"Nodes_{datetime}", self.LayerName, self.join_field, self.fields_to_add)
