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


class AllCompile(object):
    def __init__(self):
        self.last_compile = None

    def compile(self, view, mode):
        self.last_compile = Compile(view)
        self.last_compile.compile(mode)
    def show(self):
        if not self.last_compile:
            return
        self.last_compile.show()
    def kill(self):
        if not self.last_compile:
            return
        self.last_compile.kill()


class AllCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit, mode='compile'):
        log('src', src_type(self.view))

        getac(self.view).compile(self.view, mode)

class AllCompileShowPanelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        getac(self.view).show()

class AllCompileKillCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        getac(self.view).kill()

class AllCompileCommandListCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ModePanel(self.view).show(lambda mode: getac(self.view).compile(self.view, mode))


class AllCompileTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().run_command('toggle_comment', {'panel':'allcompile_output.%d' % self.view.window().id()})