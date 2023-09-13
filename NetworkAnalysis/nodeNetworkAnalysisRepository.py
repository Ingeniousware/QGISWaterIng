from .abstractAnalysisRepository import AbstractAnalysisRepository
from qgis.PyQt.QtGui import QColor

class NodeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self,token,analysisExecutionId, datetime, behavior):
        """Constructor."""
        super(NodeNetworkAnalysisRepository, self).__init__(token,analysisExecutionId, datetime, behavior)      
        self.UrlGet = "https://dev.watering.online/api/v1/WaterAnalysisResults/nodes"
        self.KeysApi = ["nodeKey", "pressure", "waterDemand", "waterDemandCovered", "waterAge"]
        self.Attributes = ["Pressure", "Demand","Demand C", "Age"]
        self.LayerName = "watering_demand_nodes"
        self.Field = "Pressure"
        self.StartColor = QColor(255, 0, 0)
        self.EndColor = QColor(0, 0, 139)
        self.Size = 3
        self.elementAnalysisResults()