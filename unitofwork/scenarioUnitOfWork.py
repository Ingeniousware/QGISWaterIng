from typing import Optional, Dict, List

from ..repositoriesLocalSHP.pipeNodeRepository import PipeNodeRepository
from ..repositoriesLocalSHP.sensorNodeRepository import SensorNodeRepository
from ..repositoriesLocalSHP.pumpNodeRepository import PumpNodeRepository
from ..repositoriesLocalSHP.reservoirNodeRepository import ReservoirNodeRepository
from ..repositoriesLocalSHP.tankNodeRepository import TankNodeRepository
from ..repositoriesLocalSHP.valveNodeRepository import ValveNodeRepository
from ..repositoriesLocalSHP.waterDemandNodeRepository import WateringDemandNodeRepository
from ..repositoriesLocalSHP.waterMeterNodeRepository import WaterMeterNodeRepository
from ..syncInfrastructureSHPREST.syncSystem import WateringSync
from ..watering_utils import WateringUtils

from qgis.core import QgsVectorLayer

class ScenarioUnitOfWork:
    PROGRESS_START = 40
    PROGRESS_INCREMENT = 10

    def __init__(self, token: str, project_path: str, scenario_fk: str) -> None:
        self.token = token
        self.scenario_fk = scenario_fk
        self.project_path = project_path
        self.syncSystem = None

        self._initialize_repositories()
        self._generate_element_list()
        self._initialize_sync_system()

    def _initialize_repositories(self) -> None:
        self.waterDemandNodeRepository = WateringDemandNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.tankNodeRepository = TankNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.reservoirNodeRepository = ReservoirNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.pipeNodeRepository = PipeNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.waterMeterNodeRepository = WaterMeterNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.valveNodeRepository = ValveNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.pumpNodeRepository = PumpNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )
        self.sensorNodeRepository = SensorNodeRepository(
            self.token, self.project_path, self.scenario_fk
        )

    def _generate_element_list(self) -> None:
        self.list_of_elements = [
            self.waterDemandNodeRepository,
            self.tankNodeRepository,
            self.reservoirNodeRepository,
            self.waterMeterNodeRepository,
            self.valveNodeRepository,
            self.pumpNodeRepository,
            self.pipeNodeRepository,
            self.sensorNodeRepository,
        ]

        self.layer_names = {
            repo.LayerName: repo for repo in self.list_of_elements
        }

    def _initialize_sync_system(self) -> None:
        self.syncSystem = WateringSync(
            self.token,
            self.project_path,
            self.scenario_fk,
            self.list_of_elements
        )

    def load_all(self, progress_bar: any, offline: bool) -> None:
        progress = self.PROGRESS_START
        
        for element in self.list_of_elements:
            element.initializeRepository(offline)
            progress_bar.setValue(progress)
            progress += self.PROGRESS_INCREMENT

    def update_all(self) -> None:
        self.syncSystem.synchronize()

    def synchronize(self) -> None:
        self.syncSystem.synchronize()

    def get_repository_by_layer(self, layer: QgsVectorLayer) -> Optional[any]:
        return self.layer_names.get(layer.name())