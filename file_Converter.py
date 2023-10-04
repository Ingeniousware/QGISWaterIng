import requests
from .inpProcessing.sectionCoordinates import sectionCoordinates
from .inpProcessing.sectionINPAbstract import sectionINPAbstract
from .inpProcessing.sectionLabels import sectionLabels
from .inpProcessing.sectionVertices import sectionVertices
from .inpProcessing.unknownINPSection import sectionUnknown
from .inpProcessing.sectionBackdrop import sectionBackdrop


import re

class fileConverter():
    def __init__(self):
            #Constructor.
            #self.sourceCrs = QgsCoordinateReferenceSystem(32614)
            #self.destCrs = QgsCoordinateReferenceSystem(4326)
            ...


    def fileConvertion(self):
        input_file_path = '/Users/alejandrorodriguez/Downloads/C-05.inp'
        output_file_path = '/Users/alejandrorodriguez/Downloads/C-05_updated.inp'

        with open(input_file_path, 'r', encoding='latin-1') as inp_file, open(output_file_path, 'w') as out_file:
            #processing_coordinates = False
            #processing_labels = False
            
            dictionarySection = {
                                    "unknown": sectionUnknown,
                                    "[COORDINATES]": sectionCoordinates,
                                    "[LABELS]" : sectionLabels,
                                    "[VERTICES]" : sectionVertices,
                                    "[BACKDROP]" : sectionBackdrop
                                }

            dictionarySection["unknonwn"] = sectionUnknown()
            dictionarySection["[COORDINATES]"] = sectionCoordinates()
            dictionarySection["[LABELS]"] = sectionLabels()
            dictionarySection["[VERTICES]"] = sectionVertices()
            dictionarySection["[BACKDROP]"] = sectionBackdrop()
            activeSection = sectionINPAbstract()

            for line in inp_file:
                cleanLine = line.strip()
                if (len(cleanLine) == 0) or (len(cleanLine) > 0 and cleanLine[0] == ';'):
                    out_file.write(line)
                    continue

                if cleanLine[0] == "[":
                    #if (dictionarySection.contains(cleanLine)):
                    if cleanLine in dictionarySection:
                        activeSection = dictionarySection[cleanLine]
                    else:
                        activeSection =  dictionarySection["unknonwn"]

                activeSection.ProcessCoordinatesConvertion(out_file, cleanLine)
                