import io
import sys
import os
import getpass

import subprocess
from pathlib import Path
from unittest import mock

from .misc import task,  printerr, pip_install, git_clone

URL = "https://github.com/antonio-cavallo/sxope-bigq.git"
REF = "beta/0.0.0"  # bigq reference to install for prod

PROJECTS = {
    "bigq": {
        "url": "https://github.com/antonio-cavallo/sxope-bigq.git",
        "destdir": "{mountpoint}/Projects/sxope-bigq",
        "prod": "beta/0.0.0",
    },
}


@task("mounting gdrive under '{mountpoint}' (readonly? {readonly})")
def mount(mountpoint: Path, readonly: bool = True) -> Path:
    from google.colab import drive
    with mock.patch('sys.stdout', new_callable=io.StringIO) as mck:
        drive.mount(str(mountpoint), force_remount=True, readonly=readonly)
    print(f"drive mounted under {mountpoint}")
    return Path(mountpoint)


@task("adding '{path}' to PYTHONPATH")
def add_pypath(path):
  sys.path.insert(0, str(path))


def setup(
    mode="dev",
    mountpoint=None,
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
            destdir="{mountpoint}/MyDrive/Projects/sxope-bigq"
        )
    """
    assert mode in { "prod", "dev-install", "dev" }

    if mode == "prod":
        token = None
        for name in PROJECTS:
            project = PROJECTS[name]
            if not project.get("prod"):
                continue
            if token is None:
                token = getpass.getpass(f"Please provide an access token: ")
            pip_install(project["url"], token=token, ref=project["prod"])

        from bigq.nb.utils import check_notebook
        return check_notebook()

    if mode in { "dev", "dev-install" } and not (mountpoint and destdir):
        printerr(f"""\
In dev mode you need the mountpoint/destdir args
Try:
    sxope_nbinstaller.install("{mode}", mountpoint=..., destdir=...)
""", multiline=True)
        return

    # mount the GDrive
    mountpoint = Path(mountpoint)
    mount(mountpoint, readonly=True if mode == "dev" else False)

    token = None
    for name in (projects or []):
        project = PROJECTS[name]

        if mode == "dev-install" and token is None:
            token = getpass.getpass(f"Please provide the token for [{name}]: ")

        destdir = Path(project["destdir"].format(mountpoint=mountpoint)).absolute()
        if mode == "dev-install":
            git_clone(destdir, url=project["url"], token=token)

        add_pypath(destdir / "src")

    # moment of truth
    from bigq.nb.utils import check_notebook
    print("Verify system:")
    return check_notebook()
