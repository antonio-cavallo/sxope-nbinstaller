from unittest import mock
from sxope_nbinstaller import tasks


def test_report(capsys):
    allprojects = {
        "bigq": {
            "url": "https://github.com/antonio-cavallo/sxope-bigq.git",
            "destdir": "{projectsdir}/sxope-bigq",
            "pypath": "src",
            "prod": "git+{url}@1e3d05c0b4df50299a459cd822349cce03f4de22",
        }
    }
    lines = tasks.report(
        mode="prod",
        mountpoint="/a/mount point",
        projectsdir="{mountpoint}/subprojects/dir",
        projects=["bigq"],
        allprojects=allprojects,
        writeable=True,
    )
    assert (
        capsys.readouterr().out.strip()
        == """\
👉 current configuration .. ✅
   | setting up [prod]
   | Config
   |   mountpoint  : /a/mount point (writeable? yes)
   |   projectsdir : /a/mount point/subprojects/dir
   |   projects    : [bigq]
   |   writeable   : True
   | 
   | Projects list
   |   . bigq
   |     pip install from https://github.com/antonio-cavallo/sxope-bigq.git
   |     (ref. git+{url}@1e3d05c0b4df50299a459cd822349cce03f4de22)
""".rstrip()
    )
    return
    lines = tasks.report(
        mode="dev",
        mountpoint="/a/mount point",
        projectsdir="{mountpoint}/subprojects/dir",
        projects=["bigq"],
        allprojects=allprojects,
        writeable=False,
    )
    assert (
        "\n".join(lines)
        == """\
setting up [dev]
Config
  mountpoint  : /a/mount point (writeable? no)
  projectsdir : /a/mount point/subprojects/dir
  projects    : bigq

Projects list
  + bigq
    (from https://github.com/antonio-cavallo/sxope-bigq.git)
""".rstrip()
    )


def test_git_clone(capsys):
    url = "https://github.com/antonio-cavallo/sxope-bigq.git"
    with mock.patch("subprocess.check_output") as mck:
        tasks.git_clone("abc", url)
        assert (
            capsys.readouterr().out.strip().partition("\n")[0]
            == "👉 checkout source code in 'abc' .. ✅"
        )
        tasks.git_clone("abc", url, token="123")
        capsys.readouterr()

        calls = [c for c in mck.mock_calls if c.args]
        assert len(calls) == 2

        assert calls[0].args[0][2] == url
        assert (
            calls[1].args[0][2]
            == "https://123@github.com/antonio-cavallo/sxope-bigq.git"
        )
