class sectionAbstract():
    def __init__(self, id=0):
        self.__id = id
        
    @property
    def id(self):
        return self.__id
    
    def writeSection(self, outfile):
        print("Metodo no implementado...")
    