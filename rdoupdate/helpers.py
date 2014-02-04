import contextlib
import exception
import os

from utils import log


def print_list(l, nl_before=False, nl_after=False):
    if nl_before:
        log.info("")
    for e in l:
        log.info("- %s" % e)
    if nl_after:
        log.info("")


def ensure_dir(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise exception.NotADirectory(path=path)
    else:
        os.makedirs(path)


@contextlib.contextmanager
def cdir(path):
    if not path or path == '.':
        yield
        return
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)
