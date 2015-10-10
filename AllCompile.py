import sublime, sublime_plugin


from .lib.compile import Compile
from .lib.util import log


AC_DICT = {}

def getac(view):
    wid = view.window().id()
    log('window id', wid)
    ac_inst = AC_DICT.get(wid)
    if ac_inst:
        return ac_inst
    ac_inst = AllCompile(view)
    AC_DICT[wid] = ac_inst
    return ac_inst


class AllCompile(object):
    def __init__(self, view):
        self.view = view
        self.last_compile = None

    def compile(self, mode):
        self.last_compile = Compile(self.view)
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
        getac(self.view).compile(mode)

class AllCompileShowPanelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        getac(self.view).show()

