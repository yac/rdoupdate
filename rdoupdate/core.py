# -*- encoding: utf-8 -*-
import yaml

import const
import exception
import os.path


class UpdateObject(object):
    """
    Abstract class providing initialization from and export to dict.
    """
    name = 'config'
    required_attrs = []
    optional_attrs = []
    attr_defaults = {}

    def __init__(self, *args, **kwargs):
        """
        Pass either kwargs specified by self.(required|optional)_attrs or
        a dictionary with them.
        """
        if args:
            if len(args) != 1:
                raise exception.Bug(dafuq="Invalid constructor usage")
            data = args[0]
        else:
            data = kwargs
        self.load_dict(data)

    def _set_attr_from_dict(self, data, attr, required=True):
        if not attr in data:
            if required:
                raise exception.InvalidUpdateStructure(
                    msg="%s is missing argument: %s" % (self.name, attr))
            val = self.attr_defaults.get(attr)
        else:
            val = data[attr]
        if required and not val:
            raise exception.InvalidUpdateStructure(
                msg="%s argument not set: %s" % (self.name, attr))
        setattr(self, attr, val)

    def load_dict(self, data):
        for attr in self.required_attrs:
            self._set_attr_from_dict(data, attr)
        for attr in self.optional_attrs:
            self._set_attr_from_dict(data, attr, required=False)

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.as_dict())


class Build(UpdateObject):
    name = 'build'
    required_attrs = ['id', 'repo', 'dist']
    optional_attrs = ['tag', 'source']
    attr_defaults = {'source': const.DEFAULT_BUILD_SOURCE}

    def load_dict(self, data):
        UpdateObject.load_dict(self, data)
        if self.source and self.source not in const.BUILD_SOURCES:
            raise exception.InvalidUpdateStructure(
                msg="Invalid build source: %s (valid: %s)" %
                    (self.source, " ".join(const.BUILD_SOURCES)))

    def __str__(self):
        s = '%s -> %s / %s' % (self.id, self.repo, self.dist)
        if self.tag:
            s += ' [%s]' % self.tag
        return s


class Update(UpdateObject):
    name = 'update'
    required_attrs = ['builds']
    optional_attrs = ['comment']

    def load_dict(self, data):
        super(Update, self).load_dict(data)
        def _buildize(b):
            if isinstance(b, Build):
                return b
            return Build(b)
        self.builds = map(_buildize, self.builds)

    def as_dict(self):
        d = super(Update, self).as_dict()
        d['builds'] = map(lambda x: x.as_dict(), d['builds'])
        return d

    def update_file(self, hints=True):
        s = '---\n'
        if self.comment:
            s += yaml.dump({'comment': self.comment})
        else:
            if hints:
                s += """## You may add a comment describing this update, for example:
#comment: |
#         Description of this mighty update
#         with "quotes" and stuff.
"""
        s += 'builds:\n'
        for b in self.builds:
            s += '   - id: %s\n     repo: %s\n     dist: %s\n' % (b.id, b.repo,
                                                                  b.dist)
        if hints:
            s += """## You can add more builds here like this:
#   - id: python-awesomepackage-3.14-1.el6
#     repo: havana
#     dist: epel-6
#
## Commented lines will be deleted
"""
        return s

    def summary(self):
        s = "\n".join(map(str, self.builds))
        if self.comment:
            s += "\n---\n%s" % self.comment
        return s

    def __str__(self):
        return self.summary()


def pp_update(path):
    pretty = os.path.splitext(path)[0]
    if pretty.startswith('updates/'):
        pretty = pretty[8:]
    return pretty