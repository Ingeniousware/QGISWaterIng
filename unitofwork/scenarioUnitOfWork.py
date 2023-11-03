
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
                                 self.sensorNodeRepository
                                ]
        
        self.lastUpdatedToServer = self.getLastUpdatedToServer()
        self.lastUpdatedFromServer = self.getLastUpdatedFromServer()

    def loadAll(self):
        for element in self.list_of_elements:
            element.initializeRepository()

    def updateAll(self):
        now = WateringUtils.getDateTimeNow().value().toString("yyyy/MM/dd HH:mm:ss.zzz")
        
        """for element in self.list_of_elements:
            element.updateFromServerToOffline(self.lastUpdatedFromServer)
        self.lastUpdatedFromServer = now"""
        
        for element in self.list_of_elements:
            element.updateFromOfflineToServer(self.lastUpdatedToServer)
        self.lastUpdatedToServer = now

        self.updateProjectMetadata(now)
        
    def getLastUpdatedToServer(self):
        date = WateringUtils.getProjectMetadata("lastUpdatedToServer")
        
        if date != "default text":
            return date
        else:
            now = WateringUtils.getDateTimeNow().value().toString("yyyy/MM/dd HH:mm:ss.zzz")
            WateringUtils.setProjectMetadata("lastUpdatedToServer", now)
            return now
        
    def getLastUpdatedFromServer(self):
        date = WateringUtils.getProjectMetadata("lastUpdatedFromServer")
        
        if date != "default text":
            return date
        else:
            now = WateringUtils.getDateTimeNow().value().toString("yyyy/MM/dd HH:mm:ss.zzz")
            WateringUtils.setProjectMetadata("lastUpdatedFromServer", now)
            return now
        
    def updateProjectMetadata(self, now):
        WateringUtils.setProjectMetadata("lastUpdatedToServer", now)
        WateringUtils.setProjectMetadata("lastUpdatedFromServer", now)