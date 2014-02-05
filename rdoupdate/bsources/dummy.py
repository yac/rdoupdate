import os.path
from rdoupdate.bsource import BuildSource
from rdoupdate.utils.cmd import run
from rdoupdate.exception import FileExists


def touch(f):
    if os.path.exists(f):
        raise FileExists(path=f)
    run('touch', f)

class DummyFetcher(BuildSource):
    name = 'dummy'

    def _download_build(self, build_id):
        touch('%s.dummy.rpm' % build_id)
        touch('%s.dummy.src.rpm' % build_id)

    def _build_available(self, build_id):
        return True
