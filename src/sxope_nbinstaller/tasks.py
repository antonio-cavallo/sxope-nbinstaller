import io
import sys
from unittest import mock
from pathlib import Path
import subprocess

from .misc import task, urlfixer, printwarn


@task("current configuration", anyway=True)
def report(
    mode, mountpoint, projectsdir, projects, allprojects, writeable, pre=" " * 2
):
    def pathresolver(path):
        if not path:
            return
        return Path(
            str(path).format(mountpoint=mountpoint, projectsdir=projectsdir)
        ).absolute()

    projectsdir = pathresolver(projectsdir)

    lines = [
        f"setting up [{mode}]",
    ]
    lines.append("Config")
    lines.append(
        f"{pre}mountpoint  : {mountpoint} (writeable? {'yes' if writeable else 'no'})"
    )
    lines.append(f"{pre}projectsdir : {projectsdir}")
    lines.append(f"{pre}projects    : [{', '.join(projects)}]")
    lines.append(f"{pre}writeable   : {writeable }")
    lines.append("")
    lines.append("Projects list")
    for name in (*projects, *[p for p in allprojects if p not in projects]):
        project = allprojects[name]
        url = project["url"]
        destdir = pathresolver(project.get("destdir", ""))
        tag = "."
        lines.append(f"{pre}{tag} {name}")
        if mode == "prod":
            if ref := project.get("prod"):
                lines.append(f"{pre}  pip install from {url}")
                lines.append(f"{pre}  (ref. {ref})")
            else:
                lines.append(f"{pre}  will skip install")
        elif mode == "dev":
            if destdir := project.get("destdir"):
                destdir = projectsdir / destdir.format(
                    **{"projectsdir": projectsdir, **project}
                )
                pypath = destdir / project.get("pypath", "")
                lines.append(f"{pre}  pypath  {pypath}")
            else:
                lines.append(f"{pre}  will skip install")
        elif mode == "dev-install":
            if destdir := project.get("destdir"):
                destdir = projectsdir / destdir.format(
                    **{"projectsdir": projectsdir, **project}
                )
                pypath = destdir / project.get("pypath", "")
                lines.append(f"{pre}  checkout  {url}")
                lines.append(f"{pre}  destdir   {destdir}")
                lines.append(f"{pre}  pypath    {pypath}")
            else:
                lines.append(f"{pre}  will skip install")
    print("\n".join(lines))
    return lines


@task("install package package from {url} (ref. {ref})")
def pip_install(url, token="", ref="", test=False):
    o = urlfixer(url, token, ref)
    scheme = o.scheme
    if not scheme.startswith("git+"):
        o = o._replace(scheme=f"git+{o.scheme}")
    cmd = ["pip", "install", "--quiet", "--force-reinstall", o.geturl()]
    if test:
        print(" ".join(str(c) for c in cmd))
        return
    run = subprocess.check_output([str(c) for c in cmd], encoding="utf-8")
    print(f"pip installed {url}")
    if run.strip():
        print(run)


@task("checkout source code in '{destdir}'")
def git_clone(destdir, url, token="", branch="", dryrun=False):
    destdir = Path(destdir).absolute()
    if destdir.exists():
        printwarn(
            f"""\
found {destdir}
not checking out sxope-bigq
(did you mean to use the mode='dev'?)
""",
            multiline=True,
        )
        return

    o = urlfixer(url, token)

    cmd = [
        "git",
        "clone",
        o.geturl(),
        destdir,
    ]
    if branch:
        cmd.insert(2, "--branch")
        cmd.insert(3, branch)
    if dryrun:
        print(" ".join(str(c) for c in cmd))
        return
    run = subprocess.check_output([str(c) for c in cmd], encoding="utf-8")
    print(f"git cloned in {destdir}")
    if run.strip():
        print(run)


@task("updating PYTHONPATH")
def add_pypath(path, dryrun=False):
    print(f"adding {path}")
    if not dryrun:
        sys.path.insert(0, str(path))


@task("mounting gdrive under '{mountpoint}' (readonly? {readonly})")
def mount(mountpoint: Path, readonly: bool = True) -> Path | None:
    from google.colab import drive

    if not mountpoint:
        print("not mounting GDrive")
        return None

    with mock.patch("sys.stdout", new_callable=io.StringIO):
        drive.mount(str(mountpoint), force_remount=True, readonly=readonly)
    print(f"drive mounted under {mountpoint}")
    return Path(mountpoint)


if __name__ == "__main__":
    import getpass

    token = getpass.getpass("Github token? ")
    git_clone(
        "x",
        "https://github.com/antonio-cavallo/sxope-bigq.git",
        token=token,
        test=False,
    )
