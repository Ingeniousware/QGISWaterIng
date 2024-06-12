
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
        self.initializeRepositories()
        self.generateListOfElements()
        self.initializeSyncSystem()
        
    def initializeRepositories(self):
        self.waterDemandNodeRepository = WateringDemandNodeRepository(self.token, self.project_path, self.scenarioFK)                
        self.tankNodeRepository = TankNodeRepository(self.token, self.project_path, self.scenarioFK)     
        self.reservoirNodeRepository = ReservoirNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.pipeNodeRepository = PipeNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.waterMeterNodeRepository = WaterMeterNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.valveNodeRepository = ValveNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.pumpNodeRepository = PumpNodeRepository(self.token, self.project_path, self.scenarioFK)   
        self.sensorNodeRepository = SensorNodeRepository(self.token, self.project_path, self.scenarioFK)   
                
    def generateListOfElements(self):
        self.list_of_elements = [self.waterDemandNodeRepository,
                                self.tankNodeRepository, 
                                self.reservoirNodeRepository,
                                self.waterMeterNodeRepository,
                                self.valveNodeRepository,                                 
                                self.pumpNodeRepository,
                                self.pipeNodeRepository,
                                self.sensorNodeRepository]
        
        self.layer_names = {repo.LayerName: repo for repo in self.list_of_elements}

    def initializeSyncSystem(self):
        self.syncSystem = WateringSync(self.token, self.project_path, self.scenarioFK, self.list_of_elements)
        
    def loadAll(self, progressBar):
        i = 40
        for element in self.list_of_elements:
            element.initializeRepository()
            progressBar.setValue(i)
            i += 10
            
    def updateAll(self):
        lastUpdate = WateringUtils.getLastUpdate()
        keyUpdate = WateringUtils.scenarioKeyLastUpdate(self.scenarioFK)
        
        _lastUpdated_ = WateringUtils.get_last_updated(self.scenarioFK)
        
        print("THE LAST _lastUpdated_: ", _lastUpdated_)
        
        for element in self.list_of_elements:
           element.generalUpdate(_lastUpdated_)
    
        WateringUtils.setProjectMetadata(keyUpdate, WateringUtils.getDateTimeNow().toString("yyyy-MM-dd hh:mm:ss"))

    def newUpdateAll(self):
        self.syncSystem.synchronize()
    
    def getRepoByLayer(self, layer):
        return self.layer_names.get(layer.name(), None)
        