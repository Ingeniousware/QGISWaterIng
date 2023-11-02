from ..repositoriesLocalSHP.abstract_repository import AbstractRepository
from ..repositoriesLocalSHP.pipeNodeRepository import PipeNodeRepository
from ..repositoriesLocalSHP.pumpNodeRepository import PumpNodeRepository
from ..repositoriesLocalSHP.reservoirNodeRepository import ReservoirNodeRepository
from ..repositoriesLocalSHP.tankNodeRepository import TankNodeRepository
from ..repositoriesLocalSHP.valveNodeRepository import ValveNodeRepository
from ..repositoriesLocalSHP.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositoriesLocalSHP.waterMeterNodeRepository import WaterMeterNodeRepository

from datetime import datetime

class scenarioUnitOfWork():

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        self.token = token
        self.scenarioFK = scenarioFK
        self.waterDemandNodeRepository = WateringDemandNodeRepository(self.token, project_path, scenarioFK)                
        self.tankNodeRepository = TankNodeRepository(self.token, project_path, scenarioFK)    
        self.reservoirNodeRepository = ReservoirNodeRepository(self.token, project_path, scenarioFK)
        self.pipeNodeRepository = PipeNodeRepository(self.token, project_path, scenarioFK)
        self.waterMeterNodeRepository = WaterMeterNodeRepository(self.token, project_path, scenarioFK)
        self.valveNodeRepository = ValveNodeRepository(self.token, project_path, scenarioFK)  
        self.pumpNodeRepository = PumpNodeRepository(self.token, project_path, scenarioFK) 

        self.list_of_elements = [self.waterDemandNodeRepository,
                                 self.tankNodeRepository, 
                                 self.reservoirNodeRepository,
                                 self.waterMeterNodeRepository,
                                 self.valveNodeRepository,                                 
                                 self.pumpNodeRepository,
                                 self.pipeNodeRepository]
        
        self.lastUpdatedToServer = None
        self.lastUpdatedFromServer = None


    def loadAll(self):
        for element in self.list_of_elements:
            element.initializeRepository()

        
    def updateAll(self):

        self.lastUpdatedFromServer = AbstractRepository.getDateTimeNow() #datetime.now()

        """ for element in self.list_of_elements:
            element.updateFromServerToOffline(self.lastUpdatedFromServer) """
    
        
        self.lastUpdatedToServer = AbstractRepository.getDateTimeNow() # datetime.now()
        for element in self.list_of_elements:
            element.updateFromOfflineToServer(self.lastUpdatedToServer)


        