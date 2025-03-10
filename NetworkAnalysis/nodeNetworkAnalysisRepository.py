import os
from ..repositoriesLocalSHP.getDataRepository import getDataRepository
from .abstractAnalysisRepository import AbstractAnalysisRepository
from ..watering_utils import WateringUtils
from qgis.core import QgsProject
from qgis.PyQt.QtGui import QColor # type: ignore


class NodeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self, token, analysisExecutionId, datetime, nodeProperty, behavior, field=None):
        """Constructor."""
        super().__init__(token, analysisExecutionId, datetime, behavior)
        self.UrlGet = "/api/v1/WaterAnalysisResults/nodesgetfull"
        self.KeysApi = ["nodeKey", "pressure", "waterDemand", "waterDemandCovered", "waterAge"]
        self.Attributes = ["Pressure", "Demand", "Demand C", "Age"]
        self.LayerName = "watering_demand_nodes"
        # self.Field = "Pressure"
        # self.Field = (f"Nodes_{datetime}_pressure")
        self.Field = f"Nodes_{datetime}_{nodeProperty}"
        # self.StartColor = QColor(255, 0, 0)
        # self.EndColor = QColor(0, 0, 139)
        self.StartColor = QColor(55, 148, 255)
        self.EndColor = QColor(255, 47, 151)
        self.Size = 3
        self.join_field = "nodeKey"
        self.fields_to_add = ["pressure", "waterDemand", "waterAge"]

        #removing the file in case it already exist
        project_path = WateringUtils.getProjectPath()
        scenario_id = QgsProject.instance().readEntry("watering", "scenario_id", "default text")[0]
        scenario_folder_path = project_path + "/" + scenario_id
        analysis_folder_path = scenario_folder_path + "/" + "Analysis"
        date_folder_path = analysis_folder_path + "/" + datetime.replace(":", "")
        resultsFile = os.path.join(date_folder_path, f"{self.analysisExecutionId}_Nodes.csv")
        if os.path.isfile(resultsFile):
            os.remove(resultsFile)

        self.elementAnalysisResults()
        print("before entering addCSVNonSpatialLayerToPanel in NodeNetworkAnalysisRepository")
        self.addCSVNonSpatialLayerToPanel(f"{self.analysisExecutionId}_Nodes.csv", f"Nodes_{datetime}")
        self.joinLayersAttributes(f"Nodes_{datetime}", self.LayerName, self.join_field, self.fields_to_add)



    def elementAnalysisResults(self):
        print("Entering nodes AnalysisResults")
        response = self.getResponse()

        filename = self.analysisExecutionId

        element_dict = {}
        for elementData in response.json()["data"]:
            for element in elementData["demandNodeResults"]:
                element["simulationDateTime"] = elementData["timeStamp"]
                element_dict[element[self.KeysApi[0]]] = [
                    element[self.KeysApi[1]],
                    element[self.KeysApi[2]],
                    element[self.KeysApi[3]],
                    element[self.KeysApi[4]],
                ]
                getDataRepository.analysis_to_csv(element, element, filename, self.datetime)
