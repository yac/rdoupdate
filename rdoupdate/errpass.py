class ErrorBool(object):
    def __init__(self, err=None):
        self.err = err

    def __nonzero__(self):
        return not bool(self.err)

    def __str__(self):
        if self.err:
            return "False (%s)" % self.err
        else:
            return "True"


class BuildErrorBool(ErrorBool):
    def __init__(self, build, err=None):
        super(BuildErrorBool, self).__init__(err=err)
        self.build = build
