
from ..repositoriesLocalSHP.pipeNodeRepository import PipeNodeRepository
from ..repositoriesLocalSHP.sensorNodeRepository import SensorNodeRepository
from ..repositoriesLocalSHP.pumpNodeRepository import PumpNodeRepository
from ..repositoriesLocalSHP.reservoirNodeRepository import ReservoirNodeRepository
from ..repositoriesLocalSHP.tankNodeRepository import TankNodeRepository
from ..repositoriesLocalSHP.valveNodeRepository import ValveNodeRepository
from ..repositoriesLocalSHP.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositoriesLocalSHP.waterMeterNodeRepository import WaterMeterNodeRepository

from ..watering_utils import WateringUtils

class scenarioUnitOfWork():

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        self.token = token
        self.scenarioFK = scenarioFK
        self.project_path = project_path
        
        self.keyUpdate = self.scenarioKeyLastUpdate()
        
        self.waterDemandNodeRepository = WateringDemandNodeRepository(self.token, project_path, scenarioFK)                
        self.tankNodeRepository = TankNodeRepository(self.token, project_path, scenarioFK)    
        self.reservoirNodeRepository = ReservoirNodeRepository(self.token, project_path, scenarioFK)
        self.pipeNodeRepository = PipeNodeRepository(self.token, project_path, scenarioFK)
        self.waterMeterNodeRepository = WaterMeterNodeRepository(self.token, project_path, scenarioFK)
        self.valveNodeRepository = ValveNodeRepository(self.token, project_path, scenarioFK)  
        self.pumpNodeRepository = PumpNodeRepository(self.token, project_path, scenarioFK)
        self.sensorNodeRepository = SensorNodeRepository(self.token, project_path, scenarioFK)

        self.list_of_elements = [self.waterDemandNodeRepository,
                                 self.tankNodeRepository, 
                                 self.reservoirNodeRepository,
                                 self.waterMeterNodeRepository,
                                 self.valveNodeRepository,                                 
                                 self.pumpNodeRepository,
                                 self.pipeNodeRepository,
                                 self.sensorNodeRepository]
        
        self.lastUpdate = self.getLastUpdate()
        
    def loadAll(self):
        for element in self.list_of_elements:
            element.initializeRepository()

    def updateAll(self):
        
        # Only water meters
        #self.list_of_elements = [self.waterMeterNodeRepository]
        
        now = WateringUtils.getDateTimeNow()
        
        for element in self.list_of_elements:
            element.generalUpdate(self.lastUpdate)
        self.lastUpdate = now
    
        WateringUtils.setProjectMetadata(self.keyUpdate, self.lastUpdate)
        
    def getLastUpdate(self):
        date = WateringUtils.getProjectMetadata(self.keyUpdate)

        print("Getting last update: ", date)
        
        if date != "default text":
            return date
        else:
            # First update, update everything
            date = "1800-11-30T14:39:22.4189860Z"
            
            WateringUtils.setProjectMetadata(self.keyUpdate, date)
            
            return date
    
    def scenarioKeyLastUpdate(self):
        return self.scenarioFK + "last_general_update"
    