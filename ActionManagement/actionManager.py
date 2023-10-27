import queue 

class actionManager():

    def __init__(self, token, scenarioFK):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.doneActions = queue.Queue(100)
        self.undoneActions = queue.Queue(100)


    def execute(self, action):
        action.execute()
        #print("after executing action in action manager")
        self.doneActions.put(action)
        while not self.undoneActions.empty():
            self.undoneActions.get()


    def undoAction(self):
        #take action from the FIFO of doneActions and call action.Undo and copy it to the FIFO of undoneActions
        action = self.doneActions.get()
        action.unDo()
        self.undoneActions.put(action)
        

    def redoAction(self):
        #take action from the FIFO of undoneActions and call action.Redo and copy it to the FIFO of doneActions
        action = self.undoneActions.get()
        action.reDo()
        self.doneActions.put(action)

        