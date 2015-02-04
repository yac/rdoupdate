import urlgrabber
import urlgrabber.progress

from rdoupdate.bsource import BuildSource
from rdoupdate.errpass import ErrorBool
from rdoupdate.utils import exception
from rdoupdate.utils.cmd import run

KOJI_AVAILABLE = False
try:
    import koji
    KOJI_AVAILABLE = True
except ImportError:
    pass


KOJI_HUB_URL = 'http://koji.fedoraproject.org/kojihub'
KOJI_BASE_URL = 'http://kojipkgs.fedoraproject.org/work/'



class KojiSource(BuildSource):
    name = 'koji'
    tool = 'koji'
    args = []

    def koji(self, *kojicmd, **kwargs):
        cmd = [self.tool] + self.args + list(kojicmd)
        return run(*cmd, **kwargs)

    def _download_build(self, build):
        self.koji('download-build', build.id)

    def _build_available(self, build):
        o = self.koji('buildinfo', build.id, fatal=False)
        if not o.success:
            return ErrorBool(err=o)
        if o.find("COMPLETE") == -1:
            return ErrorBool(err="Build not complete.")
        return ErrorBool()


class KojiScratchSource(BuildSource):
    name = 'koji-scratch'

    def __init__(self):
        if not KOJI_AVAILABLE:
            raise exception.KojiModuleNotAvailable()
        self._kojics = None

    @property
    def kojics(self):
        if self._kojics is None:
            self._kojics = koji.ClientSession(KOJI_HUB_URL)
        return self._kojics

    def _get_tasks(self, build):
        try:
            task_id = int(build.id)
        except TypeError:
            return ErrorBool(err='Not an integer task ID: %s' % build.id)
        try:
            task = self.kojics.getTaskInfo(task_id, request=True)
        except Exception as ex:
            return ErrorBool(
                err='Error getting task info: %s' % ex)
        if not task:
            # just to be sure...
            return ErrorBool(
                err='Koji returned no rows.')
        elif task.get('state') in (koji.TASK_STATES['FREE'],
                                   koji.TASK_STATES['OPEN']):
            return ErrorBool('Task %i has not completed' % task_id)
        elif task.get('state') != koji.TASK_STATES['CLOSED']:
            return ErrorBool(
                err='Task %i did not complete successfully' % task_id)

        method = task.get('method')
        if method not in ('build', 'buildArch'):
            return ErrorBool(
                err='Task %i is not a build or buildArch task (%s)' %
                    (task_id, method))
        if method == 'build':
            tasks = self.kojics.listTasks(opts={
                'parent': task_id,
                'method': 'buildArch',
                'state': [koji.TASK_STATES['CLOSED']],
                'decode': True})
            if not tasks:
                return ErrorBool(
                    err='build task %i returned no buildArch tasks.' % task_id)
        else:
            tasks = [task]
        return tasks

    def _download_build(self, build):
        tasks = self._get_tasks(build)
        if not tasks:
            # contains ErrorBool(err=...) on failure
            return tasks
        prog_meter = urlgrabber.progress.TextMeter()
        for task in tasks:
            base_path = koji.pathinfo.taskrelpath(task['id'])
            output = self.kojics.listTaskOutput(task['id'])
            for filename in output:
                if not filename.endswith('.rpm'):
                    continue
                urlgrabber.urlgrab(
                    KOJI_BASE_URL + base_path + '/' + filename,
                    progress_obj=prog_meter)
        return ErrorBool()

    def _build_available(self, build):
        tasks = self._get_tasks(build)
        if tasks:
            return ErrorBool()
        # contains ErrorBool(err=...) on failure
        return tasks

