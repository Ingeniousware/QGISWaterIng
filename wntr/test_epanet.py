import os
import pathlib

from epanetSimulation import runepanet
from utils.logger import start_logging

from epanet.toolkit import PrintToolkit

start_logging()

PrintToolkit()
file = "C:\\Temp\\test.inp"


print(os.getcwd())

print(pathlib.Path(__file__).parent.absolute())

runepanet(file)