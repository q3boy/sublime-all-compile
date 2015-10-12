from .settings import Settings

class ModePanel(object):
    def __init__(self, view):
        self.view = view
        self.window = view.window()
        self.settings = Settings

    def show(self, func):
        keys = Settings().get_mode(self.view)
        self.window.show_quick_panel(keys, lambda x: func(keys[x]))
