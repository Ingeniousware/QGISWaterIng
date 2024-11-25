
from .sections import sectionTitle, sectionJunctions, sectionReservoirs, sectionTanks, sectionEnd

class INPManager():
    def __init__(self, outfile=None):
        self.outfile = outfile

        self.sections = {'TITLE': sectionTitle('PRUEBA DE INP'),
                         'JUNCTIONS': sectionJunctions(),
                         'RESERVOIRS': sectionReservoirs(),
                         'TANKS': sectionTanks(),
                         
                         'END': sectionEnd()}

    def writeSections(self, outfile=None):
        if outfile is not None:
            self.outfile = outfile

        #Se debe organizar los sections antes de mandarlas a escribir, comprobar que todas las secciones esten escritas de no estar escrita se crea vacia.

        for t, s in self.sections.items():
            print(t,s.name)
            s.writeSection(self.outfile)
