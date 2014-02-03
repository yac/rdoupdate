from rdoupdate.bsource import BuildSource
from rdoupdate.errpass import ErrorBool
from rdoupdate.utils.cmd import run

class KojiFetcher(BuildSource):
    name = 'koji'

    def _download_build(self, build_id):
        run('koji', 'download-build', build_id)

    def _build_available(self, build_id):
        o = run('koji', 'buildinfo', build_id, fatal=False)
        if o.success:
            return ErrorBool()
        else:
            return ErrorBool(err=o)
