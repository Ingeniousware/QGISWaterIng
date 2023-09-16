from .insertNodeAbstractTool import InsertNodeAbstractTool

class InsertDemandNodeTool(InsertNodeAbstractTool):
    
    def __init__(self, canvas):
        super(InsertDemandNodeTool, self).__init__(canvas)  
        print("Init at Insert Demand Node")

    def deactivate(self):
        print("deactivate insert demand node tool")