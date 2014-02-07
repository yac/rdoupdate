import os.path
from rdoupdate.bsource import BuildSource
from rdoupdate.errpass import ErrorBool
from rdoupdate.utils.cmd import run
from rdoupdate.exception import FileExists


def touch(f):
    if os.path.exists(f):
        raise FileExists(path=f)
    run('touch', f)

class DummySource(BuildSource):
    name = 'dummy'

    def _download_build(self, build):
        touch('%s.dummy.rpm' % build.id)
        touch('%s.dummy.src.rpm' % build.id)

    def _build_available(self, build):
        return ErrorBool()
