import sublime
from .error import ACTypeNotFound
def src_type(view):
    region = view.sel()[0]
    return view.scope_name(region.begin()).split(' ', maxsplit=1)[0]

def ext_name(view):
    return view.file_name().split(".")[-1]


class  Settings:
    def __init__(self):
        self.settings = sublime.load_settings("AllCompile.sublime-settings")

    def check(self, view):
        src = src_type(view)
        ext = ext_name(view)
        compilers = self.settings.get('compilers')
        for name, v in compilers.items():
            srcbox = v['source']
            extbox = v['extname']
            if srcbox.count(src) > 0:
                return name, v, src, ext
            elif extbox.count(ext) > 0:
                return name, v, src, ext
        return None, {}, src, ext

    # def format(self, settings):

    def get(self, view, execute, region):
        name, settings, src, ext = self.check(view)
        syntax = self.settings.get('syntax')

        if name == None:
            raise ACTypeNotFound(src, ext)
        stdio   = region and settings.get('region') == 'stdio'
        tmpfile = region and not stdio
        mode    = 'exec_' if execute else 'cmpl_'
        mode   += 'stdio' if stdio else 'file'
        cmd     = settings.get('cmd')[mode]

        return syntax, cmd, stdio, tmpfile



# "extname" : ["coffee"],
#       "source" : ["source.coffee"],
#       "syntax" : "Packages/JavaScript/JavaScript.tmLanguage",
#       "cmd" : {
#         "exec_file" : ["/usr/bin/env", "coffee", "$file"],
#         "cmpl_file" : ["/usr/bin/env", "coffee", "-pb", "$file"],
#         "exec_stdio" : ["/usr/bin/env", "coffee", "-s"],
#         "cmpl_stdio" : ["/usr/bin/env", "coffee", "-pbs"],
#       },
#       "parts" : "stdio"
#