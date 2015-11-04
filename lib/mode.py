from .util import log
from .settings import Settings

class ModePanel(object):
    def __init__(self, view):
        self.view = view
        self.window = view.window()
        self.settings = Settings



    def show(self, func):
        keys = Settings().get_mode(self.view)
        nkeys = []
        nkkeys = []
        for key in keys:
            if key != 'execute' and key != 'compile':
                nkeys.append(key)
                nkkeys.append(key)
        for key in keys:
            if key == 'execute' or key == 'compile':
                nkeys.append("* " + key)
                nkkeys.append(key)
        self.window.show_quick_panel(nkeys, lambda x: func(nkkeys[x]) if x >= 0 else None)
