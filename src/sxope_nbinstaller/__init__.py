import io
import sys
import getpass

from pathlib import Path
from unittest import mock

from .misc import task, pip_install, git_clone, printok


PROJECTS = {
    "bigq": {
        "url": "https://github.com/antonio-cavallo/sxope-bigq.git",
        "destdir": "{projectsdir}/sxope-bigq",
        "prod": "beta/0.0.0",
    },
}


@task("mounting gdrive under '{mountpoint}' (readonly? {readonly})")
def mount(mountpoint: Path, readonly: bool = True) -> Path:
    from google.colab import drive

    with mock.patch("sys.stdout", new_callable=io.StringIO):
        drive.mount(str(mountpoint), force_remount=True, readonly=readonly)
    print(f"drive mounted under {mountpoint}")
    return Path(mountpoint)


@task("adding '{path}' to PYTHONPATH")
def add_pypath(path):
    sys.path.insert(0, str(path))


def setup(
    mode="dev",
    mountpoint="/content/GDrive",
    projectsdir="{mountpoint}/MyDrive/Projects",
    projects=None,
):
    """setup the notebook

    In prod mode it will install the sxope-bigq library.
    In dev mode it will:
        mount the user's GDrive under mount point (readonly)
        set the PYTHONPATH to destdir / src

    In dev-install it will:
        mount the user's GDrive under mount point (writeable)
        checkout sxope-bigq project under destdir
        set the PYTHONPATH to destdir / src

    NOTE: dev-install is a useful one-off command, once the
          source code id checked out under destdir you don't want
          to re-run it.!

    Examples:

        sxope_nbinstaller.install("dev-install",
            mountpoint="/content/GDrive",
            destdir="{mountpoint}/MyDrive/Projects",
            projects=["bigq",]
        )
    """
    assert mode in {"prod", "dev-install", "dev"}

    def pathresolver(path):
        return Path(
            str(path).format(mountpoint=mountpoint, projectsdir=projectsdir)
        ).absolute()

    projects = projects or list(PROJECTS)[:1]
    projectsdir = pathresolver(projectsdir)

    printok(
        f"""\
setting up [{mode}]
Settings:
  projectsdir : {projectsdir}
  mounted     : {mountpoint}
  projects    : {', '.join(projects)}
""",
        multiline=True,
    )

    if mode == "prod":
        token = None
        for name in PROJECTS:
            project = PROJECTS[name]
            if not project.get("prod"):
                continue
            if token is None:
                token = getpass.getpass("Please provide an access token: ")
            pip_install(project["url"], token=token, ref=project["prod"])

        from bigq.nb.utils import check_notebook

        return check_notebook()

    # mount the GDrive
    mountpoint = Path(mountpoint)
    mount(mountpoint, readonly=True if mode == "dev" else False)

    token = None
    for name in projects:
        project = PROJECTS[name]

        if mode == "dev-install" and token is None:
            token = getpass.getpass(f"Please provide the token for [{name}]: ")

        dst = pathresolver(project["destdir"])
        if mode == "dev-install":
            git_clone(dst, url=project["url"], token=token)

        add_pypath(dst / "src")

    # moment of truth
    from bigq.nb.utils import check_notebook

    print("Verify system:")
    return check_notebook()
