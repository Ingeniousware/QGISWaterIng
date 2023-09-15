from .insertNodeAbstractTool import InsertNodeAbstractTool

class InsertDemandNodeTool(InsertNodeAbstractTool):
    
    def __init__(self, canvas, action):
        super(InsertDemandNodeTool, self).__init__(canvas, action)  