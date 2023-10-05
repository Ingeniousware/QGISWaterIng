import os
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


    def fileConvertion(self, file_path, sourceCrs):
        file_dir, file_name = os.path.split(file_path)
        new_file_name = os.path.splitext(file_name)[0] + '_converted' + os.path.splitext(file_name)[1]
        output_file_path = os.path.join(file_dir, new_file_name)


        with open(file_path, 'r', encoding='latin-1') as inp_file, open(output_file_path, 'w') as out_file:
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
            dictionarySection["[COORDINATES]"] = sectionCoordinates(sourceCrs)
            dictionarySection["[LABELS]"] = sectionLabels(sourceCrs)
            dictionarySection["[VERTICES]"] = sectionVertices(sourceCrs)
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

                
                