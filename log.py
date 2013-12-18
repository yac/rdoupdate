import logging
from terminal import Terminal


INFO = logging.INFO
# between info and debug
VERBOSE = (logging.INFO + logging.DEBUG) / 2
DEBUG = logging.DEBUG

formatter = logging.Formatter(fmt='%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log = logging.getLogger('rdopkg')
log.setLevel(logging.INFO)
log.addHandler(handler)


class LogTerminal(Terminal):
    @property
    def warn(self):
        return self.yellow

    @property
    def important(self):
        return self.yellow_bold

    @property
    def error(self):
        return self.red

    @property
    def cmd(self):
        return self.cyan


term = LogTerminal()


def error(*args, **kwargs):
    log.error(*args, **kwargs)


def warn(*args, **kwargs):
    log.warning(*args, **kwargs)


def info(*args, **kwargs):
    log.info(*args, **kwargs)


def verbose(*args, **kwargs):
    log.log(VERBOSE, *args, **kwargs)


def debug(*args, **kwargs):
    log.debug(*args, **kwargs)


def command(*args, **kwargs):
    log.info(*args, **kwargs)
