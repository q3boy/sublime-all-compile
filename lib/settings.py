import sublime
import os

from .error import ACTypeNotFound, ACCommandModeNotFound, ACSettingsError
from .util import log, getpath
from tempfile import NamedTemporaryFile

def src_type(view):
    # region = view.sel()[0]
    return view.scope_name(0).split(' ', maxsplit=1)[0]

def ext_name(view):
    return view.file_name().split(".")[-1]


def get_cmd(cmd, region):
    stdio = cmd.get('stdio')
    fcmd = cmd.get('file')


    if (region and stdio) or (not region and not fcmd):
        cmd = stdio
        stdio = True
    else:
        cmd = fcmd
        stdio = False

    return cmd, stdio

def get_vars(tmpfile, view):
    variables = view.window().extract_variables()
    if tmpfile or not variables.get('file'):
        tmpfile = NamedTemporaryFile(delete=False)
        variables['file'] = tmpfile.name
        variables['file_name'] = os.path.basename(tmpfile.name)
        variables['file_path'] = os.path.dirname(tmpfile.name)

    folder = variables.get('folder')
    file_path = variables.get('file_path')
    working_dir = folder or file_path
    return tmpfile, working_dir, variables

class  Settings(object):
    def __init__(self):
        self.settings = sublime.load_settings("AllCompile.sublime-settings")
        log('load settings file')

    def check(self, view):
        src = src_type(view)
        ext = ext_name(view)
        compilers = self.settings.get('compilers')
        for name, v in compilers.items():
            try :
                srcbox = v.get('source')
                extbox = v.get('extname')
                if srcbox.count(src) > 0:
                    log('found type by source', src)
                    return name, v, src, ext
                elif extbox.count(ext) > 0:
                    log('found type by extname', ext)
                    return name, v, src, ext
            except Exception:
                log('skip type check', name)
        log('found nothing', src, ext)
        return None, {}, src, ext

    def getMode(self, view):
        # get type settings
        name, settings, src, ext = self.check(view)
        # check type
        if name == None:
            raise ACTypeNotFound(src, ext)
        # check command
        cmd = settings.get('cmd')
        if not cmd:
            raise ACCommandNotFound(name)
        return list(cmd)


    def get(self, view, mode, region):
        # get type settings
        name, settings, src, ext = self.check(view)
        # check type
        if name == None:
            raise ACTypeNotFound(src, ext)
        # check command
        cmd = settings.get('cmd').get(mode)
        if not cmd:
            raise ACCommandModeNotFound(name, mode)

        # if no_region isset disable region mode
        region = False if cmd.get('no_region') else region

        # use default syntax
        syntax = settings.get('syntax') or self.settings.get('syntax')
        # get command
        cmd, stdio = get_cmd(cmd, region)
        # get path
        path = getpath(settings.get('path')) if settings.get('path') else getpath()
        # only use tmpfile when region mode and stdio not defined
        tmpfile = None

        if region and not stdio:
            tmpfile = True

        log('init tmpfile', tmpfile)
        # get variables
        tmpfile, working_dir, variables = get_vars(tmpfile, view)
        stdio = not tmpfile
        # replace vars in cmd
        cmd = sublime.expand_variables(cmd, variables)


        return syntax, cmd, stdio, path, working_dir, tmpfile, region
