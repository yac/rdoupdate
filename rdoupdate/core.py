# -*- encoding: utf-8 -*-

import exception


VERSION = '0.1'


class UpdateObject(object):
    """
    Abstract class providing initialization from and export to dict.
    """
    name = 'config'
    required_attrs = []
    optional_attrs = []

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
            val = None
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


class Update(UpdateObject):
    name = 'update'
    required_attrs = ['builds']
    optional_attrs = ['comment']

    def load_dict(self, data):
        super(Update, self).load_dict(data)
        self.builds = map(Build, self.builds)

    def as_dict(self):
        d = super(Update, self).as_dict()
        d['builds'] = map(lambda x: x.as_dict(), d['builds'])
        return d

    def summary(self):
        s = "\n".join(map(lambda b: '%s -> %s / %s' % (b.id, b.repo, b.dist), self.builds))
        if self.comment:
            s += "\n---\n%s" % self.comment
        return s

    def __str__(self):
        return self.summary()
