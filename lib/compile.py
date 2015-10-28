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
        self.last_mode = None
        self.last_process = None
        self.running = False
        self.tab = None
        self.panel = None
        self.output = None
        self.ansi = False


    def write(self, text=None, final=False, rcode=0, mode=None):
        if final:
            self.output.write('\n--------------------\n%s %s\n' % (mode, "done" if rcode == 0 else "FAIL"))
            if self.ansi:
                self.output.ansi()
                self.ansi = False
        else:
            self.output.write(text)

    def error(self, error, tmpfile=None):
        panel = self.output
        if not panel.show():
            self.final(self.tmpfile)
            return
        panel.clean()
        panel.set_syntax_file('Packages/Markdown/Markdown.tmLanguage')
        panel.write(str(error))
        self.final(tmpfile)

    def kill(self):
        self.last_process.kill()
        if self.tmpfile:
            try:
                os.unlink(self.tmpfile.name)
            except Exception:
                pass
    def final(self, tmpfile=None):
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

    def thread(self, settings, mode, codes, tmpfile):
        log("new thread", settings.get('cmd'))
        try:
            # run sub process
            self.last_process = Process(working_dir=settings.get('working_dir'), \
                path=settings.get('path'), mode_name=mode, ansi=settings.get('ansi'))
            self.last_process.run(settings.get('cmd'))
            if settings.get('stdio'):
                self.last_process.communicate(inputs=codes, func=self.write)

            else:
                self.last_process.communicate(func=self.write)
        except Exception as error:
            self.error(error, tmpfile)
        finally:
            self.final(tmpfile)

    def compile(self, view, mode):
        self.running = True
        self.last_mode = mode

        editor = Editor(view)
        region = editor.has_selected_text()
        tmpfile = None

        # get settings
        try:
            settings, tmpfile, region = Settings().get(view, mode, region)
        except Exception as error:
            self.get_panel(view.window())
            self.error(error, tmpfile or None)
            return
        # compile codes
        try:
            ansi = settings.get('ansi')
            self.ansi = ansi
            codes = editor.get_text() if region else editor.get_all_text()
            panel = self.get_panel(view.window(), tab=settings.get('tab'))
            # show panel
            if not panel.show():
                self.final(tmpfile)
                return
            panel.set_name(mode, settings.get('type'))
            panel.clean()
            # syntax
            if not ansi:
                panel.set_syntax_file(settings.get('syntax'))
                log('set syntax', settings.get('syntax'))

            codes = codes.encode()
            self.tmpfile = tmpfile
            # write tmpfile
            if tmpfile and tmpfile.name:
                log('write tmpfile', tmpfile.name)
                tmpfile.write(codes)
                tmpfile.close()
            # run thread
            Thread(target=lambda: self.thread(settings, mode, codes, tmpfile)).start()
        except Exception as error:
            raise error
        finally:
            self.final(tmpfile)

        return self

