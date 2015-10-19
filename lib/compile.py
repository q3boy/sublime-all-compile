import os

from .panel import Editor, OutputPanel, OutputTab
from .execute import Process
from .settings import Settings
from .util import log, defer
from .error import ACError
from threading import Thread


class Compile(object):
    PANEL_NAME = 'allcompile_output'

    def __init__(self):
        self.tmpfile = None
        self.last_process = None
        self.running = False
        self.tab = None
        self.panel = None
        # self.panel = OutputPanel(view.window(), self.PANEL_NAME)
        # self.panel = OutputTab(view.window())
        self.output = None


    def write(self, text=None, final=False, rcode=0, mode=None):
        if final:
            self.output.write('\n--------------------\n%s %s\n' % (mode, "done" if rcode == 0 else "FAIL"))
        else:
            self.output.write(text)

    def error(self, error):
        panel = self.output
        if not panel.show():
            self.final(self.tmpfile)
            return
        panel.set_syntax_file('Packages/Markdown/Markdown.tmLanguage')
        panel.write(str(error))

    def kill(self):
        self.last_process.kill()
        if self.tmpfile:
            try:
                os.unlink(self.tmpfile.name)
            except Exception:
                pass
    def final(self, tmpfile):
        if tmpfile:
            log('delete tmpfile', tmpfile.name)
            os.unlink(tmpfile.name)
            self.tmpfile = None
        log("all done")
        self.running = False


    def clean_panel(self):
        if self.panel:
            self.panel.clean()
        if self.tab:
            self.tab.clean()

    def get_panel(self, window, tab=False):
        if tab:
            self.output = self.tab or OutputTab(window)
            self.tab = self.output
        else:
            self.output = self.panel or OutputPanel(window, self.PANEL_NAME)
            self.panel = self.output
        return self.output

    def compile(self, view, mode):
        self.running = True

        editor = Editor(view)
        region = editor.has_selected_text()

        # get settings
        try:
            settings, region, tmpfile = Settings().get(view, mode, region)

            # syntax, cmd, stdio, path, working_dir, tmpfile, region, ftype = \
                # Settings().get(self.view, mode, region)
        except Exception as error:
            self.error(error)
            self.final(tmpfile)
            return
        codes = editor.get_text() if region else editor.get_all_text()

        panel = self.get_panel(view.window(), tab=True)
        # show panel
        if not panel.show():
            self.final(tmpfile)
            return
        panel.set_name(mode, settings.get('type'))
        panel.clean()
        # syntax
        panel.set_syntax_file(settings.get('syntax'))
        log('set syntax', settings.get('syntax'))

        codes = codes.encode()
        self.tmpfile = tmpfile
        # write tmpfile
        if tmpfile:
            log('write tmpfile', tmpfile.name)
            tmpfile.write(codes)
            tmpfile.close()
        # thread for execute
        def func():
            log("new thread", settings.get('cmd'))
            try:
                # run sub process
                self.last_process = Process( \
                    working_dir=settings.get('working_dir'), path=settings.get('path'), mode_name=mode)
                self.last_process.run(settings.get('cmd'))
                if settings.get('stdio'):
                    self.last_process.communicate(inputs=codes, func=self.write)

                else:
                    self.last_process.communicate(func=self.write)
            except Exception as error:
                self.error(error)
            finally:
                self.final(tmpfile)
        # start thread
        Thread(target=func).start()
        return self

