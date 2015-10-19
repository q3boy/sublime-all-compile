import sublime, sublime_plugin


from .lib.compile import Compile
from .lib.mode import ModePanel
from .lib.util import log
from .lib.settings import src_type


AC_DICT = {}

def getac(view):
    wid = view.window().id()
    log('window id', wid)
    ac_inst = AC_DICT.get(wid)
    if ac_inst:
        return ac_inst
    ac_inst = AllCompile()
    AC_DICT[wid] = ac_inst
    return ac_inst


class AllCompile(Compile):

    def run_compile(self, view, mode):
        if self.running:
            if sublime.ok_cancel_dialog('Another task is still running.', 'Kill & Run'):
                self.kill()
                self.clean_panel()
                def tmp():
                    self.clean_panel()
                    self.compile(view, mode)
                sublime.set_timeout(tmp, 300)
            return
        self.compile(view, mode)

    def show(self):
        self.panel.show()

class AllCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit, mode='compile'):
        log('src', src_type(self.view))
        getac(self.view).run_compile(self.view, mode)

class AllCompileShowPanelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        getac(self.view).show()

class AllCompileKillCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        getac(self.view).kill()

class AllCompileTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.set_name('*AC* test ccc')
        self.view.erase(edit, sublime.Region(0, self.view.size()))

class AllCompileCommandListCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ModePanel(self.view).show(lambda mode: getac(self.view).compile(self.view, mode))

class AllCompileTabCleanCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.set_read_only(False)
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.set_read_only(True)

class AllCompileTabAppendCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.set_read_only(False)
        self.view.insert(edit, self.view.size(), text)
        self.view.set_read_only(True)

class AllCompileTabFocusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().focus_view(self.view)

