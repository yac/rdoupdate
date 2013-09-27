import exception
import log

import subprocess


class _CommandOutput(str):                                                    
    """
    Just a string subclass with attribute access.
    """
    @property
    def success(self):
        return self.return_code == 0


def log_cmd_fail(cmd, cout, fail_log_fun=log.warn, out_log_fun=log.info):
    fail_log_fun('command failed: %s' % cmd)
    nl = False
    if cout:
        out_log_fun("stdout:")
        out_log_fun(cout)
        nl = True
    if cout.stderr:
        out_log_fun("stderr:")
        out_log_fun(cout.stderr)
        nl = True
    if nl:
        out_log_fun('')


def run(cmd, fatal=True, stdout=False, stderr=False):
    log.command('$ %s' % cmd)
    prc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    out, err = prc.communicate()
    if out:
        out = out.rstrip()
        if stdout:
            log.info(out)
    else:
        out = ''
    if err:
        err = err.rstrip()
        if stderr:
            log.info(err)
    else:
        err = ''
    cout = _CommandOutput(out)
    cout.stderr = err
    cout.return_code = prc.returncode
    if prc.returncode != 0 and fatal:
        log_cmd_fail(cmd, cout)
        raise exception.CommandFailed(cmd=cmd, out=cout)
    return cout
