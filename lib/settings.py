import sublime
import os
import re

from .error import ACTypeNotFound, ACCommandModeNotFound, ACCommandNotFound, ACSettingsError, ACCommandNotDefined
from .util import log, getpath
from tempfile import NamedTemporaryFile

def src_type(view):
    log('src_type', view.scope_name(0))
    return view.scope_name(0)

def ext_name(view):
    fname = view.file_name()
    if not fname:
        return None
    fname = fname.split('.')
    if len(fname) <= 1:
        return None
    return fname[-1]

def init_tmpfile(variables):
    tmpfile = NamedTemporaryFile(delete=False)
    variables['file'] = tmpfile.name
    variables['file_name'] = os.path.basename(tmpfile.name)
    variables['file_path'] = os.path.dirname(tmpfile.name)
    variables['ori_file'] = tmpfile.name
    variables['ori_file_name'] = os.path.basename(tmpfile.name)
    variables['ori_file_path'] = os.path.dirname(tmpfile.name)
    return tmpfile, variables


def get_cmd(cmd, variables, region):
    stdio = cmd.get('stdio')
    fcmd = cmd.get('file')
    tmpfile = None
    if not stdio and not fcmd:
        raise ACCommandNotDefined()

    # if stdio defined
    if stdio:
        # use file mode when file command defiend and not in region mode and file exists
        if fcmd and not region and variables.get('file'):
            return False, fcmd, variables, tmpfile
        # otherwise, use stdio mode
        return True, stdio, variables, tmpfile
    # if stdio not defined
    else:
        # use tmpfile when region mode or file not exists
        if region or not variables.get('file'):
            # flag.add("tmpfile")
            tmpfile, variables = init_tmpfile(variables)
            log('use tmpfile', tmpfile.name)
        # use file mode
        return False, fcmd, variables, tmpfile



def get_vars(view):
    variables = view.window().extract_variables()

    if variables.get('file'):
        variables['ori_file'] = variables.get('file')
    if variables.get('file_name'):
        variables['ori_file_name'] = variables.get('file_name')
    if variables.get('file_path'):
        variables['ori_file_path'] = variables.get('file_path')

    folder = variables.get('folder')
    file_path = variables.get('file_path')
    working_dir = folder or file_path
    return working_dir, variables

class  Settings(object):
    def __init__(self):
        self.settings = sublime.load_settings("AllCompile.sublime-settings")
        log('load settings file')

    def check(self, view):
        src = src_type(view)
        ext = ext_name(view)
        log('settings 1', src, ext)
        compilers = self.settings.get('compilers')
        for name, v in compilers.items():
            srcbox = v.get('source')
            extbox = v.get('extname')
            log('settings 2', name, srcbox, extbox)
            if not srcbox and not extbox:
                log('skip type check', name)
                log('settings 3', name, srcbox, extbox)
                continue
            if src:
                log('settings 4 src', src, srcbox)
                for reg in srcbox:
                    log('settings 6 reg', reg, src, re.match(src, reg))
                    if re.match(reg, src):
                        return name, v, src, ext
            elif ext and extbox.count(ext) > 0:
                log('settings 5 ext', ext, extbox)
                log('found type by extname', ext)
                return name, v, src, ext
        log('found nothing', src, ext)
        return None, {}, src, ext

    def get_mode(self, view):
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
        syntax = cmd.get('syntax') or settings.get('syntax')
        syntax = syntax or self.settings.get('syntax')

        # use tab mode
        tab = True if cmd.get('tab') or settings.get('tab') else False

        ansi = True if cmd.get('ansi') or settings.get('ansi') else False
        tab = True if ansi else tab

        # get path
        path = getpath(settings.get('path')) if settings.get('path') else getpath()

        # get variables
        working_dir, variables = get_vars(view)

        # get command
        stdio, cmd, variables, tmpfile = get_cmd(cmd, variables, region)
        log('get cmd: stdio %s, cmd %s, tmpfile %s' % (stdio, cmd, tmpfile))

        # replace vars in cmd
        cmd = sublime.expand_variables(cmd, variables)
        log('cmd expend variables', cmd)


        return {"syntax": syntax, "cmd": cmd, "stdio": stdio, "path": path, \
            "working_dir": working_dir, "type": name, "tab" : tab, "ansi": ansi}, tmpfile, region
