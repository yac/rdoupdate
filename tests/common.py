import os
import py
import shutil
from rdoupdate.utils.cmd import git


ASSETS_DIR = 'tests/assets'
UPDATES_DIR = 'updates'


def update_file(name):
    ap = os.path.abspath('%s/updates/%s.yml' % (ASSETS_DIR, name))
    return py.path.local(ap)


def ffind(path='.', include_dirs=True):
    tree = set()
    for root, dirs, files in os.walk(path):
        if include_dirs:
            for f in dirs:
                tree.add(os.path.join(root, f))
        for f in files:
            tree.add(os.path.join(root, f))
    return tree


def cfind(path, include_dirs=True):
    if not hasattr(path, 'as_cwd'):
        path = py.path.local(path=path)
    with path.as_cwd():
        t = ffind(include_dirs=include_dirs)
    t = set(filter(lambda x: not x.startswith('./.'), t))
    return t


def set_git_user(joe=True):
    if joe:
        user = 'Original Joe'
        email = 'joe@origin.al'
    else:
        user = 'Not Joe'
        email = 'not@joe.xxx'
    git('config', 'user.name', user)
    git('config', 'user.email', email)


def create_rdoupate_repo(tmpdir):
    updates = py.path.local(ASSETS_DIR).join(UPDATES_DIR)
    repo = tmpdir.join('rdo-update')
    updates.copy(repo.join(UPDATES_DIR))
    with repo.as_cwd():
        git('init')
        set_git_user(joe=True)
        git('add', '.')
        git('rm', '--cached', 'updates/arch.yml')
        git('commit', '-m', 'Look at all these updates by Joe!')
        set_git_user(joe=False)
        git('add', 'updates/arch.yml')
        git('commit', '-m', 'This is not from Joe, bah')
    return repo
