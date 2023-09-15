from .insertNodeAbstractTool import InsertNodeAbstractTool


class InsertReservoirNodeTool(InsertNodeAbstractTool):
    
    def __init__(self, canvas):
        super(InsertNodeAbstractTool, self).__init__(canvas)      