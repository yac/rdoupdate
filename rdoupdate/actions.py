import argparse
import os
import re
import sys
import yaml

import core
import exception
from utils.cmd import run, git


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


def main():
    epilog = """
When no update file to check is specified using -g or -f, git repo
in current directory is assumed by default (-g .)")
"""
    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument('-g', '--git', type=str, metavar='DIR',
                        help="check latest update file from git repository in DIR directory")
    parser.add_argument('-f', '--file', type=str, metavar='FILE',
                        help="check latest update file FILE; use - for stdin")
    args = parser.parse_args()
    if args.file and args.git:
        print "Only one update file can be specified."
        sys.exit(2)
    try:
        if args.file:
            update = check_file(args.file)
        else:
            if not args.git:
                args.git = '.'
            update = check_git(args.git)
        print update
    except IOError as e:
        error("file error", "%s: %s" % (e.strerror, e.filename), 2)
    except exception.ChdirError as e:
        error("file error", e, 3)
    except exception.CommandFailed as e:
        error("command failed", e.kwargs['cmd'], 5)
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
        error("invalid YAML", e, 7)
    except exception.InvalidUpdateStructure as e:
        error("invalid structure", e, 11)
    except exception.InvalidUpdateCommit as e:
        error("invalid commit", e, 13)
    except exception.ParsingError as e:
        error("parsing error", e, 17)
    except Exception as e:
        err = type(e).__name__
        ex = str(e)
        if ex:
            err += ": %s" % ex
        error("unexpected error", err, 42)

