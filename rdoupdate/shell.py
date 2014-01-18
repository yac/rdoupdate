# -*- encoding: utf-8 -*-

import argparse
import sys
import yaml

import actions
import core
import exception


def error(errtype, msg, code=42):
    sys.stderr.write("[ERROR] %s: %s\n" % (errtype, msg))
    sys.exit(code)


def get_parser():
    parser = argparse.ArgumentParser(prog='rdopkg')
    subparsers = parser.add_subparsers(help='available actions')
    parser.add_argument('--version', action='version', version=core.VERSION)
    check_parser = subparsers.add_parser(
        'check', help="validate an update file")
    check_parser.add_argument('-g', '--git', type=str, metavar='DIR',
        help="check latest update file from git repository in DIR directory")
    check_parser.add_argument('-f', '--file', type=str, metavar='FILE',
        help="check latest update file FILE; use - for stdin")
    check_parser.set_defaults(action=do_check)

    return parser


def do_check(args):
    if args.file and args.git:
        error("invalid invocation", "Only one update file can be "
                                    "specified.", 19)
    if args.file:
        update = actions.check_file(args.file)
    else:
        if not args.git:
            args.git = '.'
        update = actions.check_git(args.git)
    print update


def main(cargs=None):
    if cargs is None:
        cargs = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(cargs)
    action = args.action
    try:
        action(args)
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
