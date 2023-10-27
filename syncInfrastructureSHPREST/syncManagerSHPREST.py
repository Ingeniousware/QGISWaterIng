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

        #creation of connectors
        self.waterDemandNodeConnector = waterDemandNodeConnectorSHPREST(self.ScenarioFK)
        
        #creation of server repositories
        self.waterDemandNodeServerRESTRepository = waterDemandNodeServerRESTRepository(self.Token, self.ScenarioFK)

        #linking connectors and server repositories
        self.waterDemandNodeServerRESTRepository.setConnectorToLocal(self.waterDemandNodeConnector)

        #linking connectors and local repositories from unitofwork
        self.scenarioUnitOfWork.waterDemandNodeRepository.setConnectorToServer(self.waterDemandNodeConnector)
        

    