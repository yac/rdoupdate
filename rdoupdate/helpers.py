import contextlib
import os

from utils import log


def print_list(l, nl_before=False, nl_after=False):
    if nl_before:
        log.info("")
    for e in l:
        log.info("- %s" % e)
    if nl_after:
        log.info("")


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
