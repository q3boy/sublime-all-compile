import os
from .util import log, getenv

class ACError(Exception):
    def __init__(self, code, msg="", path=None):
        if path != None:
            self.path = path
        else:
            self.path = getenv()['PATH'].split(os.pathsep)
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
        code = "Type Node Found"
        msg = "source: %s\n" % src
        msg += "extname: %s" % ext
        super().__init__(code, msg, [])

