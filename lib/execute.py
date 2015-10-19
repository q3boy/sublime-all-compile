import signal
import sublime
import subprocess
import os
import re

from threading import Thread
from contextlib import contextmanager
from .util import log, defer



class Dir(object):
    @classmethod
    @contextmanager
    def cd(cls, newdir):
        prevdir = os.getcwd()
        os.chdir(newdir)
        try:
            yield
        finally:
            os.chdir(prevdir)

class ProcessCache(object):
    _procs = []

    @classmethod
    def add(cls, process):
        log("add to cache", process.last_cmd)
        cls._procs.append(process)

    @classmethod
    def remove(cls, process):
        log("remove from cache", process.last_cmd)
        if process in cls._procs:
            cls._procs.remove(process)

    @classmethod
    def kill_all(cls):
        cls.each(lambda process: process.kill())
        cls.clear()

    @classmethod
    def each(cls, fn):
        for process in cls._procs:
            fn(process)

    @classmethod
    def empty(cls):
        return len(cls._procs) == 0

    @classmethod
    def clear(cls):
        del cls._procs[:]


class Process(object):
    def __init__(self, path=None, working_dir=None, mode_name=None, nonblocking=True):
        self.mode_name = mode_name
        self.working_dir = working_dir
        self.nonblocking = nonblocking
        self.path = path
        self.last_cmd = ""
        self.failed = False
        self.env = os.environ.copy()
        self.process = None
        self.rcode = 0
        if path:
            self.env['PATH'] = path


    def run(self, cmd):
        with Dir.cd(self.working_dir):
            self.process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=self.env, shell=True)

        self.last_cmd = cmd
        ProcessCache.add(self)
        return self

    def communicate(self, inputs=None, func=lambda x: None):
        self.pipe(func)

        if inputs:
            self.process.stdin.write(inputs)
            try:
                self.process.stdin.close()
            except BrokenPipeError:
                pass
        self.process.wait()
        self.terminate()
        # log('returncode', self.returncode())
        self.rcode = self.returncode()


    def pipe(self, func):
        thread = Thread(target=lambda: self._pipe_stream(self.process.stdout, func))
        thread.start()

    def _pipe_stream(self, stream, func):
        while True:
            line = stream.readline()
            if not line:
                sublime.set_timeout(lambda: func(final=True, rcode=self.rcode, mode=self.mode_name), 100)
                log('return code', self.rcode)
                break
            line = line.rstrip()
            output_line = line.decode('utf-8')
            output_line = re.sub(r'\033\[(\d{1,2}m|\d\w)', '', str(output_line))
            output_line = output_line.replace('\r', '')
            output_line += "\n"
            func(output_line)

    def terminate(self):
        if self.is_alive():
            self.process.terminate()
        ProcessCache.remove(self)

    def is_alive(self):
        return self.process.poll() is None

    def returncode(self):
        return self.process.returncode

    def kill(self):
        pid = self.process.pid
        log('kill', pid)
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
        finally:
            ProcessCache.remove(self)



