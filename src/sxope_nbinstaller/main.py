import getpass

from pathlib import Path

from .misc import printok
from .tasks import pip_install, git_clone, mount, add_pypath


PROJECTS = {
    "bigq": {
        "url": "https://github.com/antonio-cavallo/sxope-bigq.git",
        "destdir": "{projectsdir}/sxope-bigq",
        "prod": "f26124adbf8eae9a690820722b1c8b015508f7ea",
    },
}


def report(mode, mountpoint, projectsdir, projects, readonly, pre=" " * 2):
    def pathresolver(path):
        if not path:
            return
        return Path(
            str(path).format(mountpoint=mountpoint, projectsdir=projectsdir)
        ).absolute()

    lines = [
        f"setting up [{mode}]",
    ]
    lines.append("Config")
    lines.append(
        f"{pre}mountpoint  : {mountpoint} (readonly? {'yes' if readonly else 'no'})"
    )
    lines.append(f"{pre}projectsdir : {projectsdir}")
    lines.append(f"{pre}projects    : {', '.join(projects)}")
    lines.append(f"{pre}")
    lines.append("Projects list")
    for name in (*projects, *[p for p in PROJECTS if p not in projects]):
        project = PROJECTS[name]
        destdir = pathresolver(project.get("destdir", ""))
        active = "+" if destdir and destdir.exists() else "."
        lines.append(f"{pre}{active} {project}: {destdir}")
        lines.append(f"{pre}  (from {project.get('url')})")
    return lines


def setup(
    mode="dev",
    mountpoint="/content/GDrive",
    projectsdir="{mountpoint}/MyDrive/Projects",
    projects=None,
    readonly=None,
):
    """setup the notebook

    In 'prod' mode it will install the sxope-bigq library.

    In 'dev' mode it will:
        mount the user's GDrive under mountpoint (readonly unless setto False)
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
    projects = projects or list(PROJECTS)[:1]
    readonly = (
        (True if mode in {"dev", "prod"} else False) if readonly is None else readonly
    )
    printok(
        "\n".join(report(mode, mountpoint, projectsdir, projects, readonly)),
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
    mount(mountpoint, readonly=readonly)

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
