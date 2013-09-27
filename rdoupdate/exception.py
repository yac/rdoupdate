class UpdateException(Exception):
    msg_fmt = "An unknown error occurred"

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt % kwargs
            except Exception as e:
                # kwargs doesn't mach those in message.
                # Returning this is still better than nothing.
                message = self.msg_fmt
        super(UpdateException, self).__init__(msg)


class InvalidUpdateStructure(UpdateException):
    msg_fmt = "Invalid update structure"


class InvalidUpdateCommit(UpdateException):
    msg_fmt = "Invalid update commit"


class CommandFailed(UpdateException):
    msg_fmt = "Command failed: %(cmd)s"


class ParsingError(UpdateException):
    msg_fmt = "Error parsing %(what)s: %(str)s"


class ChdirError(UpdateException):
    msg_fmt = "Failed to change directory: %(dir)s"


class Bug(UpdateException):
    msg_fmt = "Bug: %(dafuq)s"
