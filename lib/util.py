import sublime
import sys
import os
from operator import concat

DEBUG=True

def log(*args):
    if DEBUG:
        sys.stdout.write("---CoffeeCompile--- ")
        print(args)

def defer(func = lambda : None):
    sublime.set_timeout(func, 0)

def getenv():
    path = os.environ.get('PATH', '').split(os.pathsep)
    path = concat(sublime.load_settings("AllCompile.sublime-settings").get('path'), path)
    return {'PATH' : os.pathsep.join(path)}
