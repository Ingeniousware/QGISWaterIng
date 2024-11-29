class sectionAbstract():
    def __init__(self, id=0):
        self.__id = id
        self.__name = None
        self.__values = []
        
    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, value):
        self.__name = value
    @property
    def values(self):
        return self.__values
    
    @values.setter
    def values(self, value):
        self.__values = value
    
    def writeSection(self, outfile):
        print("Metodo no implementado...")
    