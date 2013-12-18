import exception

import codecs
import os
import re
import rpm
import time


def spec_fn(spec_dir='.'):
    specs = [f for f in os.listdir(spec_dir) \
             if os.path.isfile(f) and f.endswith('.spec')]
    if not specs:
        raise exception.SpecFileNotFound()
    if len(specs) != 1:
        raise exception.MultipleSpecFilesFound()
    return specs[0]


class Spec(object):
    """
    Lazy .spec file parser and editor.
    """
    def __init__(self, fn=None, txt=None):
        self._fn = fn
        self._txt = txt
        self._rpmspec = None

    @property
    def fn(self):
        if not self._fn:
            self._fn = spec_fn()
        return self._fn

    @property
    def txt(self):
        if not self._txt:
            self._txt = codecs.open(self.fn, 'r', encoding='utf-8').read()
        return self._txt

    @property
    def rpmspec(self):
        if not self._rpmspec:
            try:
                self._rpmspec = rpm.ts().parseSpec(self.fn)
            except ValueError, e:
                return {'error': "Error parsing '%s': %s" % (self.fn, e.args[0])}
        return self._rpmspec

    def get_tag(self, tag):
        m = re.search('^%s:\s+(\S.*)$' % tag, self.txt, flags=re.M)
        if not m:
            raise exception.SpecFileParseError(spec_fn=self.fn,
                                               error="%s tag not found" % tag)
        return m.group(1).rstrip()

    def set_tag(self, tag, value):
        self._txt = re.sub(r'^(%s:\s+).*$' % re.escape(tag),
                           r'\g<1>%s' % value, self.txt, flags=re.M)

    def get_patches_base(self):
        match = re.search(r'(?<=patches_base=)[\w\.\+]+', self.txt)
        if match is not None:
            return match.group()

    def set_patches_base(self, base):
        self._txt = re.sub(r'(#\s*patches_base\s*=\s*)[\w\.\+]+',
                           r'\g<1>%s' % base, self.txt, flags=re.M)

    def set_patches_base_version(self, version):
        base = self.get_patches_base()
        p = base.rfind('+')
        if p == -1:
            new_base = version
        else:
            new_base = "%s%s" % (version, base[p:])
        self.set_patches_base(new_base)

    def _get_release_parts(self):
        release = self.get_tag('Release')
        m = re.match('([\d.]*\d)(.*)', release)
        if not m:
            raise exception.SpecFileParseError(
                spec_fn=self.fn, error="Unable to parse Release: %s" % release)
        return m.groups()

    def reset_release(self):
        _, dist = self._get_release_parts()
        release = "1%s" % dist
        self.set_tag('Release', release)

    def bump_release(self):
        number, dist = self._get_release_parts()
        numlist = number.split('.')
        numlist[-1] = str(int(numlist[-1]) + 1)
        release = ".".join(numlist) + dist
        self.set_tag('Release', release)

    def new_changelog_entry(self, user, email, changes=[]):
        changes_str = "\n".join(map(lambda x: "- %s" % x, changes)) + "\n"
        date = time.strftime('%a %b %d %Y')
        version = self.get_tag('Version')
        release, _ = self._get_release_parts()
        # TODO: detect if there is '-' in changelog entries and use it if so
        head = "* %s %s <%s> %s-%s" % (date, user, email, version, release)
        entry = "%s\n%s\n" % (head, changes_str)
        self._txt = re.sub(r'(%changelog\n)', r'\g<1>%s' % entry, self.txt)

    def save(self):
        if not self.txt:
            # no changes
            return
        if not self.fn:
            raise exception.InvalidAction(
                "Can't save .spec file without its file name specified.")
        f = codecs.open(self.fn, 'w', encoding='utf-8')
        f.write(self.txt)
        f.close()
        self._rpmspec = None

    def get_source_urls(self):
        # arcane rpm constants, now in python!
        sources = filter(lambda x: x[2] == 1, self.rpmspec.sources)
        if len(sources) == 0:
            error = "No sources found"
            raise exception.SpecFileParseError(spec_fn=self.fn, error=error)
        # OpenStack packages seem to always use only one tarball
        sources0 = filter(lambda x: x[1] == 0, sources)
        if len(sources0) == 0:
            error = "Source0 not found"
            raise exception.SpecFileParseError(spec_fn=self.fn, error=error)
        source_url = sources0[0][0]
        return [source_url]

    def get_source_fns(self):
        return map(os.path.basename, self.get_source_urls())

    def get_last_changelog_entry(self, strip=False):
        _, changelog = self.txt.split("%changelog\n")
        changelog = changelog.strip()
        entries = re.split(r'\n\n+', changelog)
        entry = entries[0]
        lines = entry.split("\n")
        if strip:
            lines = map(lambda x: x.lstrip(" -*\t"), lines)
        return lines[0], lines[1:]
