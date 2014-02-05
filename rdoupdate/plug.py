import os
import glob
import imp


IMPORTED_BUILD_SOURCES = []


def import_file(fn):
    (path, name) = os.path.split(fn)
    (name, ext) = os.path.splitext(name)

    (file, filename, data) = imp.find_module(name, [path])
    return imp.load_module(name, file, filename, data)


def import_pyfiles(path):
    """
    Import all *.py files in specified directory.
    """
    n = 0
    for pyfile in glob.glob(os.path.join(path, '*.py')):
        m = import_file(pyfile)
        IMPORTED_BUILD_SOURCES.append(m)
        n += 1
    return n


def import_fetchers():
    libdir, _ = os.path.split(__file__)
    bsrc_dir = os.path.join(libdir, 'bsources')
    import_pyfiles(bsrc_dir)


import_fetchers()
