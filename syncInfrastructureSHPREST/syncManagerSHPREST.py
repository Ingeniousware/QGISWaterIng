from ..repositoriesServerREST.waterDemandNodeServerRESTRepository import waterDemandNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.waterDemandNodeConnectorSHPREST import waterDemandNodeConnectorSHPREST


class syncManagerSHPREST():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.scenarioUnitOfWork = None
        self.waterDemandNodeConnector = None
        self.waterDemandNodeServerRESTRepository = None

    def connectScenarioUnitOfWorkToServer(self, scenarioUnitOfWork):
        self.scenarioUnitOfWork = scenarioUnitOfWork
        
        self.waterDemandNodeServerRESTRepository = waterDemandNodeServerRESTRepository(self.Token, self.ScenarioFK)
        
        self.waterDemandNodeConnector = waterDemandNodeConnectorSHPREST()

        self.waterDemandNodeServerRESTRepository.setConnectorToLocal(self.waterDemandNodeConnector)

        self.scenarioUnitOfWork.waterDemandNodeRepository.setConnectorToServer(self.waterDemandNodeConnector)
        

    