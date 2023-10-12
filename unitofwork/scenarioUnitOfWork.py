from ..repositories.pipeNodeRepository import PipeNodeRepository
from ..repositories.pumpNodeRepository import PumpNodeRepository
from ..repositories.reservoirNodeRepository import ReservoirNodeRepository
from ..repositories.tankNodeRepository import TankNodeRepository
from ..repositories.valveNodeRepository import ValveNodeRepository
from ..repositories.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositories.waterMeterNodeRepository import WaterMeterNodeRepository


class scenarioUnitOfWork():

    def __init__(self, token, project_path, scenarioFK):
        """Constructor."""
        self.token = token
        self.waterDemandNodeRepository = WateringDemandNodeRepository(self.token, project_path, scenarioFK)                
        self.tankNodeRepository = TankNodeRepository(self.token, project_path, scenarioFK)    
        self.reservoirNodeRepository = ReservoirNodeRepository(self.token, project_path, scenarioFK)
        self.pipeNodeRepository = PipeNodeRepository(self.token, project_path, scenarioFK)
        self.waterMeterNodeRepository = WaterMeterNodeRepository(self.token, project_path, scenarioFK)
        self.valveNodeRepository = ValveNodeRepository(self.token, project_path, scenarioFK)  
        self.pumpNodeRepository = PumpNodeRepository(self.token, project_path, scenarioFK) 

        """  myList = AbstractRepository[]
        mylist.add(self.waterDemandNodeRepository)
        myList.add(self.tankNodeRepository)
        ... """


    def UpdateFromServerToOffline(self):
        self.tankNodeRepository.updateFromServerToOffline()
        self.reservoirNodeRepository.updateFromServerToOffline()
        #foreach element in mylist
        #    element.UpdateFromServerToOffline()
        
        
    """ def UpdateFromOfflineToServer(self):
        foreach element in mylist
            element.UpdateFromOfflineToServer() """