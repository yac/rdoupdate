import os
import re
import shutil
import yaml

import core
import exception
from utils.cmd import git


def check_file(stream):
    if isinstance(stream, basestring):
        stream = file(stream, 'r')
    data = yaml.load(stream)
    return core.Update(data)


def check_git(dir):
    if dir and dir != '.':
        try:
            os.chdir(dir)
        except OSError:
            raise exception.ChdirError(dir=dir)
    out = git('diff', '--name-status', 'HEAD~..HEAD').strip()
    if out.find("\n") != -1:
        raise exception.InvalidUpdateCommit(
            msg="Update commit changes more than one file.")
    m = re.match('^([A-Z])\s+(\S+)$', out)
    if not m:
        raise exception.ParsingError(what="git diff output", str=out)
    status = m.group(1)
    if status != 'A' and status != 'M':
        raise exception.InvalidUpdateCommit(
            msg=("Invalid file status %s, should be A(dded) or M(odified)" %
                 status))
    fn = m.group(2)
    return check_file(fn)


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

