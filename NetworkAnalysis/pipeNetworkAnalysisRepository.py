import os
from .abstractAnalysisRepository import AbstractAnalysisRepository
from ..watering_utils import WateringUtils
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsProject


class PipeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self, token, analysisExecutionId, datetime, pipeProperty, behavior, field=None):
        """Constructor."""
        super().__init__(token, analysisExecutionId, datetime, behavior)
        self.UrlGet = "/api/v1/WaterAnalysisResults/linksgetfull"
        self.KeysApi = ["pipeKey", "pipeCurrentStatus", "velocity", "flow", "headLoss"]
        self.Attributes = ["C Status", "Velocity", "Flow", "HeadLoss"]
        self.LayerName = "watering_pipes"
        # self.Field = "Velocity"
        # self.Field = (f"Pipes_{datetime}_velocity")
        self.Field = f"Pipes_{datetime}_{pipeProperty}"
        print("00012: ", datetime)
        self.StartColor = QColor(255, 0, 0)
        self.EndColor = QColor(0, 0, 139)
        self.Size = 1
        self.join_field = "pipeKey"
        self.fields_to_add = ["velocity", "flow", "headLoss"]

        #removing the file in case it already exist
        project_path = WateringUtils.getProjectPath()
        scenario_id = QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]
        scenario_folder_path = project_path + "/" + scenario_id
        analysis_folder_path = scenario_folder_path + "/" + "Analysis"
        date_folder_path = analysis_folder_path + "/" + datetime.replace(":", "")
        resultsFile = os.path.join(date_folder_path, f"{self.analysisExecutionId}_Pipes.csv")
        if os.path.isfile(resultsFile):
            os.remove(resultsFile)

        self.elementAnalysisResults()
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Pipes.csv", f"Pipes_{datetime}")
        self.joinLayersAttributes(f"Pipes_{datetime}", self.LayerName, self.join_field, self.fields_to_add)
