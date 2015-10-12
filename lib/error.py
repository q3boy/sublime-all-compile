import os
from .util import getpath

class ACError(Exception):
    def __init__(self, code, msg="", path=None):
        self.path = path or getpath().split(os.pathsep)
        self.code = code
        self.msg = msg

    def __str__(self):
        output = """
AllCompile Error: %s
====================================""" % self.code

        if self.msg != "":
            output += """
Message
------------------------------------
    %s""" % "\n    ".join(self.msg.split("\n"))
        if len(self.path) > 0:
            output += """
Path
------------------------------------
    %s""" % "\n    ".join(self.path)
        return output


class ACTypeNotFound(ACError):
    def __init__(self, src, ext):
        code = "Type not Found"
        msg = "source: %s\n" % src
        msg += "extname: %s\n" % ext
        super().__init__(code, msg)

class ACCommandNotFound(ACError):
    def __init__(self, type):
        code = "Command not Found"
        msg = "type: %s\n" % type
        super().__init__(code, msg)

class ACCommandModeNotFound(ACError):
    def __init__(self, type, mode):
        code = "Command Mode not Found"
        msg = "type: %s\n" % type
        msg = "mode: %s\n" % mode
        super().__init__(code, msg)


class ACSettingsError(ACError):
    def __init__(self, path):
        code = "Settings Error"
        msg = "path: %s\n" % type
        super().__init__(code, msg)

class ACCommandNotDefined(ACError):
    def __init__(self):
        code = "Command not Defined"
        msg = "both file and stdio command not defined."
        super().__init__(code, msg)

