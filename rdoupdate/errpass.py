class ErrorBool(object):
    def __init__(self, err=None):
        self.err = err

    def __nonzero__(self):
        return not bool(self.err)


class BuildErrorBool(ErrorBool):
    def __init__(self, build, err=None):
        super(BuildErrorBool, self).__init__(err=err)
        self.build = build
