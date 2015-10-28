import sublime
import sys
import os
import json
from operator import concat

DEBUG = False

def log(*args):
    if DEBUG:
        sys.stdout.write("---AllCompile--- ")
        print(args)

def defer(func=lambda: None):
    sublime.set_timeout(func, 0)

def getpath(path=[]):
    path = concat(path, sublime.load_settings("AllCompile.sublime-settings").get('path'))
    path = concat(path, os.environ.get('PATH', '').split(os.pathsep))
    return os.pathsep.join(path)

def dump(data):
    if DEBUG:
        print("----------AllCompile----------")
        print(json.dumps(data, indent=2))
        print("----------AllCompile----------")
