import queue 

class actionManager():

    def __init__(self, token, scenarioFK, setActiveStateUndo, setActiveStateRedo):
        """Constructor."""
        self.Token = token
        self.ScenarioFK = scenarioFK
        self.doneActions = queue.Queue(100)
        self.undoneActions = queue.Queue(100)
        self.setActiveStateUndo = setActiveStateUndo
        self.setActiveStateRedo = setActiveStateRedo


    def execute(self, action):
        action.execute()
        #print("after executing action in action manager")
        self.doneActions.put(action)
        print("Calling the activation of undo button")
        self.setActiveStateUndo(True)
        self.setActiveStateRedo(False)
        while not self.undoneActions.empty():
            self.undoneActions.get()


    def undoAction(self):
        #take action from the FIFO of doneActions and call action.Undo and copy it to the FIFO of undoneActions
        print("Entering undo Action at action manager")
        action = self.doneActions.get()
        print("Calling action undo")
        action.unDo()
        self.undoneActions.put(action)
        if (not self.doneActions.empty()): self.setActiveStateUndo(True)
        else: self.setActiveStateUndo(False)
        self.setActiveStateRedo(True)
        

    def redoAction(self):
        #take action from the FIFO of undoneActions and call action.Redo and copy it to the FIFO of doneActions
        action = self.undoneActions.get()
        action.reDo()
        self.doneActions.put(action)
        if (not self.undoneActions.empty()): self.setActiveStateRedo(True)
        else: self.setActiveStateRedo(False)
        self.setActiveStateUndo(True)

    def unset(self):
        self.doneActions = None
        self.undoneActions = None
        self.setActiveStateUndo = None
        self.setActiveStateRedo = None
        print("Action manager has been unset.")
        