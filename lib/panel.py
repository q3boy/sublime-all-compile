import sublime

from .util import log
from .buf import WriteBuffer


class OutputTab(object):
    def __init__(self, window):
        self.window = window
        self.view = None
        self.group = 1
        self.buf = WriteBuffer(flush=self.raw_write)

    def show(self):
        tab = self.view
        win = self.window
        prev = win.active_view()
        log('prev tab', prev.id(), prev.buffer_id())
        if tab:
            log('curr tab', tab.id(), tab.buffer_id())
        if tab and tab.buffer_id() > 0 and tab.id() == prev.id():
            log('skip when output tab actived')
            return False
        tab = self.create_tab()
        win.set_view_index(tab, self.group, 0)
        win.focus_view(prev)
        return True

    def clean(self):
        self.view.run_command('all_compile_tab_clean')
        self.buf.clean()

    def raw_write(self, text):
        self.view.run_command('all_compile_tab_append', {"text": str(text)})

    def write(self, text):
        self.buf.write(text)

    def set_name(self, mode, ftype):
        self.view.set_name("*AC* %s %s" % (mode, ftype))

    def set_syntax_file(self, syntax_file):
        self.view.set_syntax_file(syntax_file)

    def create_tab(self):
        self.create_group()
        log(self.view)
        if not (self.view and self.view.buffer_id() > 0):
            self.window.focus_group(self.group)
            self.view = self.window.new_file()
            log('new tab', self.view)
            self.view.set_scratch(True)
        return self.view

    def create_group(self):
        win = self.window
        prev = win.active_group()
        num = win.num_groups()
        if num > 1:
            self.group = prev + 1 if prev + 1 < num else 0
        else:
            win.set_layout({
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
            })
            self.group = 1



class OutputPanel(object):

    def __init__(self, window, name):
        self.name = "%s.%d" % (name, window.id())
        self.window = window
        log('create panel', self.name)
        self.panel = self._get_or_create_panel(self.name)
        self.buf = WriteBuffer(flush=self.raw_write)


    def show(self):
        log('show panel', self.name)
        self.window.run_command('show_panel', {'panel': "output.%s" % self.name})

    def lock(self):
        self.panel.set_read_only(True)

    def unlock(self):
        self.panel.set_read_only(False)

    def write(self, text):
        self.buf.write(text)

    def raw_write(self, text):
        self.unlock()
        self.panel.run_command('append', {'characters': text})
        self.lock()

    def set_syntax_file(self, syntax_file):
        self.panel.set_syntax_file(syntax_file)

    def clean(self):
        self.buf.clean()
        self.panel = self.window.create_output_panel(self.name)

    def set_name(self, mode, type):
        return

    def _get_or_create_panel(self, name):
        try:
            return self.window.get_output_panel(name)
        except AttributeError:
            log("Couldn't get output panel.")
            return self.window.create_output_panel(name)


class Editor(object):
    def __init__(self, view):
        self.view = view

    def get_text(self):
        return self.get_selected_text() or self.get_all_text()

    def has_selected_text(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False

    def get_selected_text(self):
        if not self.has_selected_text():
            return None
        return self.view.substr(self.view.sel()[0])

    def get_all_text(self):
        return self.view.substr(sublime.Region(0, self.view.size()))




