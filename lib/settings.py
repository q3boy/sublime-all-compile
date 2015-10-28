import sublime
import os
import re

from .error import ACTypeNotFound, ACCommandModeNotFound, ACCommandNotFound, ACSettingsError, ACCommandNotDefined
from .util import log, getpath, dump
from tempfile import NamedTemporaryFile


def extends(child, parent):
    new = dict()
    for key, val in parent.items():
        cld = child.get(key)
        if cld == None:
            new[key] = val
        elif isinstance(cld, dict) and isinstance(val, dict):
            new[key] = extends(cld, val)
        else:
            new[key] = cld

    for key, val in child.items():
        if parent.get(key) == None:
            new[key] = val
    return new

def src_type(view):
    log('src_type', view.scope_name(0))
    return [src.strip(', \t') for src in view.scope_name(0).split(' ')]


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

def get_by_name(name, list):
    if not name:
        return None
    for item in list:
        if name == item.get('name'):
            return item
    return None

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
        settings = None
        name = ''
        found = False
        compilers = self.settings.get('compilers')
        cpl_dict = dict()
        for settings in compilers:
            name = settings.get('name')
            cpl_dict[name] = settings.copy()
            del cpl_dict[name]['name']
        for name, settings in cpl_dict.items():
            # pass
            while settings.get('extend') and cpl_dict.get(settings.get('extend')):
                extend = settings.get('extend')
                del settings['extend']
                settings = extends(settings, cpl_dict.get(extend))
            cpl_dict[name] = settings
        for settings in compilers:
            name = settings.get('name')
            settings = cpl_dict.get(name)
            srcbox = settings.get('source')
            extbox = settings.get('extname')
            if not srcbox and not extbox:
                continue
            if src:
                for s in src:
                    if srcbox.count(s) > 0:
                        found = True
                        log('found type by source', srcbox, src)
                        break
            if ext and extbox.count(ext) > 0:
                found = True
                log('found type by extname', extbox, ext)
                break
            if found:
                break
        if found == False:
            log('found nothing', src, ext)
            return None, {}, src, ext
        log('found type', name)
        dump(settings)
        return name, settings, src, ext

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
