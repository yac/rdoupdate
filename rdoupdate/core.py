# -*- encoding: utf-8 -*-
import os.path
import re
import yaml

import bsource
import const
import errpass
import exception
import helpers
# plug module loads (pluggable) build sources on load
import plug
from utils import log


def pp_update(path):
    pretty = os.path.splitext(path)[0]
    if pretty.startswith('updates/'):
        pretty = pretty[8:]
    return pretty


class FillThis(unicode):
    def __new__(cls):
        return unicode.__new__(cls, u'')

    def __nonzero__(self):
        return True


FILL_THIS = FillThis()


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
        if self.source and \
           self.source not in bsource.BuildSource.sources:
            raise exception.InvalidUpdateStructure(
                msg="Invalid build source: %s (valid: %s)" %
                    (self.source, " ".join(bsource.BuildSource.sources.keys())))

    def is_available(self, verbose=False):
        if verbose:
            log.info("{t.bold}Avail. check:{t.normal} {build}".format(
                t=log.term, build=self))
        return bsrcman.build_available(self)

    def download(self):
        """
        Download build into current directory.
        """
        bsrcman.download_build(self)

    def full_id(self):
        return '%s@%s' % (self.id, self.source)

    def path(self, prefix=None):
        build_path = os.path.join(self.repo, self.dist)
        if self.tag:
            build_path = os.path.join(build_path, self.tag)
        if prefix:
            build_path = os.path.join(prefix, build_path)
        return build_path

    def match_filter(self, f):
        for attr, rex in f:
            if not hasattr(self, attr):
                return False
            a = getattr(self, attr)
            if not isinstance(attr, basestring):
                return False
            if not re.match(rex, a):
                return False
        return True

    def as_yaml_item(self):
        s = ("  - id: %s\n    source: %s\n    repo: %s\n    dist: %s" %
             (self.id, self.source, self.repo, self.dist))
        if self.tag:
            s += "\n    tag: %s" % self.tag
        return s

    def __str__(self):
        s = '%s @ %s -> %s / %s' % (self.id, self.source, self.repo, self.dist)
        if self.tag:
            s += ' [%s]' % self.tag
        return s


class Update(UpdateObject):
    name = 'update'
    required_attrs = ['builds', 'notes']
    optional_attrs = ['group']

    def load_dict(self, data):
        super(Update, self).load_dict(data)
        if self.group and \
                ('/' in self.group or '\\' in self.group):
            raise exception.InvalidUpdateStructure(
                msg="Update group can't contain slashes: %s" % self.group)
        if isinstance(self.notes, unicode):
            self.notes = self.notes.encode('utf-8')
        def _buildize(b):
            if isinstance(b, Build):
                return b
            return Build(b)
        self.builds = map(_buildize, self.builds)

    def as_dict(self):
        d = super(Update, self).as_dict()
        d['builds'] = map(lambda x: x.as_dict(), d['builds'])
        return d

    def all_builds_available(self, verbose=False):
        for b in self.builds:
            r = b.is_available(verbose=verbose)
            if not r:
                return errpass.BuildErrorBool(b, err=r.err)
        return errpass.ErrorBool()

    def update_file(self, hints=True):
        s = '---\n'
        if self.notes and self.notes != FILL_THIS:
            if self.notes.find("\n") == -1:
                s += yaml.dump({'notes': self.notes}, default_flow_style=False)
            else:
                s += "notes: |-\n  "
                s += self.notes.replace("\n", "\n  ") + "\n"
        else:
            if hints:
                s += """## Describe this update, for example:
#notes: |-
#  Description of this mighty update X.Y.Z
#  with "quotes" and stuff.
notes:
"""
        if self.group:
            s += yaml.dump({'group': self.group}, default_flow_style=False)
        s += 'builds:\n'
        for b in self.builds:
            s += b.as_yaml_item() + '\n'
        if hints:
            s += """## You can add more builds here like this:
#  - id: python-awesomepackage-3.14-1.el6
#    repo: icehouse
#    dist: epel-6
#
## Commented lines will be deleted
"""
        return s

    def download(self, out_dir=None, prefix=None, build_filter=None):
        dld_builds = []
        for build in self.builds:
            if build_filter and not build.match_filter(build_filter):
                log.info("SKIPPING: %s" % build)
                continue
            if out_dir:
                updir_path = out_dir
            else:
                updir_path = ''
            if prefix:
                updir_path = os.path.join(updir_path, prefix)
            build_path = build.path(prefix=updir_path)
            helpers.ensure_dir(build_path)
            with helpers.cdir(build_path):
                build.download()
            dld_builds.append(build)
        return dld_builds

    def get_ready_dir(self):
        return self.group or 'ready'

    def summary(self):
        s = "\n".join(map(str, self.builds))
        if self.notes:
            s += "\n---\n%s" % self.notes
        return s

    def __str__(self):
        return self.summary()


class BuildSourceManager(object):
    def __init__(self):
        self.srcs = {}

    def get_source(self, source):
        if source not in self.srcs:
            cls = bsource.BuildSource.sources.get(source)
            if not cls:
                raise exception.InvalidBuildSource(source=source)
            self.srcs[source] = cls()
        return self.srcs[source]

    def download_build(self, build):
        src = self.get_source(build.source)
        src.download_build(build)

    def build_available(self, build):
        src = self.get_source(build.source)
        return src.build_available(build)


bsrcman = BuildSourceManager()
