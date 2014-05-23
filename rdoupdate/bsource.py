import exception
import helpers
import os
import re

from utils import log


class BuildSourceMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'sources'):
            cls.sources = {}
        else:
            cls.sources[cls.name] = cls


class BuildSource(object):
    """
    Subclass this to create a builds source.

    Provide:
      * `name` attribute
      * `_download_build()` function
      * `_build_available()` function
    """
    __metaclass__ = BuildSourceMount

    def download_build(self, build, path=None):
        with helpers.cdir(path):
            files_before = helpers.list_files()
            self._download_build(build)
            files_after = helpers.list_files()
            files_new = files_after - files_before
            if not files_new:
                raise exception.NoBuildFilesDownloaded(build=build.id)
            self._filter_arch(build, files_new)

    def build_available(self, build):
        return self._build_available(build)

    def _download_build(self, build):
        raise NotImplementedError

    def _build_available(self, build):
        raise NotImplementedError

    def _filter_arch(self, build, files):
        if not build.arch:
            return
        archs = re.findall("[^\s,]+", build.arch)
        some_valid = False
        for f in files:
            valid = False
            for arch in archs:
                if re.search(re.escape(arch) + '(?:\.src)?\.rpm$', f):
                    valid = True
                    break
            if valid:
                some_valid = True
            else:
                log.info("Build file excluded due to arch filter: %s" % f)
                os.remove(f)
        if not some_valid:
            raise exception.AllBuildFilesExcluded(build=build.id)
