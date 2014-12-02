import common
from rdoupdate.shell import run


def test_dl_basic(tmpdir):
    upf = common.update_file('basic')
    assert upf.check()
    with tmpdir.as_cwd():
        run('download', '-f', str(upf), '-o', 'out')
        current = common.cfind('out')
    right = {
        './icehouse',
        './icehouse/fedora-20',
        './icehouse/fedora-20/banana-1.0-1.fc21.noarch.rpm',
        './icehouse/fedora-20/banana-1.0-1.fc21.src.rpm',
        './icehouse/fedora-20/orange-2.0-2.el6.noarch.rpm',
        './icehouse/fedora-20/orange-2.0-2.el6.src.rpm',
    }
    assert current == right


def test_dl_arch(tmpdir):
    upf = common.update_file('arch')
    assert upf.check()
    with tmpdir.as_cwd():
        run('download', '-f', str(upf), '--per-update')
        current = common.cfind('.')
    right = {
        './arch.yml',
        './arch.yml/icehouse',
        './arch.yml/icehouse/fedora-20',
        './arch.yml/icehouse/fedora-20/banana-1.0-1.fc21.noarch.rpm',
        './arch.yml/icehouse/fedora-20/banana-1.0-1.fc21.src.rpm',
        './arch.yml/icehouse/fedora-20/orange-2.0-2.el6.src.rpm',
        './arch.yml/icehouse/fedora-20/orange-2.0-2.el6.src.rpm',
    }
    assert current == right


def test_dl_archfail(tmpdir):
    upf = common.update_file('archfail')
    assert upf.check()
    with tmpdir.as_cwd():
        ec = run('download', '--file', str(upf), '-u', '-o', 'out')
        current = common.cfind('.')
    right = {
          "./out",
          "./out/archfail.yml",
          "./out/archfail.yml/icehouse",
          "./out/archfail.yml/icehouse/fedora-20",
          "./out/archfail.yml/icehouse/fedora-20/banana-1.0-1.fc21.noarch.rpm",
          "./out/archfail.yml/icehouse/fedora-20/banana-1.0-1.fc21.src.rpm",
          "./out/archfail.yml/icehouse/fedora-20/orange-2.0-2.el6.src.rpm",
    }
    import json
    print json.dumps(sorted(current), indent=2)
    assert current == right
