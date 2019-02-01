from krita import *
from . import myuiexportlayers

class MyExtension(Extension):

    def __init__(self, parent):
        #This is initialising the parent, always  important when subclassing.
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("myAction", "My Script", "tools/scripts")
        action.setToolTip(i18n("Plugin to export layers from a document."))
        action.triggered.connect(self.initialize)

    def initialize(self):
        self.uiexportlayers = myuiexportlayers.MyUIExportLayers()
        self.uiexportlayers.initialize()

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance()))
