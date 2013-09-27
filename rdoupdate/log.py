import logging


log_commands = False

INFO = logging.INFO
DEBUG = logging.DEBUG

formatter = logging.Formatter(fmt='%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log = logging.getLogger('rdoupdate')
log.setLevel(logging.INFO)
log.addHandler(handler)


def error(*args, **kwargs):
    log.error(*args, **kwargs)


def warn(*args, **kwargs):
    log.warning(*args, **kwargs)


def info(*args, **kwargs):
    log.info(*args, **kwargs)


def debug(*args, **kwargs):
    log.debug(*args, **kwargs)


def command(*args, **kwargs):
    if log_commands:
        log.info(*args, **kwargs)
