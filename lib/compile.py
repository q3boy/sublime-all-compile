import os
from .panel import Editor, OutputPanel
from .execute import Process
from .settings import Settings
from .util import log, defer
from .error import ACError
from threading import Thread


class Compile(OutputPanel):
    PANEL_NAME = 'allcompile_output'

    def __init__(self, view):
        self.view = view

        self.editor = Editor(view)
        self.region = self.editor.has_selected_text()
        self.tmpfile = None
        self.last_process = None
        self.running = False
        super(Compile, self).__init__(view.window(), self.PANEL_NAME)

    def error(self, error):
        self.show()
        self.set_syntax_file('Packages/Markdown/Markdown.tmLanguage')
        self.write(str(error))

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

    def compile(self, mode):
        self.running = True
        # get settings
        try:
            syntax, cmd, stdio, path, working_dir, tmpfile, region = \
                Settings().get(self.view, mode, self.region)
        except Exception as error:
            self.error(error)
            self.final(None)
            return
        codes = self.editor.get_text() if region else self.editor.get_all_text()
        # show panel
        self.set_syntax_file(syntax)
        self.show()
        codes = codes.encode()
        self.tmpfile = tmpfile
        # write tmpfile
        if tmpfile:
            log('write tmpfile', tmpfile.name)
            tmpfile.write(codes)
            tmpfile.close()
        # thread for execute
        def func():
            log("new thread", cmd)
            try:
                # run sub process
                self.last_process = Process(working_dir=working_dir, path=path, mode_name=mode)
                self.last_process.run(cmd)
                if stdio:
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

