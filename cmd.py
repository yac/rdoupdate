import subprocess

import exception
import log


class _CommandOutput(str):
    """
    Just a string subclass with attribute access.
    """
    @property
    def success(self):
        return self.return_code == 0


def log_cmd_fail(cmd, cout, fail_log_fun=log.warn, out_log_fun=log.info):
    fail_log_fun('{t.error}command failed: {t.normal}{t.cmd}{cmd}{t.normal}'
        .format(t=log.term, cmd=cmd))
    nl = False
    if cout:
        out_log_fun(log.term.bold("stdout:"))
        out_log_fun(cout)
        nl = True
    if cout.stderr:
        out_log_fun(log.term.bold("stderr:"))
        out_log_fun(cout.stderr)
        nl = True
    if nl:
        out_log_fun('')


def run(cmd, *params, **kwargs):
    fatal = kwargs.get('fatal', True)
    direct = kwargs.get('direct', False)
    log_cmd = kwargs.get('log_cmd', True)
    input = kwargs.get('input')
    print_stdout = kwargs.get('print_stdout', False)
    print_stderr = kwargs.get('print_stderr', False)
    print_output = kwargs.get('print_output', False)

    cmd = [cmd] + list(params)
    cmd_str = ' '.join(cmd)

    if log_cmd:
        log.command(log.term.cmd(cmd_str))

    if print_output:
        print_stdout = True
        print_stderr = True

    if input:
        stdin = subprocess.PIPE
    else:
        stdin = None

    if direct:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE

    prc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout,
                           stderr=stdout)
    out, err = prc.communicate(input=input)

    if out:
        out = out.rstrip()
        if print_stdout:
            log.info(out)
    else:
        out = ''

    if err:
        err = err.rstrip()
        if print_stderr:
            log.info(err)
    else:
        err = ''

    cout = _CommandOutput(out)
    cout.stderr = err
    cout.return_code = prc.returncode
    cout.cmd = cmd_str
    if prc.returncode != 0 and fatal:
        log_cmd_fail(cmd_str, cout)
        raise exception.CommandFailed(cmd=cmd, out=cout)
    return cout


class ShellCommand(object):
    command = None

    def __init__(self):
        if self.command is None:
            self.command = self.__class__.__name__.lower()

    def __call__(self, *params, **kwargs):
        return run(self.command, *params, **kwargs)


class Git(ShellCommand):
    command = "git"

    def create_branch_from_remote(self, branch, remote_branch=None):
        lbr = self.local_branches()
        if branch in lbr or remote_branch in lbr:
            return
        if remote_branch is None:
            for rbr in self.remote_branches():
                br = rbr[rbr.find('/')+1:]
                if rbr == branch or br == branch:
                    remote_branch = rbr
        elif remote_branch not in self.remote_branches():
            raise Exception("Branch %s doesnt exist in remotes" %
                            remote_branch)
        self.create_branch(branch, remote_branch)

    def _format_output(self, out):
        out = out.split("\n")
        out = [l.strip() for l in out if l and l.find('HEAD') < 0]
        return out

    def remote_branches(self, remote=""):
        res = self("branch", "-r")
        branches = self._format_output(res)
        branches = [b.replace("remotes/", "") \
                    for b in branches if b.startswith(remote)]
        return branches

    def local_branches(self):
        res = self("branch")
        res = self._format_output(res)
        res = [b.replace("* ", "") for b in res]
        return res

    @property
    def current_branch(self):
        branch = self('rev-parse', '--abbrev-ref', 'HEAD', log_cmd=False)
        return branch

    def branch_exists(self, branch):
        o = self('show-ref', '--verify', '--quiet', 'refs/heads/%s' % branch,
                 fatal=False, log_cmd=False)
        return o.success

    def remotes(self):
        res = self("remote", "show")
        return self._format_output(res)

    def delete_branch(self, branch):
        self('branch', '-D', branch)

    def create_branch(self, new_branch, branch):
        try:
            self('branch', '-f', new_branch, branch)
        except exception.CommandFailed:
            # this could only fail if we're on the branch
            self('reset', '--hard', branch)

    def squash_last(self, branch=None):
        if branch is not None:
            self('checkout', branch)
        self("reset", "--soft", "HEAD~")
        # on git < 1.7.9 --no-edit can be done by:
        # git commit -C HEAD --amend
        self("commit", "--amend", "--no-edit")

    def linearize(self, starting_point, branch=None):
        if branch is not None and self.current_branch != branch:
            self('checkout', branch)
        self('rebase', starting_point)

    def get_commits_from_revision(self, revision):
        res = self('log', '--oneline', revision + '..')
        res = self._format_output(res)
        res = [l.split()[0] for l in res]
        return res

    def config_get(self, param):
        return self("config", "--get", param)

    def config_set(self, param, value, is_global=False):
        params = [param, value]
        if is_global:
            params.insert(0, '--global')
        return self("config", *params)

    def checkout(self, branch):
        self("checkout", branch)

    def remove(self, hash):
        self('rebase', '--onto', hash+'^', hash, '--preserve-merges',
             '--committer-date-is-author-date')


git = Git()
