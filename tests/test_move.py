import common
import rdoupdate.shell
from rdoupdate.utils.cmd import git


def test_move_one(tmpdir):
    repo = common.create_rdoupate_repo(tmpdir)
    with repo.as_cwd():
        author_before = git.get_file_authors('updates/basic.yml')[0]
        common.set_git_user(joe=False)
        rdoupdate.shell.run('move', 'updates/basic.yml')
        assert repo.join('ready', 'basic.yml').exists
        author_after = git.get_file_authors('ready/basic.yml')[0]
    assert author_after == author_before


def test_move_multiple(tmpdir):
    repo = common.create_rdoupate_repo(tmpdir)
    with repo.as_cwd():
        authors_before = (
            git.get_file_authors('updates/basic.yml')[0],
            git.get_file_authors('updates/arch.yml')[0]
        )
        common.set_git_user(joe=True)
        rdoupdate.shell.run('move', 'updates/basic.yml', 'updates/arch.yml')
        assert repo.join('ready', 'basic.yml').exists
        assert repo.join('ready', 'arch.yml').exists
        authors_after = (
            git.get_file_authors('ready/basic.yml')[0],
            git.get_file_authors('ready/arch.yml')[0]
        )
    assert authors_after == authors_before
