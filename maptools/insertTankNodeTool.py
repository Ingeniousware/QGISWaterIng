from .insertNodeAbstractTool import InsertNodeAbstractTool


class InsertTankNodeTool(InsertNodeAbstractTool):
    
    def __init__(self, canvas):
        super(InsertNodeAbstractTool, self).__init__(canvas)      