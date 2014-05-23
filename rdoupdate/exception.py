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
    msg_fmt = "%(build_id)s isn't available from %(source)s. %(detail)s"


class NotADirectory(RdopkgException):
    msg_fmt = "Not a directory: %(path)s"


class FileExists(RdopkgException):
    msg_fmt = "File already exists: %(path)s"


class InvalidFilter(RdopkgException):
    msg_fmt = "Invalid filter: %(what)s"


class NoBuildFilesDownloaded(RdopkgException):
    msg_fmt = "No files were downloaded for build: %(build)s"


class AllBuildFilesExcluded(RdopkgException):
    msg_fmt = "All files were excluded by a filter for build: %(build)s"


class Bug(RdopkgException):
    msg_fmt = "Bug: %(dafuq)s"
