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
        try:
            self.panel.show()
        except Exception:
            pass

class AllCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit, mode='compile'):
        ac = getac(self.view)
        if mode == '__LAST_COMMAND__' and ac.last_mode:
            mode = ac.last_mode
        ac.run_compile(self.view, mode)

class AllCompileShowPanelCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        getac(self.view).show()

class AllCompileKillCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        getac(self.view).kill()

class AllCompileAnsiCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        view.set_read_only(False)
        view.settings().set("color_scheme", "Packages/AllCompile/ansi.tmTheme")
        view.set_syntax_file('Packages/AllCompile/ansi.tmLanguage')
        view.settings().set("draw_white_space", "none")
        view.settings().set("line_numbers", False)

        # removing unsupported ansi escape codes before going forward: 2m 4m 5m 7m 8m
        ansi_unsupported_codes = view.find_all(r'(\x1b\[(0;)?(2|4|5|7|8)m)')
        log(ansi_unsupported_codes)
        ansi_unsupported_codes.reverse()
        for r in ansi_unsupported_codes:
            view.replace(edit, r, "\x1b[1m")

        settings = sublime.load_settings("ansi.sublime-settings")
        for bg in settings.get("ANSI_BG", []):
            for fg in settings.get("ANSI_FG", []):
                regex = r'({0}{1}(?!\x1b))(.+?)(?=\x1b)|({1}{0}(?!\x1b))(.+?)(?=\x1b)'.format(fg['code'], bg['code'])
                ansi_scope = "{0}{1}".format(fg['scope'], bg['scope'])
                ansi_regions = view.find_all(regex)
                log(ansi_scope, '\n', regex, '\n', ansi_regions, '---------------')
                view.add_regions(ansi_scope, ansi_regions, ansi_scope, '', sublime.DRAW_NO_OUTLINE)

        # removing the rest of  ansi escape codes
        ansi_codes = view.find_all(r'(\x1b\[[\d;]*m){1,}')
        ansi_codes.reverse()
        for r in ansi_codes:
            view.erase(edit, r)
        view.set_read_only(True)

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

