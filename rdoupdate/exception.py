from utils.exception import RdopkgException, CommandFailed


class InvalidUpdateStructure(RdopkgException):
    msg_fmt = "Invalid update structure"


class InvalidUpdateCommit(RdopkgException):
    msg_fmt = "Invalid update commit"


class ParsingError(RdopkgException):
    msg_fmt = "Error parsing %(what)s: %(str)s"


class ChdirError(RdopkgException):
    msg_fmt = "Failed to change directory: %(dir)s"


class Bug(RdopkgException):
    msg_fmt = "Bug: %(dafuq)s"
