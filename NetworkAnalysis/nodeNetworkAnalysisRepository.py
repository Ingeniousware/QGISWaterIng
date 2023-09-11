from NetworkAnalysis.abstractAnalysisRepository import AbstractAnalysisRepository


class NodeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(NodeNetworkAnalysisRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/WaterAnalysisResults/nodes"