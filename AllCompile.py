import sublime, sublime_plugin


from .lib.compile import Compile
from .lib.util import log


AC_DICT = {}

def getac(wid, view):
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

    def compile(self, execute=False):
        # print(run)
        self.last_compile = Compile(self.view).compile(execute)



    # def show_panel(self, edit):
    #     if self.last_compile:
    #         self.last_compile.


class AllCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit, execute=False):
        wid = self.view.window().id()
        log('window id', wid)
        ac_inst = getac(wid, self.view)
        log('allcompile instance', ac_inst)
        ac_inst.compile(execute)

# from .lib.exec import Process

# from .lib.settings import Settings

# print(Process)
# import os
# import subprocess
# from threading import Thread


# settings = Settings()
# from time import sleep

# def exec(message=''):
#     process = subprocess.Popen(
#         ['ls'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
#         )
#     output, error = process.communicate(message)
#     if output:
#         output = output.decode('utf8')
#         output = output.strip()
#     return (output, error)

# def ls():
#     sleep(3)
#     print(5)
# def ls1():
#     sleep(2)
#     print(2)
# threads = []
# threads.append(threading.Thread(target=ls))
# threads.append(threading.Thread(target=ls1))

# for t in threads:
#     t.setDaemon(True)
#     t.start()
#
#
#

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




        # print(123)
        # region = self.view.sel()[0]
        # print(self.view.settings().get('syntax'))
        # print(settings.get(self.view))
        # panel = CompilePanel(self.view)
        # panel.compile()


