from .abstractAnalysisRepository import AbstractAnalysisRepository
from ..watering_utils import WateringUtils
from qgis.PyQt.QtGui import QColor


class PipeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self,token, analysisExecutionId, datetime, behavior):
        """Constructor."""
        super(PipeNetworkAnalysisRepository, self).__init__(token, analysisExecutionId, datetime ,behavior)      
        self.UrlGet = "/api/v1/WaterAnalysisResults/pipes"
        self.KeysApi = ["pipeKey","pipeCurrentStatus", "velocity", "flow", "headLoss"]
        self.Attributes = ["C Status","Velocity", "Flow","HeadLoss"]
        self.LayerName = "watering_pipes"
        self.Field = "Velocity"
        self.StartColor = QColor(255, 0, 0)
        self.EndColor = QColor(0, 0, 139)
        self.Size = 1
        self.elementAnalysisResults()
        self.addLayerToPanel()