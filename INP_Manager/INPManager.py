
from .sectionTitle import sectionTitle


class INPManager():
    def __init__(self, outfile=None):
        self.outfile = outfile
        self.sections = []
        title = sectionTitle("Prueba de INP")
        self.sections.append(title)
        
    def writeSections(self, outfile=None):
        if outfile is not None:
            self.outfile = outfile
        
        #Se debe organizar los sections antes de mandarlas a escribir, comprobar que todas las secciones esten escritas de no estar escrita se crea vacia.
        
        for section in self.sections:
            section.writeSection(self.outfile)
        