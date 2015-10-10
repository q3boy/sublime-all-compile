import sublime

from .util import log

class OutputPanel(object):

    def __init__(self, window, name):
        self.name = "%s.%d" % (name, window.id())
        self._window = window
        log('create panel', self.name)
        self._panel = self._get_or_create_panel(window, self.name)

    def show(self):
        log('show panel', self.name)
        self._window.run_command('show_panel', {'panel': "output.%s" % self.name})

    def lock(self):
        self._panel.set_read_only(True)

    def unlock(self):
        self._panel.set_read_only(False)

    def write(self, text):
        self.unlock()
        self._panel.run_command('append', {'characters': text})
        self.lock()

    def display(self, text):
        self.show()
        self.write(text)

    def set_syntax_file(self, syntax_file):
        self._panel.set_syntax_file(syntax_file)

    def _get_or_create_panel(self, window, name):
        try:
            return window.get_output_panel(name)
        except AttributeError:
            log("Couldn't get output panel.")
            return window.create_output_panel(name)


class Editor(object):
    def __init__(self, view):
        self._view = view

    def get_text(self):
        return self.get_selected_text() or self.get_all_text()

    def has_selected_text(self):
        for region in self._view.sel():
            if not region.empty():
                return True
        return False

    def get_selected_text(self):
        if not self.has_selected_text():
            return None
        region = self._get_selected_region()
        return self._view.substr(region)

    def get_all_text(self):
        region = self._get_full_region()
        return self._view.substr(region)

    def _get_selected_region(self):
        return self._view.sel()[0]

    def _get_full_region(self):
        return sublime.Region(0, self._view.size())


