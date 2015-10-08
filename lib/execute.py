import signal, subprocess
import os
import re

from threading import Thread
from contextlib import contextmanager

class Dir():
    @classmethod
    @contextmanager
    def cd(cls, newdir):
        prevdir = os.getcwd()
        os.chdir(newdir)
        try:
            yield
        finally:
            os.chdir(prevdir)

class ThreadWithResult(Thread):
    def __init__(self, target, args):
        self.result = None
        self.target = target
        self.args = args
        Thread.__init__(self)
        self.start()

    def run(self):
        self.result = self.target(*self.args)

class ProcessCache():
    _procs = []

    @classmethod
    def add(cls, process):
        print("add to cache")
        cls._procs.append(process)

    @classmethod
    def remove(cls, process):
        print("remove from cache")
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


class Process():
    def __init__(self, path=None, working_dir=None, nonblocking=True):
        self.working_dir = working_dir
        self.nonblocking = nonblocking
        self.path = path
        self.last_command = ""
        self.failed = False
        self.env = os.environ.copy()
        if path:
            self.env['PATH'] = path


    def run(self, command):
        with Dir.cd(self.working_dir):
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env, shell=True, preexec_fn=os.setsid)

        self.last_command = command
        print("++++ add", self.last_command, ' to cache')
        ProcessCache.add(self)
        return self

    def run_sync(self, command):

        with Dir.cd(self.working_dir):
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env, shell=True)
            (stdout, stderr) = self.process.communicate()
            self.failed = self.process.returncode == 127 or stderr

        return (stdout.decode('utf-8'), stderr.decode('utf-8'))


    def communicate(self, input=None, fn = lambda x:None):
        stdout, stderr = self.pipe(fn)
        self.process.communicate(input)
        self.terminate()
        return (stdout, stderr)

    def pipe(self, fn):
        streams = [self.process.stdout, self.process.stderr]
        streams_text = []
        if self.nonblocking:
            threads = [ThreadWithResult(target=self._pipe_stream, args=(stream, fn)) for stream in streams]
            [t.join() for t in threads]
            streams_text = [t.result for t in threads]
        else:
            streams_text = [self._pipe_stream(stream, fn) for stream in streams]
        return streams_text

    def _pipe_stream(self, stream, fn):
        output_text = ""
        while True:
            line = stream.readline()
            if not line: break
            line = line.rstrip()
            output_line = line.decode('utf-8')
            output_line = re.sub(r'\033\[(\d{1,2}m|\d\w)', '', str(output_line))
            output_line += "\n"
            output_text += output_line
            fn(output_line)
        return output_text

    def terminate(self):
        if self.is_alive():
            self.process.terminate()
        print("---- del", self.last_command, ' from cache')
        ProcessCache.remove(self)

    def is_alive(self):
        return self.process.poll() is None

    def returncode(self):
        return self.process.returncode

    def kill(self):
        pid = self.process.pid
        os.killpg(pid, signal.SIGTERM)
        print("---- del", self.last_command, ' from cache')
        ProcessCache.remove(self)



