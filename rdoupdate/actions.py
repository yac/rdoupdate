import os
import re
import shutil
import yaml

import core
import exception
import helpers
from utils.cmd import git
from utils import log


def check_file(stream):
    if isinstance(stream, basestring):
        stream = file(stream, 'r')
    data = yaml.load(stream)
    return core.Update(data)


def check_files(*files, **kwargs):
    good = []
    fails = []
    avail = kwargs.get('available', False)
    for f in files:
        try:
            update = check_file(f)
            if avail:
                avl = update.all_builds_available()
                if not avl:
                    e = exception.BuildNotAvailable(
                        build_id=avl.build.full_id(), detail=avl.err or '')
                    raise e
            good.append((f, update))
        except Exception as ex:
            fails.append((f, ex))
    return good, fails


def print_summary(good, fails, good_s, fail_s):
    n_good = len(good)
    n_fails = len(fails)
    n_all = n_good + n_fails
    if good:
        log.success("\n%d updates %s:" % (n_good, good_s))
        fmt = '{t.bold}{upf}:{t.normal}\n{up}'
        l = map(lambda x: fmt.format(t=log.term, upf=x[0], up=x[1]), good)
        helpers.print_list(l)
    if fails:
        log.error("\n%s updates %s:" % (n_fails, fail_s))
        fmt = "{t.warn}{upf}:{t.normal} {err}"
        l = map(lambda x: fmt.format(t=log.term, upf=x[0], err=str(x[1])),
                fails)
        helpers.print_list(l)


def download_updates_builds(*files, **kwargs):
    good = []
    fails = []
    per_update = kwargs.get('per_update', False)
    out_dir = kwargs.get('out_dir', None)
    if not out_dir:
        out_dir = ''
    prefix = None
    for f in files:
        try:
            update = check_file(f)
            bn = os.path.basename(f)
            if per_update:
                prefix = bn
            log.info(log.term.bold('downloading %s' % core.pp_update(bn)))
            update.download(out_dir=out_dir, prefix=prefix)
            good.append((f, update))
        except Exception as ex:
            log.warn(str(ex))
            fails.append((f, ex))
    return good, fails


def get_last_commit_update(dir):
    with helpers.cdir(dir):
        out = git('diff', '--name-status', 'HEAD~..HEAD').strip()
    if out.find("\n") != -1:
        raise exception.InvalidUpdateCommit(
            msg="Last commit changes more than one file.")
    m = re.match('^([A-Z])\s+(\S+)$', out)
    if not m:
        raise exception.ParsingError(what="git diff output", str=out)
    status = m.group(1)
    if status != 'A' and status != 'M':
        raise exception.InvalidUpdateCommit(
            msg=("Invalid file status %s, should be A(dded) or M(odified)" %
                 status))
    fn = m.group(2)
    return fn


def move_files(files, to_dir):
    if not os.path.exists(to_dir):
        os.makedirs(to_dir)
    n_files = len(files)
    if n_files == 1:
        msg = "Move %s to %s/" % (core.pp_update(files[0]), to_dir)
    else:
        msg = "Move %d updates to %s/\n" % (n_files, to_dir)
    for from_path in files:
        bn = os.path.basename(from_path)
        to_path = "%s/%s" % (to_dir, bn)
        assert(from_path and to_path)
        git('mv', from_path, to_path)
        if n_files != 1:
            msg += "\n%s" % core.pp_update(from_path)
    git('commit', '-a', '-F', '-', input=msg, print_output=True)

