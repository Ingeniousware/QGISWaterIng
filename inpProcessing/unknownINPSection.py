
from ..inpProcessing.sectionINPAbstract import sectionINPAbstract


class sectionUnknown(sectionINPAbstract):
    def __init__(self):
            #Constructor.
            super(sectionUnknown, self).__init__()  


    def ProcessCoordinatesConvertion(self, out_file, line):
        
        out_file.write(line + '\n')