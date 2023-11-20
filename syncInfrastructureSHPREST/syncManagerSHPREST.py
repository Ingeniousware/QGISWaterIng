import os

from ..watering_utils import WateringUtils
from ..repositoriesServerREST.waterDemandNodeServerRESTRepository import waterDemandNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.waterDemandNodeConnectorSHPREST import waterDemandNodeConnectorSHPREST
from ..repositoriesServerREST.tankNodeServerRESTRepository import tankNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.tankNodeConnectorSHPREST import tankNodeConnectorSHPREST
from ..repositoriesServerREST.reservoirNodeServerRESTRepository import reservoirNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.reservoirNodeConnectorSHPREST import reservoirNodeConnectorSHPREST
from ..repositoriesServerREST.valveNodeServerRESTRepository import valveNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.valveNodeConnectorSHPREST import valveNodeConnectorSHPREST
from ..repositoriesServerREST.pumpNodeServerRESTRepository import pumpNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.pumpNodeConnectorSHPREST import pumpNodeConnectorSHPREST
from ..repositoriesServerREST.sensorNodeServerRESTRepository import sensorNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.sensorNodeConnectorSHPREST import sensorNodeConnectorSHPREST
from ..repositoriesServerREST.pipeNodeServerRESTRepository import pipeNodeServerRESTRepository
from ..repositoryConnectorsSHPREST.pipeNodeConnectorSHPREST import pipeNodeConnectorSHPREST

from signalrcore.hub_connection_builder import HubConnectionBuilder


class syncManagerSHPREST():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.scenarioUnitOfWork = None
        self.waterDemandNodeConnector = None
        self.tankNodeConnector = None
        self.reservoirNodeConnector= None
        self.valveNodeConnector= None
        self.pumpNodeConnector= None
        self.sensorNodeConnector = None
        self.pipeNodeConnector = None
        self.waterDemandNodeServerRESTRepository = None
        self.tankNodeServerRESTRepository = None
        self.reservoirNodeServerRESTRepository = None
        self.valveNodeServerRESTRepository = None
        self.pumpNodeServerRESTRepository = None
        self.sensorNodeServerRESTRepository = None
        self.pipeNodeServerRESTRepository = None
        
        server_url = WateringUtils.getServerUrl() + "/hubs/waternetworkhub"

        self.hub_connection = HubConnectionBuilder()\
            .with_url(server_url, options={"verify_ssl": False, 
                                        "headers": {'Authorization': "Bearer {}".format(os.environ.get('TOKEN'))}}) \
            .with_automatic_reconnect({
                    "type": "interval",
                    "keep_alive_interval": 10,
                    "intervals": [1, 3, 5, 6, 7, 87, 3]
                }).build()

        #self.hub_connection.on_open(lambda: print("connection opened and handshake received ready to send messages"))
        self.hub_connection.on_open(self.jointToServerUpdateGroup)
        self.hub_connection.on_close(lambda: print("connection closed"))
        self.hub_connection.on_error(lambda data: print(f"An exception was thrown closed{data.error}"))
        



    def jointToServerUpdateGroup(self):
        print("Joining to hub")       
        invoresult = self.hub_connection.send("joingroup", [self.ScenarioFK]) 
        print(invoresult.invocation_id)



    def connectScenarioUnitOfWorkToServer(self, scenarioUnitOfWork):
        self.scenarioUnitOfWork = scenarioUnitOfWork

        #creation of connectors
        self.waterDemandNodeConnector = waterDemandNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        self.tankNodeConnector = tankNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        self.reservoirNodeConnector = reservoirNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        self.valveNodeConnector = valveNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        self.pumpNodeConnector = pumpNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        self.sensorNodeConnector = sensorNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        self.pipeNodeConnector = pipeNodeConnectorSHPREST(self.ScenarioFK, self.hub_connection)
        
        #creation of server repositories
        self.waterDemandNodeServerRESTRepository = waterDemandNodeServerRESTRepository(self.Token, self.ScenarioFK)
        self.tankNodeServerRESTRepository = tankNodeServerRESTRepository(self.Token, self.ScenarioFK)
        self.reservoirNodeServerRESTRepository = reservoirNodeServerRESTRepository(self.Token, self.ScenarioFK)
        self.valveNodeServerRESTRepository = valveNodeServerRESTRepository(self.Token, self.ScenarioFK)
        self.pumpNodeServerRESTRepository = pumpNodeServerRESTRepository(self.Token, self.ScenarioFK)
        self.sensorNodeServerRESTRepository = sensorNodeServerRESTRepository(self.Token, self.ScenarioFK)
        self.pipeNodeServerRESTRepository = pipeNodeServerRESTRepository(self.Token, self.ScenarioFK)
        
        #linking connectors and server repositories
        self.waterDemandNodeServerRESTRepository.setConnectorToLocal(self.waterDemandNodeConnector)
        self.tankNodeServerRESTRepository.setConnectorToLocal(self.tankNodeConnector)
        self.reservoirNodeServerRESTRepository.setConnectorToLocal(self.reservoirNodeConnector)
        self.valveNodeServerRESTRepository.setConnectorToLocal(self.valveNodeConnector)
        self.pumpNodeServerRESTRepository.setConnectorToLocal(self.pumpNodeConnector)
        self.sensorNodeServerRESTRepository.setConnectorToLocal(self.sensorNodeConnector)
        self.pipeNodeServerRESTRepository.setConnectorToLocal(self.pipeNodeConnector)
        
        #linking connectors and local repositories from unitofwork
        self.scenarioUnitOfWork.waterDemandNodeRepository.setConnectorToServer(self.waterDemandNodeConnector)
        self.scenarioUnitOfWork.tankNodeRepository.setConnectorToServer(self.tankNodeConnector)
        self.scenarioUnitOfWork.reservoirNodeRepository.setConnectorToServer(self.reservoirNodeConnector)
        self.scenarioUnitOfWork.valveNodeRepository.setConnectorToServer(self.valveNodeConnector)
        self.scenarioUnitOfWork.pumpNodeRepository.setConnectorToServer(self.pumpNodeConnector)
        self.scenarioUnitOfWork.sensorNodeRepository.setConnectorToServer(self.sensorNodeConnector)
        self.scenarioUnitOfWork.pipeNodeRepository.setConnectorToServer(self.pipeNodeConnector)
        
        self.hub_connection.start()

        
    def stop(self):
        print("Entering stopping the sync manager...............................................")
        if (self.hub_connection): 
            self.hub_connection.stop()
            print("Stopped the hub at sync manager...............................................")
        else:
            print("Hub cannot be reached...............................................")
            
        print("Finishing stopping the sync manager...............................................")

    