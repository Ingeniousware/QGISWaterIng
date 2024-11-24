from .sectionAbstract import sectionAbstract


class sectionTitle(sectionAbstract):
    def __init__(self, title=""):
        super(sectionTitle, self).__init__(1)
        self.title = title
        
    def writeSection(self, outfile):
        outfile.write("[TITLE]\n")
        outfile.write(self.title + '\n')