import helpers


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

    def download_build(self, build_id, path=None):
        with helpers.cdir(path):
            self._download_build(build_id)

    def build_available(self, build_id):
        return self._build_available(build_id)

    def _download_build(self, build_id):
        raise NotImplementedError

    def _build_available(self, build_id):
        raise NotImplementedError