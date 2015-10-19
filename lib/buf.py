from sublime import set_timeout
from .util import log

class WriteBuffer(object):
    def __init__(self, flush=lambda txt: None, timeout=30, size=512):
        self.buf = ''
        self.raw_flush = flush
        self.timeout = timeout
        self.size = size
        self.running = False

    def begin(self):
        # log('+++begin')
        self.running = True

    def end(self):
        self.running = False

    def run(self):
        if self.buf == '':
            return
        if self.running:
            return
        self.begin()
        set_timeout(self.flush, self.timeout)

    def clean(self):
        self.buf = ''

    def flush(self):
        if self.buf == '':
            return
        # log('+++flush', len(self.buf))
        buf = self.buf
        self.buf = ''
        self.raw_flush(buf)
        # log('+++end')
        self.end()

    def write(self, text):
        # log('+++write', len(self.buf))
        self.buf += text
        if len(self.buf) > self.size:
            self.flush()
        self.run()

