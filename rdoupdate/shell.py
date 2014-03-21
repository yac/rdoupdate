# -*- encoding: utf-8 -*-

import argparse
import os
import sys
import yaml

from . import VERSION
import actions
import core
import exception
from utils import log


def error(errtype, msg, code=42):
    sys.stderr.write("{t.red}[ERROR] {t.yellow}{er}: {msg}"
                     "{t.normal}\n".format(er=errtype, msg=msg, t=log.term))
    sys.exit(code)


def get_parser():
    parser = argparse.ArgumentParser(prog='rdoupdate')
    subparsers = parser.add_subparsers(help='available actions')
    parser.add_argument('--version', action='version', version=VERSION)
    # check
    check_parser = subparsers.add_parser(
        'check', help="validate update file(s)",
        description="validate one or more update files; use -g to select "
                    "an update file added by last commit to a git repo or "
                    "use -f to select update files directly (default: -g .)")
    check_parser.add_argument(
        '-g', '--git', type=str, metavar='DIR',
        help="check latest update file added to git repo in DIR directory")
    check_parser.add_argument(
        '-f', '--files', type=str, metavar='FILE', nargs='+',
        help="check all specified FILEs; use - for stdin")
    check_parser.add_argument(
        '-a', '--available', action='store_true',
        help="also check if builds are available for download")
    check_parser.set_defaults(action=do_check)
    # download
    dl_parser = subparsers.add_parser(
        'download', help="download builds from update file(s)",
        description=("download builds from one or more update files into a "
                     "directory tree; use -g to select an update file added "
                     "by last commit to a git repo or use -f to select update "
                     "files directly; default: -g ."))
    dl_parser.add_argument(
        '-g', '--git', type=str, metavar='DIR',
        help="download builds from latest update file added to git repo in "
             "DIR directory")
    dl_parser.add_argument(
        '-f', '--files', type=str, metavar='FILE', nargs='+',
        help="check all specified FILEs; use - for stdin")
    dl_parser.add_argument(
        '-o', '--outdir', type=str, metavar='DIR',
        help="directory to download builds into (default: .)")
    dl_parser.add_argument(
        '-u', '--per-update', action='store_true',
        help="create extra directory for each update")
    dl_parser.add_argument(
        '-b', '--build-filter', metavar='ATTR:REGEX', action='append',
        help="Only download builds with ATTRibute matching python REGEX; can "
             "be specified multiple times")
    dl_parser.set_defaults(action=do_download)
    # move
    move_parser = subparsers.add_parser(
        'move', help="move an update file (create a commit)",
        description="create a commit that moves selected files to a directory")
    move_parser.add_argument(
        'files', metavar='FILE', type=str, nargs='+',
        help='update file(s) to move')
    move_parser.add_argument(
        '-d', '--dir', type=str, metavar='DIR',
        help="move update file(s) to this directory instead of using "
             "update.group")
    move_parser.set_defaults(action=do_move)
    list_parser = subparsers.add_parser(
        'list-bsources', help="show available build sources",
        description="show available build sources")
    list_parser.set_defaults(action=do_list_bsources)

    return parser


def _get_update_files(args):
    if args.files and args.git:
        error("invalid invocation", "-g and -f are exclusive.", 19)
    if args.files:
        files = args.files
    else:
        if not args.git:
            args.git = '.'
        f = actions.get_last_commit_update(args.git)
        files = [os.path.join(args.git, f)]
    return files


def do_check(args):
    files = _get_update_files(args)
    good, fails = actions.check_files(*files, available=args.available,
                                      verbose=True)
    actions.print_summary(good, fails, 'PASSED', 'FAILED')
    if fails:
        return 127


def _parse_build_filter(fargs):
    bf = []
    if not fargs:
        return bf
    for f in fargs:
        try:
            attr, rex = f.split(':', 1)
        except Exception as ex:
            raise exception.InvalidFilter(what=f)
        bf.append((attr, rex))
    return bf


def do_download(args):
    files = _get_update_files(args)
    build_filter = _parse_build_filter(args.build_filter)
    good, fails = actions.download_updates_builds(
        *files, out_dir=args.outdir, per_update=args.per_update,
        build_filter=build_filter)
    actions.print_summary(good, fails, 'DOWNLOADED', 'FAILED to download')
    if fails:
        return 128


def do_move(args):
    actions.move_files(args.files, args.dir)


def do_list_bsources(args):
    actions.list_build_sources()


def main(cargs=None):
    if cargs is None:
        cargs = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(cargs)
    action = args.action
    try:
        ret = action(args)
        if ret:
            sys.exit(ret)
        else:
            sys.exit()
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


if __name__ == '__main__':
    main()
