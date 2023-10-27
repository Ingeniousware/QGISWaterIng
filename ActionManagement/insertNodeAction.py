from ..ActionManagement.abstractAction import abstractAction


class insertNodeAction(abstractAction):

    def __init__(self, repository, x, y):
        """Constructor."""
        super(insertNodeAction, self).__init__(repository)     
        self.x = x
        self.y = y
        self.feature = None


    def execute(self):
        self.feature = self.elementRepository.AddNewElementFromMapInteraction(self.x, self.y)

    def reDo(self):
        self.execute()

    def unDo(self):
        self.elementRepository.deleteFeatureFromMapInteraction(self.feature)