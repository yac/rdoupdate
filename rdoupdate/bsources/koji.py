from rdoupdate.bsource import BuildSource
from rdoupdate.errpass import ErrorBool
from rdoupdate.utils.cmd import run

class KojiSource(BuildSource):
    name = 'koji'

    def _download_build(self, build):
        run('koji', 'download-build', build.id)

    def _build_available(self, build):
        o = run('koji', 'buildinfo', build.id, fatal=False)
        if not o.success:
            return ErrorBool(err=o)
        if o.find("COMPLETE") == -1:
            return ErrorBool(err="Build not complete.")
        return ErrorBool()
