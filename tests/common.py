import os
import py


ASSETS_DIR = 'tests/assets'


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


