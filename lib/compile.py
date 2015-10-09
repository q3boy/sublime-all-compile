from .panel import Editor, OutputPanel
from .execute import Process
from .settings import Settings
from .util import log
from threading import Thread
from tempfile import TemporaryFile

# class Tempfile(object):


class Compile(object):
    PANEL_NAME = 'allcompile_output'
    def __init__(self, view):
        self.view = view
        self.window = view.window()

        editor = Editor(view)
        self.codes = editor.get_text()
        self.region = editor.has_selected_text()
        self.panel = None
        # self.create_panel()

    def create_panel(self):
        self.panel = OutputPanel(self.window, self.PANEL_NAME)


    def show(self, syntax):
        self.create_panel()
        self.panel.set_syntax_file(syntax)

    def write(self, codes):
        self.panel.display(codes)

    def error(self, error):
        self.show('Packages/Markdown/Markdown.tmLanguage')
        self.panel.display(str(error))

    def compile(self, execute=False):
        syntax, cmd, stdio, tmpfile, path, working_dir = Settings().get(self.view, execute, self.region)
        self.show(syntax)

        def func():
            p = Process(working_dir=working_dir, path=path)
            p.run(" ".join(cmd))
            stdout = p.communicate('text', self.write)
            log("end stdout", stdout)
        Thread(target=func).start()
        # log()

        # print(syntax, cmd, stdio, tmpfile)
        return syntax, cmd, stdio, tmpfile

# def pp():
#     p = Process(working_dir="/Users/q3boy/codes")
#     p.run(['./a'])
#     stdout, stderr = p.communicate('text', lambda txt: print("=========\n", txt))
#     print("stdout", stdout)
#     print("stderr", stderr)

# Thread(target = pp).start()





# class CompilePanel:
#     PANEL_NAME = 'allcompile_output'

#     def __init__(self, view):
#         self.view = view
#         self.window = view.window()
#         self.type, self.setting = sets_format(self.view)
#         self.editor = SublimeTextEditorView(self.view)
#         self.codes = self.editor.get_text()

#         self.create_panel()



#     def create_panel(self):
#         self.panel = SublimeTextOutputPanel(self.window, self.PANEL_NAME)

#     def compile(self) :
#         if self.type == TYPE_NOT_DEFINED:
#             self.error("# Type Not Defined")
#             return

#         # self.write(self.setting['syntax'])

#     def write(self, syntax):
#         # print(123)
#         if not syntax:
#             raise ValueError('missing `syntax` setting')
#         self.panel.set_syntax_file(syntax)
#         # self.panel.display(self.codes)

#     def error(self, error):
#         self.panel.set_syntax_file('Packages/Markdown/Markdown.tmLanguage')
#         self.panel.display(error)