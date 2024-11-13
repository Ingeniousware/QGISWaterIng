from ..ActionManagement.abstractAction import abstractAction


class deleteElementAction(abstractAction):

    def __init__(self, repository, x, y):
        """Constructor."""
        super(deleteElementAction, self).__init__(repository)     
        self.x = x
        self.y = y
        self.feature = None


    def execute(self):
        self.elementRepository.deleteFeatureFromMapInteraction(self.feature)

    def reDo(self):
        self.execute()

    def unDo(self):
        print("Getting inside the undo of insert node")
        self.feature = self.elementRepository.AddNewElementFromMapInteraction(self.x, self.y)
        