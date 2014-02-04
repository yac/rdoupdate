from utils.exception import RdopkgException, CommandFailed


class InvalidUpdateStructure(RdopkgException):
    msg_fmt = "Invalid update structure"


class InvalidUpdateCommit(RdopkgException):
    msg_fmt = "Invalid update commit"


class ParsingError(RdopkgException):
    msg_fmt = "Error parsing %(what)s: %(str)s"


class ChdirError(RdopkgException):
    msg_fmt = "Failed to change directory: %(dir)s"


class InvalidBuildSource(RdopkgException):
    msg_fmt = "Invalid build source: %(source)s"


class BuildNotAvailable(RdopkgException):
    msg_fmt = "%(build_id)s isn't available. %(detail)s"


class NotADirectory(RdopkgException):
    msg_fmt = "Not a directory: %(path)s"


class Bug(RdopkgException):
    msg_fmt = "Bug: %(dafuq)s"
