from ..ActionManagement.abstractAction import abstractAction


class insertPipeAction(abstractAction):

    def __init__(self, repository, vertexs, upnode, downnode):
        """Constructor."""
        super(insertPipeAction, self).__init__(repository)     
        self.vertexs = vertexs
        self.upnode = upnode
        self.downnode = downnode
        self.feature = None


    def execute(self):
        self.feature = self.elementRepository.AddNewElementFromMapInteraction(self.vertexs, self.upnode, self.downnode)

    def reDo(self):
        self.execute()

    def unDo(self):
        print("Getting inside the undo of insert node")
        self.elementRepository.deleteFeatureFromMapInteraction(self.feature)