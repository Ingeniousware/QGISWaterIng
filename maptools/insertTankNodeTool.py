from .insertAbstractTool import InsertAbstractTool


class InsertTankNodeTool(InsertAbstractTool):
    
    def __init__(self, canvas):
        super(InsertAbstractTool, self).__init__(canvas)      