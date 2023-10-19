import getpass
import contextlib
from pathlib import Path
import json

from . import tasks, misc


PROJECTS = {
    "bigq": {
        "url": "https://github.com/antonio-cavallo/sxope-bigq.git",
        "prod": "v0.0.2",  # check out this in prod
        "ask-token": True,
        "dev": "",  # check out this in dev-install
        "destdir": "{projectsdir}/sxope-bigq",
        "pypath": "src",
    },
    "alphalens": {
        "url": "https://github.com/antonio-cavallo/alphalens.git",
        "prod": "ng",
        "ask-token": False,
        "dev": "ng",  # check out this in dev-install
        "destdir": "{projectsdir}/alphalens",
        "pypath": "",
    },
}


def setup(
    mode="dev",
    mountpoint="/content/GDrive",
    projectsdir="{mountpoint}/MyDrive/Projects",
    credentials="{mountpoint}/MyDrive/credentials.json",
    projects=None,
    writeable=None,
    dryrun=False,
):
    """setup the notebook

    In 'prod' mode it will install the sxope-bigq library.

    In 'dev' mode it will:
        mount the user's GDrive under mountpoint (writeable unless setto False)
        set the PYTHONPATH to destdir / src

    In dev-install it will:
        mount the user's GDrive under mount point (writeable)
        checkout sxope-bigq project under {mountpoint}/{projectsdir}/<project-destdir>
        set the PYTHONPATH to src

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
        if not path:
            return
        return Path(
            str(path).format(mountpoint=mountpoint, projectsdir=projectsdir)
        ).absolute()

    projectsdir = pathresolver(projectsdir)
    projects = ([projects] if isinstance(projects, str) else projects) or list(
        PROJECTS
    )[:1]
    writeable = (
        (True if mode in {"dev-install"} else False) if writeable is None else writeable
    )

    misc.set_runmode(misc.RunMode.DRYRUN if dryrun else None)

    mountpoint = Path(mountpoint).absolute() if mountpoint else None
    tasks.report(mode, mountpoint, projectsdir, projects, PROJECTS, writeable)

    # mount the GDrive
    tasks.mount(mountpoint, readonly=not writeable)

    tokens = {}
    if credentials:
        if (path := pathresolver(credentials)).exists():
            misc.printtask(f"loading credentials from {path}")
            tokens = json.loads(path.read_text())
        else:
            misc.printwarn(f"cannot find credentials file in {path}")

    for name in PROJECTS:
        project = PROJECTS[name]
        if mode == "prod":
            if not project.get("prod"):
                continue
            token = tokens.get(name, None)
            if not token and project.get("ask-token") and not dryrun:
                token = getpass.getpass("Please provide an access token: ")
            tasks.pip_install(project["url"], token=token, ref=project["prod"])
        elif mode in {"dev", "dev-install"}:
            destdir = project.get("destdir")
            destdir = projectsdir / destdir.format(
                **{"projectsdir": projectsdir, **project}
            )
            pypath = destdir / project.get("pypath", "")

            if mode == "dev-install":
                token = tokens.get(name, None)
                if not token and project.get("ask-token") and not dryrun:
                    token = getpass.getpass("Please provide an access token: ")
                tasks.git_clone(
                    destdir, url=project["url"], token=token, branch=project.get("dev")
                )

            tasks.add_pypath(pypath)

    with contextlib.suppress(ModuleNotFoundError):
        from bigq.nb.utils import check_notebook

        return check_notebook()
    return "bigq not installed"


#     if mode == "prod":
#         token = None
#         for name in PROJECTS:
#             project = PROJECTS[name]
#             if not project.get("prod"):
#                 continue
#             if token is None and not dryrun:
#                 token = getpass.getpass("Please provide an access token: ")
#             tasks.pip_install(project["url"], token=token, ref=project["prod"])
#
#         with contextlib.suppress(ModuleNotFoundError):
#             from bigq.nb.utils import check_notebook
#
#             return check_notebook()
#         return "bigq not installed"
#
#     # TODO
#     return
#
#     token = None
#     for name in projects:
#         project = PROJECTS[name]
#
#         if mode == "dev-install" and token is None:
#             token = getpass.getpass(f"Please provide the token for [{name}]: ")
#
#         dst = pathresolver(project["destdir"])
#         if mode == "dev-install":
#             tasks.git_clone(dst, url=project["url"], token=token)
#
#         tasks.add_pypath(dst / "src")
#
#     # moment of truth
#     from bigq.nb.utils import check_notebook
#
#     print("Verify system:")
#     return check_notebook()


if __name__ == "__main__":
    # setup("prod", dryrun=True)
    # setup("dev", dryrun=True)
    setup("dev-install", dryrun=True)
