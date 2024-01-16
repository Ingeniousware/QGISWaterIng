
from ..repositoriesLocalSHP.pipeNodeRepository import PipeNodeRepository
from ..repositoriesLocalSHP.sensorNodeRepository import SensorNodeRepository
from ..repositoriesLocalSHP.pumpNodeRepository import PumpNodeRepository
from ..repositoriesLocalSHP.reservoirNodeRepository import ReservoirNodeRepository
from ..repositoriesLocalSHP.tankNodeRepository import TankNodeRepository
from ..repositoriesLocalSHP.valveNodeRepository import ValveNodeRepository
from ..repositoriesLocalSHP.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositoriesLocalSHP.waterMeterNodeRepository import WaterMeterNodeRepository
from ..repositoriesLocalSHP.syncSystem import WateringSync

from ..watering_utils import WateringUtils

class scenarioUnitOfWork():

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        self.token = token
        self.scenarioFK = scenarioFK
        self.project_path = project_path
        self.lastUpdate = None
        self.keyUpdate = self.scenarioKeyLastUpdate()
        self.initializeRepositories()
        self.initializeSyncSystem()
        self.generateListOfElements()
        
    def initializeRepositories(self):
        self.waterDemandNodeRepository = WateringDemandNodeRepository(self.token, self.project_path, self.scenarioFK)                
        self.tankNodeRepository = TankNodeRepository(self.token, self.project_path, self.scenarioFK)     
        self.reservoirNodeRepository = ReservoirNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.pipeNodeRepository = PipeNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.waterMeterNodeRepository = WaterMeterNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.valveNodeRepository = ValveNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.pumpNodeRepository = PumpNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.sensorNodeRepository = SensorNodeRepository(self.token, self.project_path, self.scenarioFK)   
        
    def initializeSyncSystem(self):
        self.syncSystem = WateringSync(self.token, self.project_path, self.scenarioFK,
                                 self.waterDemandNodeRepository,
                                 self.tankNodeRepository, 
                                 self.reservoirNodeRepository,
                                 self.waterMeterNodeRepository,
                                 self.valveNodeRepository,                                 
                                 self.pumpNodeRepository,
                                 self.pipeNodeRepository,
                                 self.sensorNodeRepository)

    def generateListOfElements(self):
        self.list_of_elements = [self.waterDemandNodeRepository,
                                self.tankNodeRepository, 
                                self.reservoirNodeRepository,
                                self.waterMeterNodeRepository,
                                self.valveNodeRepository,                                 
                                self.pumpNodeRepository,
                                self.pipeNodeRepository,
                                self.sensorNodeRepository]

    def loadAll(self):
        for element in self.list_of_elements:
            element.initializeRepository()
            
    def updateAll(self):
        self.lastUpdate = self.getLastUpdate()
        
        for element in self.list_of_elements:
           element.generalUpdate(self.lastUpdate)
    
        WateringUtils.setProjectMetadata(self.keyUpdate, str(WateringUtils.getDateTimeNow()))

    def newUpdateAll(self):
        self.syncSystem.initializeRepository()
        
    def getLastUpdate(self):
        date = WateringUtils.getProjectMetadata(self.keyUpdate)

        print("Getting last update: ", date)
        
        if date != "default text":
            return date
        else:
            return str(WateringUtils.getDateTimeNow())
    
    def scenarioKeyLastUpdate(self):
        return self.scenarioFK + "last_general_update"
    