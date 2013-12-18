class RdopkgException(Exception):
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
        super(RdopkgException, self).__init__(msg)


class CommandFailed(RdopkgException):
    msg_fmt = "Command failed: %(cmd)s"
