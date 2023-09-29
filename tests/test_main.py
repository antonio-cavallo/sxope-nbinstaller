from sxope_nbinstaller import main


def test_report():
    lines = main.report(
        mode="prod",
        mountpoint="/a/mount point",
        projectsdir="{mountpoint}/subprojects/dir",
        projects=["bigq"],
        writeable=True,
    )
    assert (
        "\n".join(lines)
        == """\
setting up [prod]
Config
  mountpoint  : /a/mount point (writeable? yes)
  projectsdir : /a/mount point/subprojects/dir
  projects    : bigq

Projects list
  . bigq
    (from https://github.com/antonio-cavallo/sxope-bigq.git)
""".rstrip()
    )

    lines = main.report(
        mode="dev",
        mountpoint="/a/mount point",
        projectsdir="{mountpoint}/subprojects/dir",
        projects=["bigq"],
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
  . bigq
    destdir /a/mount point/subprojects/dir/sxope-bigq
    (from https://github.com/antonio-cavallo/sxope-bigq.git)
""".rstrip()
    )
