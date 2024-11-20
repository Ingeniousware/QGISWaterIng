from PyQt5.QtWidgets import QAction


class toolbarAction(QAction):

    def __init__(self, icon, text, parent):
        super(toolbarAction, self).__init__(icon, text, parent)
        self.MapTool = None

    def setCurrentTool(self, tool):
        self.MapTool = tool
