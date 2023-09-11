from NetworkAnalysis.abstractAnalysisRepository import AbstractAnalysisRepository


class PipeNetworkAnalysisRepository(AbstractAnalysisRepository):

    def __init__(self,token, project_path, scenarioFK):
        """Constructor."""
        super(PipeNetworkAnalysisRepository, self).__init__(token, scenarioFK)      
        self.UrlGet = "https://dev.watering.online/api/v1/WaterAnalysisResults/pipes"